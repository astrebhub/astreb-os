# AI CABINET — Governed Hybrid AI Operating System

AI Cabinet is not a chatbot and not a thin API wrapper. It is a secure microkernel control layer for governed AI execution across local and cloud intelligence.

## What It Does

- Routes tasks across OpenAI, Gemini, Ollama/local, manual mode, and placeholder enterprise providers.
- Enforces YAML policy before model calls.
- Masks PII and secrets.
- Blocks cloud routing for personal/confidential data.
- Governs tokens, cost, quotas, and emergency stop.
- Logs audit, budget events, action queue states, and memory proposals.
- Supports governed memory evolution through proposal and approval.
- Provides plugin manifest validation and sandbox metadata.
- Exposes an AI Control Center browser UI.
- Normalizes text, voice, image, file, browser, email, calendar, and plugin action inputs.
- Tracks runtime state transitions and approval center records.
- Adds identity/access, secrets vault, agent registry, evidence, and observability layers.

## Jazekker Phase 1 Skeleton

The Jazekker-specific AI Editorial Cabinet contract lives in:

- `architecture.md`: product architecture, phases, governance flow, and dashboard surface.
- `agents.md`: specialist agent roles, boundaries, approval triggers, and forbidden behavior.
- `workflows.md`: governed editorial, translation, SEO, evidence, community, newsletter, trend, and strategy workflows.
- `policies.yaml`: declarative Phase 1 governance policy for editorial AI operations.

## Folder Structure

```text
ai_cabinet_mvp/
  kernel/ router/ security/ policies/ providers/
  local_runtime/
    models/ embeddings/ vector_memory/ gpu/ quantized/
  plugins/
  memory/ audit/ runtime/ ui/ budget/ voice/
  connectors/ vector_memory/ embeddings/ action_queue/
  backend/
    main.py
    cabinet/
      actions.py
      agent_registry.py
      approval_center.py
      budget_governor.py
      classifier.py
      config.py
      database.py
      evidence.py
      identity.py
      local_runtime.py
      memory_engine.py
      multimodal.py
      observability.py
      output_guard.py
      pii.py
      pipeline.py
      plugin_sandbox.py
      policy.py
      providers.py
      router.py
      secrets_vault.py
      schemas.py
      state_engine.py
      tokens.py
  config/
    policy.yaml
    model_routing.yaml
  frontend/
    index.html
    app.js
    styles.css
```

## Execution Pipeline

```text
INPUT -> MULTIMODAL NORMALIZER -> STATE ENGINE -> PII DETECTOR ->
DATA CLASSIFIER -> POLICY ENGINE -> TOKEN / COST GOVERNOR ->
MODEL / VOICE / TOOL ROUTER -> LOCAL OR CLOUD RUNTIME ->
PLUGIN SANDBOX -> OUTPUT GUARD -> ACTION QUEUE -> APPROVAL CENTER -> AUDIT LOG ->
MEMORY UPDATE PROPOSAL -> HUMAN APPROVAL IF REQUIRED
```

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## Windows Autostart

Install autostart at Windows logon:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\install_autostart.ps1
```

Start script:

```powershell
.\scripts\start_ai_cabinet.ps1
```

Remove autostart:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\uninstall_autostart.ps1
```

Logs are written to `logs/autostart.log` and `logs/autostart_install.log`.

If Windows blocks Scheduled Task registration, use the current-user Startup folder fallback:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\install_startup_folder_autostart.ps1
```

Remove Startup folder fallback:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\uninstall_startup_folder_autostart.ps1
```

## Ubuntu Deployment And Autostart

Install Python 3.11+ and venv support first if needed:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

Deploy the backend dependencies:

```bash
cd ai_cabinet_mvp
chmod +x scripts/*.sh
./scripts/deploy_unix.sh
```

Start manually:

```bash
./scripts/start_ai_cabinet.sh
```

Install current-user autostart with systemd:

```bash
./scripts/install_ubuntu_autostart.sh
```

Check service status and logs:

```bash
systemctl --user status ai-cabinet.service
journalctl --user -u ai-cabinet.service -f
```

Remove Ubuntu autostart:

```bash
./scripts/uninstall_ubuntu_autostart.sh
```

## macOS Deployment And Autostart

Install Python 3.11+ first if needed:

```bash
brew install python
```

Deploy the backend dependencies:

```bash
cd ai_cabinet_mvp
chmod +x scripts/*.sh
./scripts/deploy_unix.sh
```

Start manually:

```bash
./scripts/start_ai_cabinet.sh
```

Install current-user autostart with launchd:

