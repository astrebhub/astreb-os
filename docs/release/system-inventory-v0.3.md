# System Inventory v0.3: ASTREB / JAZEKKER

Date: 2026-05-27
Scope: runtime inventory for read-only governed production preview

## Service Entry Point

| Item | Current State |
| --- | --- |
| Backend framework | FastAPI |
| App module | `backend/main.py` |
| Local command | `python -m uvicorn main:app --host 127.0.0.1 --port 8000` |
| Local public port | `8000` by convention in README/docs |
| Current production deployment | Not confirmed |
| Background workers | None implemented in this snapshot |
| Scheduled tasks | None implemented in this snapshot |
| Multi-worker safety | Not approved; JSON stores are single-process/local MVP only |

## Public And Preview Routes

| Route | Surface | Preview Status |
| --- | --- | --- |
| `/health` | Health response | Public operational check; no secrets. |
| `/` | Redirect to `/jazekker` | Public. |
| `/jazekker` | Foundation homepage | Allowed read-only preview. |
| `/jazekker/orientation` | Orientation stream | Allowed read-only preview. |
| `/jazekker/local` | Local orientation preview | Allowed read-only preview. |
| `/jazekker/research` | Research desk preview | Allowed read-only preview. |
| `/jazekker/ai-cabinet` | AI Cabinet explanation | Allowed read-only preview. |
| `/jazekker/testbox` | TESTBOX demo explanation | Allowed observation-only preview. |
| `/jazekker/co-creation` | Coordination preview | Allowed read-only preview. |
| `/jazekker/news`, `/jazekker/public-news`, `/jazekker/workspace` | Local news/workspace surfaces | Review before public deployment. |
| `/jazekker/banner`, `/jazekker/assets/{asset_name}` | Static assets/surfaces | Allowed after asset review. |
| `/jazekker/articles`, `/jazekker/articles/{slug}` | Local article JSON and rendered pages | Allowed only for reviewed local content. |
| `/testbox/*` | Full TESTBOX shell | Operator/demo UI; runtime API remains privileged. |

## Privileged TESTBOX Runtime API

All `/api/testbox/runtime/*` endpoints require
`X-AI-Cabinet-Admin-Token`.

| Method And Route | Function | Boundary |
| --- | --- | --- |
| `POST /api/testbox/runtime/message` | Governed orientation processing | Admin token; no external execution authority. |
| `GET /api/testbox/runtime/events` | Runtime event readback | Admin token; local JSONL source. |
| `GET /api/testbox/runtime/sources` | Source registry | Admin token. |
| `GET /api/testbox/runtime/roles` | Role registry | Admin token. |
| `GET /api/testbox/runtime/constitution` | Instruction registry | Admin token. |
| `POST /api/testbox/runtime/clipboard/read` | Explicit local clipboard read | Admin token plus localhost-only check. |
| `POST /api/testbox/runtime/approval` | Approval event recording | Admin token; records evidence only. |
| `POST /api/testbox/runtime/actions/{id}/approve` | Approve governed action | Admin token; human authority required. |
| `POST /api/testbox/runtime/actions/{id}/reject` | Reject governed action | Admin token. |
| `POST /api/testbox/runtime/actions/{id}/execute` | Request ASTI execution | Admin token; Telegram external delivery frozen in preview. |
| `GET /api/testbox/runtime/meta-qms` | META-QMS overview | Admin token. |
| `POST /api/testbox/runtime/meta-qms/assess` | Quality assessment/proposal | Admin token; proposal only. |
| `POST /api/testbox/runtime/meta-qms/proposals/{id}/decision` | Human approve/reject decision | Admin token; no automatic implementation. |

## ASTI Boundary API

Current implementation exposes `/asti/*`; versioned `/api/asti/*` is a pending
production ingress decision.

| Method And Route | Function | Boundary |
| --- | --- | --- |
| `POST /asti/task` | Create queued action | Admin token; action begins `pending`. |
| `GET /asti/inbox` | List queued actions | Admin token. |
| `POST /asti/actions/{id}/approve` | Approve pending action | Admin token; records approval audit. |
| `POST /asti/actions/{id}/reject` | Reject pending action | Admin token. |
| `POST /asti/actions/{id}/execute` | Execute approved action | Admin token; external Telegram delivery blocked in preview/prod. |
| `POST /webhooks/telegram` | Telegram owner command ingress | Webhook secret, owner-chat check, replay protection; external delivery still blocked. |

## Environment Variables

| Variable | Purpose | Preview Rule |
| --- | --- | --- |
| `AI_CABINET_ENV` | `dev` or `prod` runtime mode | In `prod`, privileged token is mandatory and external execution flag is forbidden. |
| `ADMIN_API_TOKEN` | Shared privileged admin token | Required for privileged runtime; must come from environment/secret manager. |
| `ASTI_EXTERNAL_EXECUTION_ENABLED` | External execution release flag | Must remain `false`; `true` is rejected in `prod`. |
| `TELEGRAM_BOT_TOKEN` | Telegram delivery credential | Not required for read-only preview; never commit. |
| `TELEGRAM_OWNER_CHAT_ID` | Allowed Telegram owner chat | Required only if webhook commands are enabled. |
| `TELEGRAM_WEBHOOK_SECRET` | Telegram webhook shared secret | Required for webhook ingress; never commit. |

## Runtime And Audit Stores

| Path | Content | Current Status | Production Requirement |
| --- | --- | --- | --- |
| `action_queue/asti_actions.json` | ASTI action queue | Ignored local state | Transactional store and idempotent claims. |
| `action_queue/telegram_processed_updates.json` | Telegram replay cache | Ignored local state | Durable replay store with retention. |
| `audit/asti_events.jsonl` | ASTI audit events | Ignored append-only local JSONL | Immutable protected audit DB. |
| `audit/testbox_runtime_events.jsonl` | TESTBOX runtime events | Ignored append-only local JSONL | Immutable protected audit DB. |
| `audit/testbox_session_context.json` | Session context | Ignored local state | Protected session store. |
| `audit/meta_qms_evolution_proposals.json` | META-QMS proposals | Ignored local state | Redaction-aware durable proposal store. |
| `backend/ai_cabinet.db` | Legacy/local database state | Ignored | Not a release artifact. |

## External Integrations

| Integration | Code Path | Preview Status |
| --- | --- | --- |
| Telegram sendMessage | `backend/asti/executors.py` | External delivery disabled for preview/prod. |
| Telegram webhook | `backend/asti/api.py` | Secret/owner protected; should not be public until ingress review. |
| GitHub Actions | `.github/workflows/ci.yml` | Configured; remote passing evidence still required. |
| Notion governance records | External project documentation | Updated manually; not a runtime dependency. |

## Dependencies

Runtime Python dependencies:

- `fastapi==0.115.6`
- `uvicorn==0.34.0`
- `pytest==8.3.4`
- `httpx==0.28.1`

CI tool dependencies:

- `ruff`
- `pip-audit`
