from typing import Any, Dict, List


PROCESS_MAP = {
    "principle": "The model asks. The microkernel decides.",
    "pipeline": [
        {"step": "INPUT", "owner": "Gateway", "decision": "Accept text, voice, image, file, browser, email, calendar, or plugin task."},
        {"step": "PII DETECTOR", "owner": "Security", "decision": "Mask email, phone, IBAN, names, and secrets before provider calls."},
        {"step": "DATA CLASSIFIER", "owner": "Classifier", "decision": "Classify public, internal, confidential, or personal data."},
        {"step": "POLICY ENGINE", "owner": "Policies", "decision": "Apply YAML rules: cloud allowed, local-only, approval, mask, or block."},
        {"step": "TOKEN / COST GOVERNOR", "owner": "Budget", "decision": "Estimate tokens/cost and enforce limits."},
        {"step": "MODEL ROUTER", "owner": "Routing", "decision": "Choose OpenAI, Gemini, OpenRouter, Ollama, local fallback, or manual mode."},
        {"step": "LOCAL/CLOUD DECISION", "owner": "Runtime", "decision": "Sensitive/high-risk stays local; public low-risk may use cloud/free routes."},
        {"step": "PROVIDER ADAPTER", "owner": "Providers", "decision": "Call configured provider or fall back safely when keys/models are unavailable."},
        {"step": "OUTPUT GUARD", "owner": "Security", "decision": "Scan output for leakage, dangerous instructions, and unauthorized action claims."},
        {"step": "ACTION QUEUE", "owner": "Actions", "decision": "Convert tool work into draft, pending approval, approved, executed, rejected, rollback, or expired."},
        {"step": "AUDIT LOG", "owner": "Audit", "decision": "Record request, risk, policy, route, provider, tokens, cost, status, and action id."},
        {"step": "MEMORY PROPOSAL", "owner": "Memory", "decision": "Suggest learning updates; human approval required before durable memory changes."},
    ],
    "routing_rules": [
        "Personal/confidential/high-risk -> local-only or local-safe-fallback.",
        "Public low-risk -> cloud/free route if keys exist.",
        "Missing provider key -> local-safe-fallback.",
        "Action modes -> approval queue.",
    ],
}


PANEL_AUDIT: List[Dict[str, Any]] = [
    {"panel": "Runtime", "button": "healthBtn", "endpoint": "/health", "access": "public", "status": "working", "purpose": "Backend health, pipeline, provider state, connector summary."},
    {"panel": "Policies", "button": "policyBtn", "endpoint": "/config/policy", "access": "admin", "status": "working", "purpose": "YAML policy rules currently loaded by the runtime."},
    {"panel": "Routing", "button": "routingBtn", "endpoint": "/config/model-routing", "access": "admin", "status": "working", "purpose": "Model/provider routing rules and local runtime declarations."},
    {"panel": "Budget", "button": "budgetBtn", "endpoint": "/budget/status", "access": "admin", "status": "working_mvp", "purpose": "Token/cost events. Governance exists; rich dashboards are future work."},
    {"panel": "Plugins", "button": "pluginsBtn", "endpoint": "/connectors/status", "access": "public", "status": "working", "purpose": "ASTI connector manifests, signature state, data classes, and execution gates."},
    {"panel": "Actions", "button": "actionsBtn", "endpoint": "/actions", "access": "admin", "status": "working_mvp", "purpose": "Approval-gated draft/action queue. Real external execution remains disabled."},
    {"panel": "Approvals", "button": "approvalsBtn", "endpoint": "/approvals", "access": "admin", "status": "working_mvp", "purpose": "Approval records for actions and memory proposals."},
    {"panel": "Memory", "button": "memoryLayersBtn", "endpoint": "/memory/layers", "access": "admin", "status": "working_mvp", "purpose": "Governed memory layers and learning proposals."},
    {"panel": "Audit", "button": "auditBtn", "endpoint": "/audit", "access": "admin", "status": "working", "purpose": "Immutable-style SQLite audit records for demo/MVP."},
    {"panel": "Local Models", "button": "localRuntimeBtn", "endpoint": "/local-runtime/status", "access": "public", "status": "working", "purpose": "Ollama/local model inventory and offline-capable runtime status."},
    {"panel": "Vector", "button": "vectorBtn", "endpoint": "/vector-memory/search", "access": "admin", "status": "working_mvp", "purpose": "Local deterministic embedding/vector search over stored memory."},
    {"panel": "Voice", "button": "voiceBtn", "endpoint": "/voice/status", "access": "public", "status": "prepared", "purpose": "Voice runtime readiness. Browser STT/TTS UI exists; production voice connectors are future work."},
    {"panel": "Multimodal", "button": "multimodalBtn", "endpoint": "/multimodal/status", "access": "public", "status": "prepared", "purpose": "Normalizes multiple input types into one governance pipeline."},
    {"panel": "Access", "button": "accessBtn", "endpoint": "/access/users", "access": "admin", "status": "working_mvp", "purpose": "Basic users/access-level records. Production RBAC/AuthN is future work."},
    {"panel": "Agents", "button": "agentsBtn", "endpoint": "/agents", "access": "admin_with_public_fallback", "status": "working", "purpose": "Agent registry: guide, operator, governance, GitHub, computer, Microsoft, editorial, research, risk."},
    {"panel": "Personalization", "button": "personalizationBtn", "endpoint": "/runtime/personalization", "access": "public", "status": "working", "purpose": "Profiles, dialog modes, and public agent list."},
    {"panel": "Evidence", "button": "evidenceBtn", "endpoint": "/evidence", "access": "admin", "status": "working_mvp", "purpose": "Source metadata for research/news workflows."},
    {"panel": "Observe", "button": "observabilityBtn", "endpoint": "/observability/events", "access": "admin", "status": "working_mvp", "purpose": "Runtime events, policy checks, plugin checks, and latency records."},
    {"panel": "Forecasts", "button": "forecastsBtn", "endpoint": "/forecasts", "access": "admin", "status": "working_mvp", "purpose": "Forecast records for uncertainty and calibration workflows."},
    {"panel": "Calibration", "button": "calibrationBtn", "endpoint": "/forecasts/calibration-profile", "access": "admin", "status": "working_mvp", "purpose": "Forecast calibration profile and Brier score readiness."},
]


def panel_audit() -> Dict[str, Any]:
    return {
        "summary": {
            "total_panels": len(PANEL_AUDIT),
            "public_panels": len([p for p in PANEL_AUDIT if p["access"] == "public"]),
            "admin_panels": len([p for p in PANEL_AUDIT if "admin" in p["access"]]),
            "principle": "The model asks. The microkernel decides.",
        },
        "legend": {
            "working": "Endpoint and UI path are functional.",
            "working_mvp": "Functional MVP layer; needs hardening for enterprise use.",
            "prepared": "Architecture/UI exists; deeper execution layer is future work.",
        },
        "panels": PANEL_AUDIT,
    }