```bash
./scripts/install_macos_autostart.sh
```

Check LaunchAgent status and logs:

```bash
launchctl print gui/$(id -u)/nl.jazekker.ai-cabinet
tail -f logs/launchd.out.log logs/launchd.err.log
```

Remove macOS autostart:

```bash
./scripts/uninstall_macos_autostart.sh
```

## Environment

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash
APP_NAME=AI CABINET v0.2
TOKEN_LIMIT_PER_REQUEST=8000
SESSION_COST_LIMIT=1.00
DAILY_COST_LIMIT=5.00
MONTHLY_COST_LIMIT=100.00
DAILY_TOKEN_LIMIT_PER_USER=50000
LOCAL_ONLY_MODE=false
EMERGENCY_STOP=false
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

## API

- `POST /submit` runs the governed execution pipeline.
- `GET /health` shows runtime pipeline and provider state.
- `GET /budget/status` shows budget event history.
- `GET /local-runtime/status` shows Ollama/local runtime readiness.
- `POST /local-runtime/models/{model}/load` records safe load intent.
- `POST /local-runtime/models/{model}/unload` records safe unload intent.
- `GET /plugins` validates sandbox manifests.
- `GET /actions` shows action lifecycle records.
- `POST /actions/{id}/approve`, `/reject`, `/execute`, `/rollback`.
- `GET /memory/layers` shows governed memory and learning proposals.
- `POST /memory/proposals/{id}/approve`, `/reject`.
- `GET /audit` shows audit records.
- `GET /voice/status` shows future voice pipeline readiness.
- `GET /multimodal/status` shows unified input governance readiness.
- `GET /state/{request_id}` shows state machine transitions.
- `GET /approvals` shows approval center records.
- `GET /access/users` shows identity/access records.
- `POST /secrets` stores a secret in the MVP vault.
- `GET /agents` and `POST /agents` manage agent registry records.
- `GET /evidence` shows source/evidence records.
- `GET /observability/events` shows runtime telemetry.
- `POST /vector-memory/add` stores local deterministic embedding memory.
- `POST /vector-memory/search` searches local SQLite vector memory.
- `POST /forecasts` creates a saved ForecastRecord with base rate, factors, risk layers, bias check, scenarios, and final probability.
- `GET /forecasts` lists saved forecast records.
- `POST /forecasts/{forecast_id}/outcome` resolves a binary forecast and calculates Brier Score.
- `GET /forecasts/calibration-profile` summarizes user calibration, recurring bias, and domain performance.

## Database Schema

SQLite tables:

- `audit_log`: request, risk, data class, policy, provider, tokens, cost, status.
- `action_queue`: draft, pending_approval, approved, executed, rejected, rollback.
- `memory`: operational request/response memory.
- `governed_memory`: layered governed memory.
- `memory_proposals`: learning updates requiring approval.
- `budget_events`: per-user, per-agent, per-session budget records.
- `local_runtime_models`: local model inventory metadata.
- `vector_memory`: placeholder for local vector storage.
- local deterministic embeddings are available for offline vector search in MVP form.
- `runtime_state`: received, normalized, classified, masked, policy_checked, budget_checked, routed, executed, scanned, queued, approved, audited, memory_proposed, completed, failed, rollback_requested.
- `users`, `sessions`, `api_keys`: identity and access.
- `secrets_vault`: MVP encrypted placeholder secret storage.
- `agent_registry`: controlled agent definitions.
- `evidence_sources`: source, URL, timestamp, confidence, verification status, citation.
- `observability_events`: health, latency, failures, blocked actions, policy violations.
- `approvals`: approval center records.
- `forecast_records`: measurable forecasts, outcome status, Brier Score, and full ForecastRecord JSON.

## Long-Term Scaling Roadmap

- Replace local mock with managed Ollama and native GGUF worker pool.
- Add real local embeddings and vector search.
- Add PostgreSQL, pgvector, and append-only audit log.
- Add signed plugin registry.
- Add connector workers with isolated credentials.
- Add policy test suite and governance review UI.
- Add per-agent budgets, model SLAs, latency scoring, and routing simulation.
- Add voice STT/TTS connectors and SIP gateway.

## Enterprise Roadmap

- SSO, RBAC, tenant isolation.
- SIEM export, OpenTelemetry, compliance retention.
- Key vault integration.
- Human approval inbox and dual-control approvals.
- Model risk management, red-team gates, eval pipelines.
- Enterprise connectors for Microsoft Graph, Google Workspace, Slack, Teams, Jira, Notion, CRM.
