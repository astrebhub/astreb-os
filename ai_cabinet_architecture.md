# AI CABINET — Hybrid AI Microkernel Operating System

AI Cabinet is an operating system for governed AI execution. AI models are not trusted; AI Cabinet is the trusted layer. The core philosophy is **Control Before Autonomy**.

## Modular Architecture

```text
/kernel              trusted control boundary
/router              model and workload routing
/security            PII, secrets, redaction, leak scanning
/policies            YAML governance rules
/providers           OpenAI, Gemini, Claude, DeepSeek, Mistral, manual mode
/local_runtime       Ollama, GGUF, CPU/GPU, quantized local models
/plugins             sandboxed permission-manifest plugins
/memory              governed layered memory
/audit               immutable evidence trail
/runtime             pipeline orchestration
/ui                  AI Control Center
/budget              cost, quota, kill-switch governance
/voice               voice pipeline readiness
/multimodal_runtime  text, voice, image, files, browser, actions
/voice_runtime       STT, TTS, calls, emotion, routing, latency, turns
/state_engine        governed runtime state machine
/approval_center     human approval workflow
/identity            users, roles, permissions, sessions, API keys
/secrets             secrets vault boundary
/agents              agent registry
/observability       runtime health, latency, policy violations, failures
/evidence            sources, citations, confidence, verification status
/connectors          Telegram, WhatsApp, email, calendar, browser, SIP targets
/vector_memory       vector store abstraction
/embeddings          local/cloud embedding providers
/forecasting         decision calibration, risk scoring, outcomes, Brier Score
/action_queue        draft, approval, execution, rollback lifecycle
```

Backend implementation lives under `backend/cabinet`, with matching top-level architecture folders for the OS domains.

## Mandatory Execution Pipeline

```text
INPUT
 ↓
MULTIMODAL NORMALIZER
 ↓
STATE ENGINE
 ↓
PII DETECTOR
 ↓
DATA CLASSIFIER
 ↓
POLICY ENGINE
 ↓
TOKEN / COST GOVERNOR
 ↓
MODEL / VOICE / TOOL ROUTER
 ↓
LOCAL OR CLOUD RUNTIME
 ↓
PLUGIN SANDBOX
 ↓
PROVIDER ADAPTER
 ↓
OUTPUT GUARD
 ↓
ACTION QUEUE
 ↓
APPROVAL CENTER
 ↓
AUDIT LOG
 ↓
MEMORY UPDATE PROPOSAL
 ↓
HUMAN APPROVAL (IF REQUIRED)
```

## Hybrid Intelligence

Routing considers sensitivity, risk, cost, latency intent, task type, policy, privacy classification, and local availability.

- Sensitive data: local only.
- Public content: cloud allowed.
- Complex medium-risk reasoning: cloud premium route when policy permits.
- Cheap bulk processing: local model route.
- Offline operation: local mock or Ollama route.
- Local-only mode: enforced globally via `LOCAL_ONLY_MODE=true` or per-request UI flag.

## Local Runtime

Implemented local runtime manager supports:

- Ollama status and generation adapter.
- GGUF/CPU/GPU/quantized model slots as runtime targets.
- Supported families: Llama 3, Mistral, DeepSeek, Phi, Qwen Coder.
- Local embeddings and vector search placeholders.
- Offline operation through local mock fallback.
- Model load/unload request endpoints with safe no-destructive behavior.

## Governed Memory

Memory layers:

1. Constitution memory
2. Role / job instruction memory
3. Policy memory
4. Project memory
5. Operational memory
6. Learning memory
7. Audit memory

Learning flow:

```text
Observation -> Hypothesis -> Proposal -> Approval Required -> Memory Update -> Audit Record
```

The runtime may observe and propose. It may not rewrite constitution memory, role instructions, policy, or audit history.

## Security

- PII and secret masking.
- Output guard for PII leakage, dangerous instructions, policy violations, secret exposure, and unauthorized action claims.
- Local-only enforcement.
- Sandboxed plugin manifests.
- Access levels 0-5.
- Identity/access roles: owner, admin, operator, agent, guest, client.
- Secrets vault table with `.env` fallback, prepared for real KMS replacement.
- Per-user and per-agent budget events.
- Emergency stop via `EMERGENCY_STOP=true`.
- No direct real-world action execution.

## State Machine

```text
received -> normalized -> classified -> masked -> policy_checked ->
budget_checked -> routed -> executed -> scanned -> queued -> approved ->
audited -> memory_proposed -> completed
```

Failure and recovery states:

```text
failed
rollback_requested
```

## Evidence And Observability

Evidence records store source, URL, timestamp, confidence, verification status, and citation. Observability records runtime health, latency, token/cost events, plugin failures, blocked actions, and policy violations.

## Forecasting And Risk Calibration

The forecasting module converts uncertain questions into measurable events, starts from a base rate, applies weighted factors, scores legal, human, and technical risk, checks cognitive bias, generates scenario distributions, and saves ForecastRecord entries. Resolved forecasts store binary outcome and Brier Score, then feed the calibration profile.

## Action Lifecycle

```text
draft -> pending_approval -> approved -> executed -> rollback
                       ↘ rejected
```

`executed` is a no-op execution record in this MVP. Real external execution requires future signed connectors.

## Enterprise Roadmap

- AuthN/AuthZ and tenant isolation.
- PostgreSQL plus append-only audit store.
- Signed plugin registry and runtime sandboxing.
- Hardware-backed key management.
- Policy-as-code review workflow.
- Model evaluation and red-team gates.
- Enterprise connectors: Microsoft Graph, Google Workspace, Slack, Teams, Jira, Notion.
- Observability: OpenTelemetry, SIEM export, budget dashboards.
- HA deployment: API workers, queue workers, vector DB, secrets manager.
