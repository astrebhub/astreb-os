# System Boundaries: v0.3 Local Governed MVP

Date: 2026-05-27
Status: Canonical boundary inventory for local freeze review

## Layer Responsibilities

| Layer | Responsibility | Current Local Boundary |
| --- | --- | --- |
| Frontend | Public orientation and static previews | JAZEKKER routes are present locally; no external execution authority. |
| Runtime API | Governed runtime interactions | `/api/testbox/runtime/*` requires admin-token authorization. |
| Audit storage | Runtime evidence | Local JSONL/JSON artifacts; raw stores excluded from Git. |
| Execution service | ASTI action boundary | Admin-gated queue and approval; Telegram execution off by default. |
| QMS service | Quality and evolution review | Auth-gated proposals and human decisions; no automatic mutation. |

## Local Public Routes

| Route | Surface | Production Preview Classification |
| --- | --- | --- |
| `/jazekker` | Foundation homepage | Allowed as read-only public surface after deployment review. |
| `/jazekker/orientation` | Orientation stream | Allowed as read-only preview. |
| `/jazekker/local` | Local orientation preview | Allowed as read-only preview. |
| `/jazekker/research` | Research desk preview | Allowed as read-only preview. |
| `/jazekker/ai-cabinet` | Governance explanation demo | Allowed as explanatory preview. |
| `/jazekker/testbox` | TESTBOX demo surface | Allowed as observation-only preview. |
| `/jazekker/co-creation` | Coordination preview | Allowed as preview only. |
| `/testbox/*` | Full cockpit static shell | Operator/demo surface; runtime operations require token. |

## Runtime API Inventory

| Route | Purpose | Boundary |
| --- | --- | --- |
| `POST /api/testbox/runtime/message` | Execute local governed orientation processing | Admin token required. |
| `GET /api/testbox/runtime/events` | Read runtime event evidence | Admin token required. |
| `GET /api/testbox/runtime/sources` | Read runtime source registry | Admin token required. |
| `GET /api/testbox/runtime/roles` | Read runtime role registry | Admin token required. |
| `GET /api/testbox/runtime/constitution` | Read runtime instructions registry | Admin token required. |
| `POST /api/testbox/runtime/clipboard/read` | Read explicit local clipboard input | Admin token plus localhost constraint required. |
| `POST /api/testbox/runtime/approval` | Record runtime approval evidence | Admin token required. |
| `POST /api/testbox/runtime/actions/{id}/approve` | Approve queued action | Admin token required. |
| `POST /api/testbox/runtime/actions/{id}/reject` | Reject queued action | Admin token required. |
| `POST /api/testbox/runtime/actions/{id}/execute` | Request governed execution | Admin token required; external executor remains frozen. |
| `GET /api/testbox/runtime/meta-qms` | Inspect review loop | Admin token required. |
| `POST /api/testbox/runtime/meta-qms/assess` | Register assessment/proposal | Admin token required. |
| `POST /api/testbox/runtime/meta-qms/proposals/{id}/decision` | Record human decision | Admin token required. |

## ASTI Inventory

The current implementation uses `/asti/*`, rather than the aspirational
`/api/asti/*` naming. Renaming or versioned gateway mapping is a pending API
normalization decision.

| Route | Purpose | Boundary |
| --- | --- | --- |
| `POST /asti/task` | Create action | Admin token required. |
| `GET /asti/inbox` | List actions | Admin token required. |
| `POST /asti/actions/{id}/approve` | Approve action | Admin token required. |
| `POST /asti/actions/{id}/reject` | Reject action | Admin token required. |
| `POST /asti/actions/{id}/execute` | Execute approved action | Admin token required; external delivery frozen by default. |
| `POST /webhooks/telegram` | Telegram owner command boundary | Webhook secret and owner-chat verification; external delivery freeze still applies. |

## Runtime And Audit Stores

| Store | Content | Git Policy | Production Status |
| --- | --- | --- | --- |
| `action_queue/asti_actions.json` | Pending/action state | Ignored | Replace with transactional storage. |
| `action_queue/telegram_processed_updates.json` | Replay protection state | Ignored | Replace with durable atomic store. |
| `audit/asti_events.jsonl` | ASTI event audit | Ignored raw state | Durable append-only audit required. |
| `audit/testbox_runtime_events.jsonl` | TESTBOX events | Ignored raw state | Durable append-only audit required. |
| `audit/testbox_session_context.json` | Runtime session memory | Ignored raw state | Protected session storage required. |
| `audit/meta_qms_evolution_proposals.json` | QMS proposals | Ignored raw state | Durable redaction-aware review store required. |

## Secrets And Configuration

| Configuration | Treatment |
| --- | --- |
| `ADMIN_API_TOKEN` | Runtime environment secret; never stored in Git. |
| `TELEGRAM_BOT_TOKEN` | Execution secret; never stored in Git. |
| `TELEGRAM_OWNER_CHAT_ID` | Runtime configuration; deploy securely. |
| `TELEGRAM_WEBHOOK_SECRET` | Runtime secret; never stored in Git. |
| `ASTI_EXTERNAL_EXECUTION_ENABLED` | Must remain `false` unless separately approved. |
| `.env` and `.env.production` | Ignored local/deployment secret stores. |
| `.env.example` | Commit-safe placeholder template only. |
