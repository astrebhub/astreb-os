import json
from html import escape
from pathlib import Path
from typing import Any, Dict

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cabinet.actions import ActionQueue
from cabinet.agent_registry import AgentRegistry
from cabinet.approval_center import ApprovalCenter
from cabinet.budget_governor import BudgetGovernor
from cabinet.classifier import DataClassifier
from cabinet.config import ADMIN_API_TOKEN, APP_NAME, FRONTEND_DIR, load_yaml
from cabinet.connector_registry import ConnectorRegistry
from cabinet.control_center import PROCESS_MAP, panel_audit
from cabinet.database import Database
from cabinet.evidence import EvidenceLayer
from cabinet.forecasting import ForecastCreateRequest, ForecastOutcomeRequest, ForecastingEngine
from cabinet.guide_agent import CabinetGuideAgent
from cabinet.identity import IdentityAccessLayer
from cabinet.local_runtime import LocalRuntimeManager
from cabinet.memory_engine import MemoryEngine
from cabinet.multimodal import MultimodalNormalizer
from cabinet.news_collector import JazekkerNewsCollector, NewsCollectRequest
from cabinet.observability import ObservabilityLayer
from cabinet.orientation_workflow import ORIENTATION_STATUSES, OrientationWorkflow
from cabinet.output_guard import OutputGuard
from cabinet.pii import PiiDetector
from cabinet.pipeline import CabinetPipeline
from cabinet.policy import PolicyEngine
from cabinet.providers import ProviderAdapter
from cabinet.router import ModelRouter
from cabinet.secrets_vault import SecretsVault
from cabinet.schemas import SubmitRequest, SubmitResponse
from cabinet.state_engine import StateEngine
from cabinet.tokens import TokenCostEstimator
from cabinet.plugin_sandbox import PluginSandbox
from cabinet.vector_memory import LocalEmbeddingEngine, VectorMemory


class VectorAddRequest(BaseModel):
    namespace: str = "project"
    content: str


class VectorSearchRequest(BaseModel):
    namespace: str = "project"
    query: str
    limit: int = 5


class SecretPutRequest(BaseModel):
    name: str
    value: str
    provider: str = ""


class AgentRegisterRequest(BaseModel):
    id: str
    role: str = "agent"
    instructions: str = ""
    permissions: list[str] = []
    budget: Dict[str, Any] = {}
    tools: list[str] = []
    memory_scope: str = "operational"
    risk_level: str = "low"
    status: str = "active"


class GuideChatRequest(BaseModel):
    message: str = ""
    ui_state: Dict[str, Any] = {}


class JazekkerNewsCollectRequest(BaseModel):
    topic: str = "auto"
    channel: str = "auto"
    limit_per_source: int = 5
    max_total: int = 12


class EditorialActionRequest(BaseModel):
    action: str
    reviewer: str = "owner"
    notes: str = ""
    publication_target: str | None = None
    patch: Dict[str, Any] = {}

