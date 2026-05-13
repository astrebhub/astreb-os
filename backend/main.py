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
      <div class="lens"><strong>Orientation lens:</strong> {escape(article.get("orientation_lens", ""))}</div>
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
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>JAZEKKER - Public Intelligence Hub</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #122026;
      --muted: #5a6872;
      --line: #d9e0e4;
      --paper: #f7f8f7;
      --panel: #ffffff;
      --green: #23483f;
      --blue: #23506f;
      --red: #8a3d36;
      --gold: #9b7a2f;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--paper); color: var(--ink); }
    a { color: inherit; }
    .topbar {
      position: sticky; top: 0; z-index: 10;
      display: flex; align-items: center; justify-content: space-between;
      padding: 14px 28px; background: rgba(247,248,247,.92);
      border-bottom: 1px solid var(--line); backdrop-filter: blur(12px);
    }
    .brand { font-weight: 760; font-size: 20px; letter-spacing: 0; }
    nav { display: flex; gap: 18px; color: var(--muted); font-size: 14px; }
    .hero {
      min-height: 82vh; display: grid; align-items: end;
      background:
        linear-gradient(180deg, rgba(18,32,38,.08), rgba(18,32,38,.72)),
        url("/jazekker/assets/jazekker-homepage-ecosystem-concept.png") center/cover no-repeat;
      color: white;
    }
    .hero-inner { width: min(1120px, calc(100% - 40px)); margin: 0 auto; padding: 0 0 54px; }
    h1 { max-width: 780px; margin: 0; font-size: clamp(42px, 7vw, 82px); line-height: .96; letter-spacing: 0; }
    .hero p { max-width: 670px; margin: 22px 0 0; font-size: 20px; line-height: 1.45; color: rgba(255,255,255,.86); }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 26px; }
    .button {
      border: 1px solid rgba(255,255,255,.55); color: white; text-decoration: none;
      min-height: 42px; display: inline-flex; align-items: center; padding: 0 14px; border-radius: 6px;
      background: rgba(255,255,255,.12);
    }
    .button.primary { background: white; color: var(--ink); border-color: white; }
    main { width: min(1120px, calc(100% - 40px)); margin: 0 auto; }
    section { padding: 42px 0; border-bottom: 1px solid var(--line); }
    .section-head { display: flex; justify-content: space-between; gap: 24px; align-items: end; margin-bottom: 18px; }
    h2 { margin: 0; font-size: 30px; letter-spacing: 0; }
    .section-head p { max-width: 520px; margin: 0; color: var(--muted); line-height: 1.5; }
    .orientation-grid { display: grid; grid-template-columns: 1.1fr .9fr; gap: 16px; }
    .daily {
      background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 20px;
      display: grid; gap: 18px;
    }
    .daily h3, .signal h3, .object h3, .trust h3 { margin: 0; font-size: 18px; line-height: 1.3; letter-spacing: 0; }
    .daily p, .signal p, .object p, .trust p { margin: 8px 0 0; color: var(--muted); line-height: 1.5; }
    .signal-map { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
    .signal { background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--blue); border-radius: 8px; padding: 16px; min-height: 142px; }
    .signal:nth-child(2) { border-left-color: var(--green); }
    .signal:nth-child(3) { border-left-color: var(--gold); }
    .signal:nth-child(4) { border-left-color: var(--red); }
    .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
    .chip { font-size: 12px; padding: 4px 8px; border-radius: 999px; background: #edf1f2; color: #344750; }
    .objects { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
    .object { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 18px; min-height: 260px; display: flex; flex-direction: column; }
    .object .next { margin-top: auto; padding-top: 14px; font-size: 13px; color: var(--green); }
    .trust-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .trust { background: #eef2f1; border: 1px solid #d6dfdc; border-radius: 8px; padding: 16px; }
    .cabinet {
      display: grid; grid-template-columns: .9fr 1.1fr; gap: 18px; align-items: center;
      background: #172026; color: white; border-radius: 8px; padding: 18px;
    }
    .cabinet img { width: 100%; border-radius: 6px; display: block; }
    .cabinet p { color: rgba(255,255,255,.76); }
    .pipeline { display: grid; gap: 8px; margin-top: 16px; }
    .step { padding: 9px 10px; border-radius: 6px; background: rgba(255,255,255,.1); color: rgba(255,255,255,.9); font-size: 14px; }
    footer { padding: 26px 0 42px; color: var(--muted); display: flex; justify-content: space-between; gap: 18px; }
    @media (max-width: 860px) {
      nav { display: none; }
      .orientation-grid, .cabinet { grid-template-columns: 1fr; }
      .objects, .trust-row, .signal-map { grid-template-columns: 1fr; }
      .section-head { display: block; }
      .section-head p { margin-top: 8px; }
    }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">JAZEKKER</div>
    <nav>
      <a href="#orientation">Daily Orientation</a>
      <a href="#signals">Signals</a>
      <a href="#trust">Trust</a>
      <a href="/jazekker/news">News Signals</a>
      <a href="/">AI Cabinet</a>
    </nav>
  </header>
  <section class="hero">
    <div class="hero-inner">
      <h1>Public intelligence for calm orientation.</h1>
      <p>JAZEKKER transforms noise into signals, signals into context, and context into orientation for people and organizations navigating AI, society, governance, and future systems.</p>
      <div class="actions">
        <a class="button primary" href="/jazekker/news">Open News Signals</a>
        <a class="button" href="/">Open AI Cabinet</a>
      </div>
    </div>
  </section>
  <main>
    <section id="orientation">
      <div class="section-head">
        <h2>Daily Orientation</h2>
        <p>A concise map of what matters now, why it matters, what is uncertain, and what the next orientation step should be.</p>
      </div>
      <div class="orientation-grid">
        <article class="daily">
          <div>
            <h3>Today’s governing signal</h3>
            <p>AI governance is moving from principles into operational infrastructure: approvals, audit trails, local routing, and source transparency.</p>
            <div class="chips"><span class="chip">medium risk</span><span class="chip">weeks</span><span class="chip">source review</span></div>
          </div>
          <div>
            <h3>Noise versus significance</h3>
            <p>The noise is product hype. The signal is that organizations need controlled AI execution before agentic workflows become operationally trusted.</p>
          </div>
        </article>
        <div class="signal-map" id="signals">
          <article class="signal"><h3>AI Governance</h3><p>Runtime controls, approvals, and accountability become product requirements.</p></article>
          <article class="signal"><h3>Local-first AI</h3><p>Sensitive workflows route locally while public tasks may use controlled cloud paths.</p></article>
          <article class="signal"><h3>Agentic Media</h3><p>Publishing becomes governed interpretation, not direct automation.</p></article>
          <article class="signal"><h3>Civic Intelligence</h3><p>Public understanding depends on source confidence and calm synthesis.</p></article>
        </div>
      </div>
    </section>
    <section>
      <div class="section-head">
        <h2>Orientation Objects</h2>
        <p>The core object is not an article. It is a structured unit of signal, context, uncertainty, impact, and next step.</p>
      </div>
      <div class="objects">
        <article class="object">
          <div class="chips"><span class="chip">draft</span><span class="chip">official source</span></div>
          <h3>How enterprises are scaling AI</h3>
          <p>Collected from an approved source. Needs interpretation and governance review before becoming public analysis.</p>
          <div class="next">Next: verify source, separate fact from interpretation, decide if full orientation is needed.</div>
        </article>
        <article class="object">
          <div class="chips"><span class="chip">draft</span><span class="chip">reputational</span></div>
          <h3>OpenAI legal and governance battle</h3>
          <p>A sensitive public signal where source confidence, legal framing, and uncertainty must be explicit.</p>
          <div class="next">Next: governance review before any headline or public framing.</div>
        </article>
        <article class="object">
          <div class="chips"><span class="chip">draft</span><span class="chip">workplace AI</span></div>
          <h3>AI automates HR compliance</h3>
          <p>A practical infrastructure signal about compliance automation, limits, and organizational risk.</p>
          <div class="next">Next: add primary sources and identify affected organizations.</div>
        </article>
      </div>
    </section>
    <section id="trust">
      <div class="section-head">
        <h2>Trust Architecture</h2>
        <p>JAZEKKER is built around confidence, approval status, source visibility, and AI disclosure.</p>
      </div>
      <div class="trust-row">
        <article class="trust"><h3>Sources</h3><p>Every signal carries source URL, publisher, type, and last checked date.</p></article>
        <article class="trust"><h3>Confidence</h3><p>Signals are marked low, medium, or high confidence before editorial use.</p></article>
        <article class="trust"><h3>Approval</h3><p>Draft, reviewed, approved, scheduled, and published states remain separate.</p></article>
        <article class="trust"><h3>AI Disclosure</h3><p>AI-assisted work remains auditable and cannot publish directly.</p></article>
      </div>
    </section>
    <section>
      <div class="cabinet">
        <img src="/jazekker/assets/ai-cabinet-concept.png" alt="AI Cabinet concept visualization" />
        <div>
          <h2>AI Cabinet is the governed runtime.</h2>
          <p>JAZEKKER is the public intelligence surface. AI Cabinet classifies, applies policy, routes models, tracks evidence, records audit events, and keeps publication behind human approval.</p>
          <div class="pipeline">
            <div class="step">signal intake -> source tracking</div>
            <div class="step">classification -> policy -> interpretation</div>
            <div class="step">orientation object -> human approval</div>
            <div class="step">distribution draft -> publish queue proposal</div>
          </div>
        </div>
      </div>
    </section>
    <footer>
      <span>Noise -> Signals -> Context -> Orientation -> Trust -> Coordination -> Clarity</span>
      <span>Draft preview. No publication action performed.</span>
    </footer>
  </main>
</body>
</html>
    """


@app.get("/jazekker/news")
async def jazekker_news_page():
    return FileResponse(FRONTEND_DIR / "jazekker-news.html", media_type="text/html")
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>JAZEKKER News Signals</title>
  <style>
    :root { color-scheme: light; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    body { margin: 0; background: #f6f7f8; color: #172026; }
    main { max-width: 1120px; margin: 0 auto; padding: 32px 20px 56px; }
    header { display: flex; gap: 16px; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
    h1 { margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }
    p { margin: 0; color: #52616b; line-height: 1.5; }
    .controls { display: grid; grid-template-columns: 1fr 1fr auto auto; gap: 10px; margin: 20px 0 24px; }
    input { height: 40px; border: 1px solid #cbd3d9; border-radius: 6px; padding: 0 12px; font: inherit; background: white; }
    button, a.button { height: 42px; border: 0; border-radius: 6px; padding: 0 14px; background: #172026; color: white; font: inherit; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; }
    a.button.secondary, button.secondary { background: #e4e8eb; color: #172026; }
    .status { margin: 0 0 16px; font-size: 14px; color: #52616b; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; }
    article { background: white; border: 1px solid #dfe5e9; border-radius: 8px; padding: 16px; min-height: 220px; display: flex; flex-direction: column; gap: 12px; }
    article h2 { margin: 0; font-size: 18px; line-height: 1.3; letter-spacing: 0; }
    .meta { display: flex; flex-wrap: wrap; gap: 6px; }
    .chip { font-size: 12px; background: #eef2f4; color: #35454f; border-radius: 999px; padding: 4px 8px; }
    .summary { color: #35454f; font-size: 14px; }
    .source { margin-top: auto; font-size: 13px; }
    .source a { color: #0b5cad; overflow-wrap: anywhere; }
    pre { white-space: pre-wrap; background: #111820; color: #e8edf1; border-radius: 8px; padding: 12px; overflow: auto; }
    @media (max-width: 760px) { header, .controls { grid-template-columns: 1fr; display: grid; } }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>JAZEKKER News Signals</h1>
        <p>Draft-only RSS collector. It gathers signals, but does not publish, schedule, distribute, or update strategic memory.</p>
      </div>
      <a class="button secondary" href="/">AI Cabinet</a>
    </header>
    <section class="controls">
      <input id="token" placeholder="Admin token" />
      <input id="topic" value="AI governance" placeholder="Topic" />
      <button id="collect">Collect News</button>
      <button id="refresh" class="secondary">Refresh Saved</button>
    </section>
    <p id="status" class="status">Ready.</p>
    <section id="cards" class="grid"></section>
    <pre id="raw" hidden></pre>
  </main>
  <script>
    const token = document.getElementById("token");
    const topic = document.getElementById("topic");
    const cards = document.getElementById("cards");
    const status = document.getElementById("status");
    const raw = document.getElementById("raw");

    token.value = localStorage.getItem("AI_CABINET_ADMIN_TOKEN") || "";
    token.addEventListener("input", () => localStorage.setItem("AI_CABINET_ADMIN_TOKEN", token.value));

    function headers() {
      return {"Content-Type": "application/json", "X-AI-Cabinet-Admin-Token": token.value};
    }

    function sourceOf(item) {
      const record = item.record?.record || item.record || item;
      return record.sources?.[0] || {publisher: item.source, url: item.url, confidence: ""};
    }

    function render(items) {
      cards.innerHTML = "";
      items.forEach((item) => {
        const record = item.record?.record || item.record || item;
        const source = sourceOf(item);
        const article = document.createElement("article");
        article.innerHTML = `
          <div class="meta">
            <span class="chip">${record.status || item.status || "draft"}</span>
            <span class="chip">${record.noise_level || "medium"} noise</span>
            <span class="chip">${record.impact_horizon || "weeks"}</span>
            <span class="chip">${source.confidence || "medium"} confidence</span>
          </div>
          <h2>${escapeHtml(record.title || item.title)}</h2>
          <p class="summary">${escapeHtml(record.signal?.summary || "")}</p>
          <p class="summary"><strong>Next:</strong> ${escapeHtml(record.next_orientation_step || "")}</p>
          <p class="source">${escapeHtml(source.publisher || item.source || "")}<br><a href="${escapeAttr(source.url || item.url)}" target="_blank" rel="noreferrer">${escapeHtml(source.url || item.url || "")}</a></p>
        `;
        cards.appendChild(article);
      });
    }

    function escapeHtml(value) {
      return String(value || "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
    }
    function escapeAttr(value) { return escapeHtml(value).replaceAll("`", "&#96;"); }

    async function collect() {
      status.textContent = "Collecting RSS signals...";
      const res = await fetch("/jazekker/news/collect", {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({topic: topic.value || "AI governance", limit_per_source: 5, max_total: 12})
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || JSON.stringify(data));
      raw.textContent = JSON.stringify(data, null, 2);
      render(data.orientation_object_drafts || []);
      status.textContent = `Collected ${data.collected}, returned ${data.returned}. Publication: none.`;
    }

    async function refreshSaved() {
      status.textContent = "Loading saved draft signals...";
      const res = await fetch("/jazekker/news/signals", {headers: headers()});
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || JSON.stringify(data));
      const rows = data.value || data;
      raw.textContent = JSON.stringify(rows, null, 2);
      render(rows);
      status.textContent = `Loaded ${rows.length} saved draft signals.`;
    }

    document.getElementById("collect").addEventListener("click", () => collect().catch((err) => status.textContent = `Error: ${err.message}`));
    document.getElementById("refresh").addEventListener("click", () => refreshSaved().catch((err) => status.textContent = `Error: ${err.message}`));
    refreshSaved().catch(() => {});
  </script>
</body>
</html>
    """


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
