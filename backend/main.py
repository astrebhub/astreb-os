import json
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cabinet.actions import ActionQueue
from cabinet.agent_registry import AgentRegistry
from cabinet.approval_center import ApprovalCenter
from cabinet.budget_governor import BudgetGovernor
from cabinet.classifier import DataClassifier
from cabinet.config import APP_NAME, FRONTEND_DIR, load_yaml
from cabinet.database import Database
from cabinet.evidence import EvidenceLayer
from cabinet.forecasting import ForecastCreateRequest, ForecastOutcomeRequest, ForecastingEngine
from cabinet.identity import IdentityAccessLayer
from cabinet.local_runtime import LocalRuntimeManager
from cabinet.memory_engine import MemoryEngine
from cabinet.multimodal import MultimodalNormalizer
from cabinet.observability import ObservabilityLayer
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
plugin_sandbox = PluginSandbox(Path(__file__).resolve().parents[1] / "plugins")
vector_memory = VectorMemory(database, LocalEmbeddingEngine())
state_engine = StateEngine(database)
identity_layer = IdentityAccessLayer(database)
secrets_vault = SecretsVault(database)
agent_registry = AgentRegistry(database)
agent_registry.ensure_default()
approval_center = ApprovalCenter(database)
evidence_layer = EvidenceLayer(database)
observability_layer = ObservabilityLayer(database)
forecasting_engine = ForecastingEngine(database)
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


@app.post("/submit", response_model=SubmitResponse)
async def submit(req: SubmitRequest):
    return await pipeline.run(req)


@app.get("/audit")
async def audit(limit: int = 50):
    return list(database.list_rows("audit_log", limit))


@app.get("/memory")
async def memory(limit: int = 50):
    return list(database.list_rows("memory", limit))


@app.get("/actions")
async def actions(limit: int = 50):
    rows = list(database.list_rows("action_queue", limit))
    for row in rows:
        row["payload"] = json.loads(row["payload"]) if row.get("payload") else {}
    return rows


@app.get("/memory/layers")
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


@app.get("/state/{request_id}")
async def runtime_state(request_id: str, limit: int = 100):
    rows = list(database.list_rows("runtime_state", limit))
    return [row for row in rows if row.get("request_id") == request_id]


@app.post("/memory/proposals/{proposal_id}/approve")
async def approve_memory_proposal(proposal_id: str):
    result = memory_engine.approve_proposal(proposal_id)
    if not result:
        raise HTTPException(status_code=404, detail="Memory proposal not found")
    return result


@app.post("/memory/proposals/{proposal_id}/reject")
async def reject_memory_proposal(proposal_id: str):
    result = memory_engine.reject_proposal(proposal_id)
    if not result:
        raise HTTPException(status_code=404, detail="Memory proposal not found")
    return result


@app.post("/actions/{action_id}/approve")
async def approve_action(action_id: str):
    result = action_queue.approve(action_id)
    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@app.post("/actions/{action_id}/reject")
async def reject_action(action_id: str):
    result = action_queue.reject(action_id)
    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@app.post("/actions/{action_id}/execute")
async def execute_action(action_id: str):
    result = action_queue.execute_noop(action_id)
    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@app.post("/actions/{action_id}/rollback")
async def rollback_action(action_id: str):
    result = action_queue.rollback(action_id)
    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@app.post("/actions/{action_id}/expire")
async def expire_action(action_id: str):
    result = action_queue.expire(action_id)
    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@app.get("/plugins")
async def plugins():
    return read_plugin_manifests()


@app.get("/approvals")
async def approvals(limit: int = 50):
    return list(database.list_rows("approvals", limit))


@app.get("/budget/status")
async def budget_status(limit: int = 50):
    return list(database.list_rows("budget_events", limit))


@app.get("/access/users")
async def users(limit: int = 50):
    return list(database.list_rows("users", limit))


@app.post("/access/users/{user_id}/ensure")
async def ensure_user(user_id: str, access_level: int = 1):
    return identity_layer.ensure_user(user_id, access_level)


@app.post("/secrets")
async def put_secret(req: SecretPutRequest):
    secret_id = secrets_vault.put(req.name, req.value, req.provider)
    return {"id": secret_id, "name": req.name, "stored": True}


@app.get("/secrets/{name}/metadata")
async def secret_metadata(name: str):
    return secrets_vault.metadata(name)


@app.get("/agents")
async def agents(limit: int = 50):
    return list(database.list_rows("agent_registry", limit))


@app.post("/agents")
async def register_agent(req: AgentRegisterRequest):
    return {"id": agent_registry.register(req.model_dump()), "status": "registered"}


@app.get("/evidence")
async def evidence(limit: int = 50):
    return list(database.list_rows("evidence_sources", limit))


@app.get("/observability/events")
async def observability_events(limit: int = 50):
    return list(database.list_rows("observability_events", limit))


@app.post("/forecasts")
async def create_forecast(req: ForecastCreateRequest):
    return forecasting_engine.create_forecast(req)


@app.get("/forecasts")
async def forecasts(limit: int = 50):
    return forecasting_engine.list_forecasts(limit)


@app.post("/forecasts/{forecast_id}/outcome")
async def forecast_outcome(forecast_id: str, req: ForecastOutcomeRequest):
    result = forecasting_engine.resolve_forecast(forecast_id, req)
    if not result:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return result


@app.get("/forecasts/calibration-profile")
async def forecast_calibration_profile():
    return forecasting_engine.calibration_profile()


@app.get("/local-runtime/status")
async def local_runtime_status():
    return await local_runtime.status()


@app.post("/local-runtime/models/{model_name}/load")
async def load_local_model(model_name: str):
    return await local_runtime.load_model(model_name)


@app.post("/local-runtime/models/{model_name}/unload")
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


@app.post("/vector-memory/add")
async def add_vector_memory(req: VectorAddRequest):
    return vector_memory.add(req.namespace, req.content)


@app.post("/vector-memory/search")
async def search_vector_memory(req: VectorSearchRequest):
    return vector_memory.search(req.namespace, req.query, req.limit)


@app.get("/config/policy")
async def policy_config():
    return load_yaml("policy.yaml")


@app.get("/config/model-routing")
async def model_routing_config():
    return load_yaml("model_routing.yaml")


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
        "local_only_mode": os.getenv("LOCAL_ONLY_MODE", "false").lower() == "true",
    }