app = FastAPI(title=APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

database = Database()
database.init()

pii_detector = PiiDetector()
action_queue = ActionQueue(database)
memory_engine = MemoryEngine(database)
local_runtime = LocalRuntimeManager()
PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins"
plugin_sandbox = PluginSandbox(PLUGIN_ROOT)
connector_registry = ConnectorRegistry(PLUGIN_ROOT)
vector_memory = VectorMemory(database, LocalEmbeddingEngine())
state_engine = StateEngine(database)
identity_layer = IdentityAccessLayer(database)
secrets_vault = SecretsVault(database)
agent_registry = AgentRegistry(database)
agent_registry.ensure_defaults()
approval_center = ApprovalCenter(database)
evidence_layer = EvidenceLayer(database)
observability_layer = ObservabilityLayer(database)
forecasting_engine = ForecastingEngine(database)
guide_agent = CabinetGuideAgent()
news_collector = JazekkerNewsCollector(load_yaml("news_sources.yaml").get("sources", []))
orientation_workflow = OrientationWorkflow(database)
pipeline = CabinetPipeline(
    database=database,
    state=state_engine,
    normalizer=MultimodalNormalizer(),
    identity=identity_layer,
    pii=pii_detector,
    classifier=DataClassifier(),
    policy=PolicyEngine(load_yaml("policy.yaml")),
    estimator=TokenCostEstimator(database),
    budget=BudgetGovernor(database),
    router=ModelRouter(load_yaml("model_routing.yaml")),
    provider=ProviderAdapter(secrets_vault),
    plugin_sandbox=plugin_sandbox,
    output_guard=OutputGuard(pii_detector),
    actions=action_queue,
    approvals=approval_center,
    evidence=evidence_layer,
    observability=observability_layer,
    memory_engine=memory_engine,
)


def read_plugin_manifests() -> list[Dict[str, Any]]:
    return plugin_sandbox.manifests()


def require_admin_token(x_ai_cabinet_admin_token: str | None = Header(default=None)) -> None:
    if not ADMIN_API_TOKEN:
        raise HTTPException(status_code=503, detail="admin_api_token_not_configured")
    if x_ai_cabinet_admin_token != ADMIN_API_TOKEN:
        raise HTTPException(status_code=403, detail="admin_token_required")


def load_jazekker_articles() -> list[Dict[str, Any]]:
    articles_dir = Path(__file__).resolve().parents[1] / "content" / "articles"
    articles: list[Dict[str, Any]] = []
    for path in sorted(articles_dir.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, list):
            articles.extend(item for item in data if isinstance(item, dict))
        elif isinstance(data, dict):
            articles.append(data)
    return sorted(articles, key=lambda item: item.get("published_at", ""), reverse=True)


def article_url(article: Dict[str, Any]) -> str:
    return f"/jazekker/articles/{article.get('slug', article.get('id', 'article'))}"


def render_jazekker_article(article: Dict[str, Any]) -> str:
    paragraphs = "\n".join(f"<p>{escape(str(paragraph))}</p>" for paragraph in article.get("body", []))
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(article.get("title", "JAZEKKER Article"))}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #071019;
      --panel: #0d1a25;
      --line: #203345;
      --text: #edf4f7;
      --muted: #9badba;
      --gold: #e2b354;
      --green: #6fd2a5;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: radial-gradient(circle at 75% 0%, #11243a 0, var(--bg) 38%); color: var(--text); }}
    .shell {{ width: min(920px, calc(100% - 36px)); margin: 0 auto; padding: 24px 0 64px; }}
    header {{ display: flex; justify-content: space-between; gap: 18px; align-items: center; padding-bottom: 22px; border-bottom: 1px solid var(--line); }}
    a {{ color: inherit; }}
    .back {{ min-height: 38px; border: 1px solid var(--line); border-radius: 6px; padding: 0 12px; display: inline-flex; align-items: center; text-decoration: none; background: #12283a; }}
    .brand {{ color: var(--gold); letter-spacing: 0; font-weight: 700; }}
    article {{ margin-top: 42px; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }}
    .chip {{ display: inline-flex; align-items: center; min-height: 24px; padding: 3px 8px; border-radius: 6px; background: #13283a; color: #c5d1db; font-size: 12px; }}
    .chip.local {{ background: #173628; color: #aee7c7; }}
    h1 {{ margin: 0; max-width: 820px; font-size: 44px; line-height: 1.05; letter-spacing: 0; }}
    .dek {{ margin-top: 18px; max-width: 760px; color: #c7d4df; font-size: 20px; line-height: 1.5; }}
    .lens {{ margin: 28px 0; padding: 16px; border: 1px solid #385339; border-radius: 8px; background: rgba(17, 38, 31, .88); color: #dceadf; }}
    .body {{ margin-top: 26px; max-width: 760px; }}
    p {{ color: #d7e1e8; font-size: 18px; line-height: 1.72; }}
    .next {{ margin-top: 34px; padding-top: 18px; border-top: 1px solid var(--line); color: var(--gold); }}
    @media (max-width: 760px) {{ h1 {{ font-size: 34px; }} .dek, p {{ font-size: 17px; }} }}
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div class="brand">JAZEKKER</div>
      <a class="back" href="/jazekker/news">Назад к ленте</a>
    </header>
    <article>
      <div class="meta">
        <span class="chip local">{escape(article.get("status", "published_local"))}</span>
        <span class="chip">{escape(article.get("category_label", ""))}</span>
        <span class="chip">{escape(str(article.get("reading_minutes", 4)))} min</span>
        <span class="chip">{escape(article.get("published_at", ""))}</span>
      </div>
      <h1>{escape(article.get("title", ""))}</h1>
      <div class="dek">{escape(article.get("dek", ""))}</div>
      <div class="lens"><strong>Фокус материала:</strong> {escape(article.get("orientation_lens", ""))}</div>
      <div class="body">{paragraphs}</div>
      <div class="next"><strong>Следующий шаг:</strong> {escape(article.get("next_orientation_step", ""))}</div>
    </article>
  </div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    with (FRONTEND_DIR / "index.html").open("r", encoding="utf-8") as handle:
        return handle.read()


@app.get("/styles.css")
async def styles():
    return FileResponse(FRONTEND_DIR / "styles.css", media_type="text/css")


@app.get("/app.js")
async def frontend_app():
    return FileResponse(FRONTEND_DIR / "app.js", media_type="application/javascript")


@app.get("/jazekker/assets/{asset_name}")
async def jazekker_asset(asset_name: str):
    assets_dir = Path(__file__).resolve().parents[1] / "docs" / "strategy" / "jazekker" / "assets"
    asset_path = assets_dir / asset_name
    if not asset_path.exists() or asset_path.parent != assets_dir:
        raise HTTPException(status_code=404, detail="asset_not_found")
    return FileResponse(asset_path)


@app.get("/jazekker")
async def jazekker_homepage_preview():
    return FileResponse(FRONTEND_DIR / "jazekker.html", media_type="text/html")


@app.get("/jazekker/news")
async def jazekker_news_page():
    return FileResponse(FRONTEND_DIR / "jazekker-news.html", media_type="text/html")


@app.get("/jazekker/editorial")
async def jazekker_editorial_page():
    return FileResponse(FRONTEND_DIR / "jazekker-editorial.html", media_type="text/html")


@app.get("/jazekker/chief-editor")
async def jazekker_chief_editor_page():
    return FileResponse(FRONTEND_DIR / "jazekker-chief-editor.html", media_type="text/html")


@app.post("/submit", response_model=SubmitResponse)
async def submit(req: SubmitRequest):
    return await pipeline.run(req)


@app.get("/audit", dependencies=[Depends(require_admin_token)])
async def audit(limit: int = 50):
    return list(database.list_rows("audit_log", limit))


@app.get("/memory", dependencies=[Depends(require_admin_token)])
async def memory(limit: int = 50):
    return list(database.list_rows("memory", limit))


@app.get("/actions", dependencies=[Depends(require_admin_token)])
async def actions(limit: int = 50):
    rows = list(database.list_rows("action_queue", limit))
    for row in rows:
        row["payload"] = json.loads(row["payload"]) if row.get("payload") else {}
    return rows


@app.get("/memory/layers", dependencies=[Depends(require_admin_token)])
async def memory_layers(limit: int = 50):
    return {
        "layers": [
            "constitution",
            "role_instruction",
            "policy",
            "project",
            "operational",
            "learning",
            "audit",
        ],
        "records": list(database.list_rows("governed_memory", limit)),
        "proposals": list(database.list_rows("memory_proposals", limit)),
    }


@app.get("/state/{request_id}", dependencies=[Depends(require_admin_token)])
async def runtime_state(request_id: str, limit: int = 100):
    rows = list(database.list_rows("runtime_state", limit))
    return [row for row in rows if row.get("request_id") == request_id]


@app.post("/memory/proposals/{proposal_id}/approve", dependencies=[Depends(require_admin_token)])
async def approve_memory_proposal(proposal_id: str):
    result = memory_engine.approve_proposal(proposal_id)
    if not result:
        raise HTTPException(status_code=404, detail="Memory proposal not found")
    return result


@app.post("/memory/proposals/{proposal_id}/reject", dependencies=[Depends(require_admin_token)])
async def reject_memory_proposal(proposal_id: str):
    result = memory_engine.reject_proposal(proposal_id)
    if not result:
        raise HTTPException(status_code=404, detail="Memory proposal not found")
    return result


@app.post("/actions/{action_id}/approve", dependencies=[Depends(require_admin_token)])
async def approve_action(action_id: str):
    result = action_queue.approve(action_id)
    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@app.post("/actions/{action_id}/reject", dependencies=[Depends(require_admin_token)])
async def reject_action(action_id: str):
    result = action_queue.reject(action_id)
    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@app.post("/actions/{action_id}/execute", dependencies=[Depends(require_admin_token)])
async def execute_action(action_id: str):
    result = action_queue.execute_noop(action_id)
    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@app.post("/actions/{action_id}/rollback", dependencies=[Depends(require_admin_token)])
async def rollback_action(action_id: str):
    result = action_queue.rollback(action_id)
    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@app.post("/actions/{action_id}/expire", dependencies=[Depends(require_admin_token)])
async def expire_action(action_id: str):
    result = action_queue.expire(action_id)
    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@app.get("/plugins")
async def plugins():
    return read_plugin_manifests()


@app.get("/connectors/status")
async def connectors_status():
    return connector_registry.capabilities()


@app.get("/connectors/{connector_name}")
async def connector_detail(connector_name: str):
    connector = connector_registry.get(connector_name)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector


@app.post("/connectors/{connector_name}/dry-run", dependencies=[Depends(require_admin_token)])
async def connector_dry_run(connector_name: str, action: str, data_class: str = "public", access_level: int = 2):
    return connector_registry.dry_run(connector_name, action, data_class, access_level)


@app.get("/approvals", dependencies=[Depends(require_admin_token)])
async def approvals(limit: int = 50):
    return list(database.list_rows("approvals", limit))


@app.get("/budget/status", dependencies=[Depends(require_admin_token)])
async def budget_status(limit: int = 50):
    return list(database.list_rows("budget_events", limit))


@app.get("/access/users", dependencies=[Depends(require_admin_token)])
async def users(limit: int = 50):
    return list(database.list_rows("users", limit))


@app.post("/access/users/{user_id}/ensure", dependencies=[Depends(require_admin_token)])
async def ensure_user(user_id: str, access_level: int = 1):
    return identity_layer.ensure_user(user_id, access_level)


@app.post("/secrets", dependencies=[Depends(require_admin_token)])
async def put_secret(req: SecretPutRequest):
    secret_id = secrets_vault.put(req.name, req.value, req.provider)
    return {"id": secret_id, "name": req.name, "stored": True}


@app.get("/secrets/{name}/metadata", dependencies=[Depends(require_admin_token)])
async def secret_metadata(name: str):
    return secrets_vault.metadata(name)


@app.get("/agents", dependencies=[Depends(require_admin_token)])
async def agents(limit: int = 50):
    return list(database.list_rows("agent_registry", limit))


@app.get("/runtime/personalization")
async def runtime_personalization():
    return {
        "profiles": load_yaml("user_profiles.yaml").get("profiles", {}),
        "dialog_modes": load_yaml("dialog_modes.yaml").get("modes", {}),
        "agents": list(database.list_rows("agent_registry", 100)),
    }


@app.post("/guide/chat")
async def guide_chat(req: GuideChatRequest):
    import os

    runtime = connector_registry.capabilities()
    runtime.update(
        {
            "app": APP_NAME,
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
            "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
            "local_only_mode": os.getenv("LOCAL_ONLY_MODE", "false").lower() == "true",
        }
    )
    reply = guide_agent.reply(req.message, req.ui_state, runtime)
    return {
        "agent_id": "cabinet_guide_agent",
        "answer": reply.answer,
        "suggestions": reply.suggestions,
        "recommended_panel": reply.recommended_panel,
        "governance": {
            "execution": "advisory_only",
            "external_actions": "none",
            "policy": "control_before_autonomy",
        },
    }


@app.post("/agents", dependencies=[Depends(require_admin_token)])
async def register_agent(req: AgentRegisterRequest):
    return {"id": agent_registry.register(req.model_dump()), "status": "registered"}


@app.get("/evidence", dependencies=[Depends(require_admin_token)])
async def evidence(limit: int = 50):
    return list(database.list_rows("evidence_sources", limit))


@app.get("/jazekker/news/sources", dependencies=[Depends(require_admin_token)])
async def jazekker_news_sources():
    return {
        "status": "configured",
        "sources": load_yaml("news_sources.yaml").get("sources", []),
        "topics": news_collector.topics(),
        "governance": {
            "mode": "draft_only",
            "publication": "none",
            "approval_required_before_publication": True,
        },
    }


@app.get("/jazekker/news/signals", dependencies=[Depends(require_admin_token)])
async def jazekker_news_signals(limit: int = 50):
    rows = list(database.list_rows("jazekker_news_signals", limit))
    for row in rows:
        row["record"] = json.loads(row["record"]) if row.get("record") else {}
    return rows


@app.get("/jazekker/articles")
async def jazekker_articles():
    articles = []
    for article in load_jazekker_articles():
        item = dict(article)
        item["url"] = article_url(item)
        articles.append(item)
    return {
        "status": "published_local",
        "count": len(articles),
        "articles": articles,
        "governance": {
            "publication_scope": "local",
            "external_distribution": "none",
            "source": "content/articles",
        },
    }


@app.get("/jazekker/articles/{slug}", response_class=HTMLResponse)
async def jazekker_article_page(slug: str):
    for article in load_jazekker_articles():
        if article.get("slug") == slug or article.get("id") == slug:
            return render_jazekker_article(article)
    raise HTTPException(status_code=404, detail="article_not_found")


@app.get("/jazekker/orientation-objects", dependencies=[Depends(require_admin_token)])
async def jazekker_orientation_objects(limit: int = 100, status: str = "", rubric: str = ""):
    rows = list(database.list_orientation_objects(limit, status, rubric))
    return {
        "status": "ok",
        "workflow_statuses": ORIENTATION_STATUSES,
        "count": len(rows),
        "objects": [row["record"] for row in rows],
    }


@app.get("/jazekker/orientation-objects/{object_id}", dependencies=[Depends(require_admin_token)])
async def jazekker_orientation_object(object_id: str):
    row = database.get_orientation_object(object_id)
    if not row:
        raise HTTPException(status_code=404, detail="orientation_object_not_found")
    return {
        "object": row["record"],
        "audit": list(database.list_editorial_audit(object_id, 100)),
    }


@app.get("/jazekker/editorial/audit", dependencies=[Depends(require_admin_token)])
async def jazekker_editorial_audit(object_id: str = "", limit: int = 100):
    return list(database.list_editorial_audit(object_id, limit))


@app.post("/jazekker/orientation-objects/ingest-local", dependencies=[Depends(require_admin_token)])
async def jazekker_ingest_local_articles():
    return orientation_workflow.seed_from_articles(load_jazekker_articles())


@app.post("/jazekker/orientation-objects/ingest-news", dependencies=[Depends(require_admin_token)])
async def jazekker_ingest_news_signals(limit: int = 100):
    rows = list(database.list_rows("jazekker_news_signals", limit))
    records = []
    for row in rows:
        draft = json.loads(row["record"]) if row.get("record") else {}
        if draft.get("record") and isinstance(draft["record"], dict):
            draft = draft["record"]
        records.append(orientation_workflow.from_rss_draft(draft, actor="news_signal_ingest"))
    return {"status": "ingested", "count": len(records), "records": records}


@app.post("/jazekker/orientation-objects/{object_id}/action", dependencies=[Depends(require_admin_token)])
async def jazekker_orientation_action(object_id: str, req: EditorialActionRequest):
    status_map = {
        "review": "review_required",
        "approve": "approved",
        "reject": "blocked",
        "block": "blocked",
        "escalate": "review_required",
        "schedule": "scheduled",
        "publish_local": "published_local",
        "publish_external": "published_external",
        "archive": "archived",
        "edit": None,
    }
    if req.action not in status_map:
        raise HTTPException(status_code=400, detail="unsupported_editorial_action")
    row = database.get_orientation_object(object_id)
    if not row:
        raise HTTPException(status_code=404, detail="orientation_object_not_found")
    try:
        if req.action == "edit":
            target_status = row["record"].get("status", "drafted")
            result = orientation_workflow.transition(
                object_id,
                target_status,
                actor=req.reviewer,
                notes=req.notes or "Editorial fields updated.",
                patch=req.patch,
                publication_target=req.publication_target,
            )
        else:
            result = orientation_workflow.transition(
                object_id,
                status_map[req.action],
                actor=req.reviewer,
                notes=req.notes,
                patch=req.patch,
                publication_target=req.publication_target,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "status": "updated",
        "object": result,
        "audit": list(database.list_editorial_audit(object_id, 20)),
    }


@app.post("/jazekker/news/collect", dependencies=[Depends(require_admin_token)])
async def jazekker_news_collect(req: JazekkerNewsCollectRequest):
    result = await news_collector.collect(
        NewsCollectRequest(
            topic=req.topic,
            channel=req.channel,
            limit_per_source=req.limit_per_source,
            max_total=req.max_total,
        )
    )
    for draft in result["orientation_object_drafts"]:
        source = draft["sources"][0]
        database.insert_news_signal(
            {
                "id": draft["id"],
                "topic": result["topic"],
                "title": draft["title"],
                "url": source["url"],
                "source": source["publisher"],
                "status": draft["status"],
                "record": draft,
            }
        )
        orientation_workflow.from_rss_draft(draft, actor="news_collector")
    observability_layer.event(
        "jazekker_news_collected",
        "",
        "info",
        {
            "topic": result["topic"],
            "collected": result["collected"],
            "returned": result["returned"],
            "errors": len(result["errors"]),
        },
    )
    return result


@app.post("/jazekker/news/collect-all", dependencies=[Depends(require_admin_token)])
async def jazekker_news_collect_all(limit_per_channel: int = 3):
    topics = [topic for topic in news_collector.topics() if topic.get("source_count", 0) > 0]
    combined: list[Dict[str, Any]] = []
    errors: list[Dict[str, str]] = []
    for topic in topics:
        result = await news_collector.collect(
            NewsCollectRequest(
                topic=topic["label"],
                channel=topic["id"],
                limit_per_source=2,
                max_total=limit_per_channel,
            )
        )
        errors.extend(result.get("errors", []))
        for draft in result["orientation_object_drafts"]:
            source = draft["sources"][0]
            database.insert_news_signal(
                {
                    "id": draft["id"],
                    "topic": draft.get("category_label", topic["label"]),
                    "title": draft["title"],
                    "url": source["url"],
                    "source": source["publisher"],
                    "status": draft["status"],
                    "record": draft,
                }
            )
            orientation_workflow.from_rss_draft(draft, actor="news_collector")
            combined.append(draft)
    return {
        "status": "draft_only",
        "mode": "auto_feed",
        "topics": topics,
        "returned": len(combined),
        "errors": errors,
        "governance": {
            "external_action": "rss_fetch_only",
            "publication": "none",
            "approval_required_before_publication": True,
            "memory_update": "none",
        },
        "orientation_object_drafts": combined,
    }


@app.get("/observability/events", dependencies=[Depends(require_admin_token)])
async def observability_events(limit: int = 50):
    return list(database.list_rows("observability_events", limit))


@app.post("/forecasts")
async def create_forecast(req: ForecastCreateRequest):
    return forecasting_engine.create_forecast(req)


@app.get("/forecasts", dependencies=[Depends(require_admin_token)])
async def forecasts(limit: int = 50):
    return forecasting_engine.list_forecasts(limit)


@app.post("/forecasts/{forecast_id}/outcome", dependencies=[Depends(require_admin_token)])
async def forecast_outcome(forecast_id: str, req: ForecastOutcomeRequest):
    result = forecasting_engine.resolve_forecast(forecast_id, req)
    if not result:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return result


@app.get("/forecasts/calibration-profile", dependencies=[Depends(require_admin_token)])
async def forecast_calibration_profile():
    return forecasting_engine.calibration_profile()


@app.get("/local-runtime/status")
async def local_runtime_status():
    return await local_runtime.status()


@app.post("/local-runtime/models/{model_name}/load", dependencies=[Depends(require_admin_token)])
async def load_local_model(model_name: str):
    return await local_runtime.load_model(model_name)


@app.post("/local-runtime/models/{model_name}/unload", dependencies=[Depends(require_admin_token)])
async def unload_local_model(model_name: str):
    return await local_runtime.unload_model(model_name)


@app.get("/voice/status")
async def voice_status():
    from cabinet.voice_runtime import VoiceRuntime

    return VoiceRuntime().status()


@app.get("/multimodal/status")
async def multimodal_status():
    return {
        "inputs": ["text", "voice", "image", "file", "browser_action", "email", "calendar", "plugin_action"],
        "normalizer": "enabled",
        "risk_classifier": "normalizer_modality_risk_plus_data_classifier",
        "governance": "all_modalities_enter_same pipeline",
    }


@app.get("/control-center/process-map")
async def control_center_process_map():
    return PROCESS_MAP


@app.get("/control-center/panel-audit")
async def control_center_panel_audit():
    return panel_audit()


@app.post("/vector-memory/add", dependencies=[Depends(require_admin_token)])
async def add_vector_memory(req: VectorAddRequest):
    return vector_memory.add(req.namespace, req.content)


@app.post("/vector-memory/search", dependencies=[Depends(require_admin_token)])
async def search_vector_memory(req: VectorSearchRequest):
    return vector_memory.search(req.namespace, req.query, req.limit)


@app.get("/config/policy", dependencies=[Depends(require_admin_token)])
async def policy_config():
    return load_yaml("policy.yaml")


@app.get("/config/model-routing", dependencies=[Depends(require_admin_token)])
async def model_routing_config():
    return load_yaml("model_routing.yaml")


@app.get("/config/dialog-modes", dependencies=[Depends(require_admin_token)])
async def dialog_modes_config():
    return load_yaml("dialog_modes.yaml")


@app.get("/config/user-profiles", dependencies=[Depends(require_admin_token)])
async def user_profiles_config():
    return load_yaml("user_profiles.yaml")


@app.get("/health")
async def health():
    import os

    return {
        "status": "ok",
        "app": APP_NAME,
        "pipeline": [
            "INPUT",
            "MULTIMODAL NORMALIZER",
            "STATE ENGINE",
            "PII DETECTOR",
            "DATA CLASSIFIER",
            "POLICY ENGINE",
            "TOKEN / COST GOVERNOR",
            "MODEL / VOICE / TOOL ROUTER",
            "LOCAL/CLOUD DECISION LAYER",
            "PLUGIN SANDBOX",
            "PROVIDER ADAPTER",
            "OUTPUT GUARD",
            "ACTION QUEUE",
            "APPROVAL CENTER",
            "AUDIT LOG",
            "MEMORY UPDATE PROPOSAL",
            "HUMAN APPROVAL IF REQUIRED",
        ],
        "states": state_engine.states(),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
        "free_models": {
            "local": "ollama_or_local_safe_fallback",
            "openrouter": os.getenv("OPENROUTER_MODEL", "openrouter/free"),
            "gemini": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        },
        "connectors": connector_registry.capabilities(),
        "local_only_mode": os.getenv("LOCAL_ONLY_MODE", "false").lower() == "true",
    }
