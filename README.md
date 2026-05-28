# JAZEKKER

JAZEKKER is a calm orientation news portal.

It is designed to turn noisy information into readable civic signals:

```text
noise -> signal -> context -> orientation
```

The public product is not a dashboard, not a chatbot, and not a control panel.
It is a lightweight news and orientation surface for readers.

## What This Branch Contains

- Public homepage: `/jazekker`
- Public news feed: `/jazekker/news`
- Readable article pages: `/jazekker/articles/{slug}`
- ASTREB TESTBOX governance console: `/testbox`
- Local JSON article content
- Static visual assets
- Minimal FastAPI runtime

## Project Structure

```text
backend/
  main.py                 # minimal JAZEKKER FastAPI app
  requirements.txt

frontend/
  jazekker.html           # public homepage
  jazekker-news.html      # public news feed
  assets/                 # public visual assets

content/
  articles/               # local published article JSON

tests/
  test_jazekker_surfaces.py
```

## Run Locally

```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/jazekker
http://127.0.0.1:8000/testbox
```

## ASTREB TESTBOX

TESTBOX is a dynamic AI governance and demonstration environment. It is separate
from AI Cabinet: AI Cabinet is the static governance architecture, while TESTBOX
shows runtime orchestration, routing, approvals, audit, quality, PII masking, and
Administrator explainability.

Status:

```text
TESTBOX v0.1 = historical local functional smoke-test milestone.
TESTBOX v0.3 = local governed runtime baseline under release-gate review.
```

Acceptance report:

```text
docs/testbox-v0.1-acceptance-report.md
```

v0.2 governed business acceptance cases:

```text
docs/testbox-v0.2-acceptance-cases.md
```

Operations guide:

```text
docs/testbox-operations-guide.md
```

Starter kit comparison and integration note:

```text
docs/testbox-starter-kit-comparison.md
governance/testbox-starter-kit/
```

Runtime model:

```text
docs/testbox-runtime-model.md
```

LegalBox module:

```text
docs/legalbox-for-testbox.md
```

v0.2 backend refactor architecture:

```text
docs/testbox-v0.2-refactor-architecture.md
docs/testbox-v0.2-implementation-plan.md
```

v0.3 situational orientation target architecture and constitution:

```text
docs/testbox-v0.3-situational-orientation-architecture.md
docs/ai-runtime-constitution-v2.md
```

Governed local runtime API (admin-token protected):

```text
POST /api/testbox/runtime/message
GET  /api/testbox/runtime/events
GET  /api/testbox/runtime/sources
POST /api/testbox/runtime/approval
```

The v0.2 runtime begins moving TESTBOX execution out of the frontend and into a
backend event pipeline. The current `/testbox` UI remains the observation and
demo console while backend events become the source of truth.

### TESTBOX Orientation Core

The backend now routes every user message through a central orientation layer
before any specialised answer strategy:

```text
context -> normalization -> intent -> domain graph -> mode -> governance -> route -> answer
```

`Orientation Core` preserves short follow-up context, normalizes regulated
terms and common typing errors, selects `LegalBox`, `BusinessBox`,
`DocumentBox`, `LetterBox`, or `ASTI Action Mode`, and emits observable events
for domain graph, mode, route, and answer-strategy decisions. ASTI orientation
never sends from chat: `TestboxOrchestrator` places an explicit external-action
request into the ASTI queue as `pending`, records `GOVERNED_ACTION_QUEUED`, and
external delivery still requires the separate approval and governed execute
endpoints. The queued payload comes from the user's explicit request, never
from generated answer text.

Operational roles are backend runtime assignments, separate from skills and
policies. `GET /api/testbox/runtime/roles` exposes the core role registry.
Every oriented message records `ROLE_ASSIGNMENT_SELECTED`: it activates
`Orientation Architect`, `Runtime Orchestrator`, `Governance Officer`,
`Audit Narrator`, and `Memory Coordinator`, plus a bounded specialist such as
`LegalBox Specialist`, `BusinessBox Strategist`, `DocumentBox Analyst`,
`LetterBox Composer`, or `ASTI Action Supervisor` when the selected mode
requires it.

Behavioral runtime instructions form a separate `AI Runtime Constitution`
layer rather than being embedded into role labels. The backend exposes:

```text
GET /api/testbox/runtime/constitution
```

Each processed message reports the active system, role, skill, and policy
instruction identifiers and records `BEHAVIORAL_INSTRUCTIONS_APPLIED`. This
keeps the execution rule visible: orientation first, governance second,
execution third, audit always.

## ASTI Telegram Approval Loop

ASTI queues outbound actions and will not run an executor until its action has
been explicitly approved. Configure Telegram with:

```text
TELEGRAM_BOT_TOKEN=<bot token>
TELEGRAM_OWNER_CHAT_ID=<approved owner chat id>
TELEGRAM_WEBHOOK_SECRET=<Telegram webhook secret token>
AI_CABINET_ENV=dev|prod
ADMIN_API_TOKEN=<required token for privileged runtime endpoints>
ASTI_EXTERNAL_EXECUTION_ENABLED=false
```

API:

```text
POST /asti/task
GET  /asti/inbox
POST /asti/actions/{action_id}/approve
POST /asti/actions/{action_id}/reject
POST /asti/actions/{action_id}/execute
POST /webhooks/telegram
```

The Telegram webhook accepts owner-only commands `/task <text>`, `/actions`,
`/approve <action_id>`, `/reject <action_id>`, `/execute <action_id>`, and
`/status`. Command processing returns JSON; only approved `/execute` invokes
Telegram `sendMessage`. Local integrations can select `local_report` or `no_op`
as the executor while retaining the same approval gate and audit trail.

Telegram must send the configured `TELEGRAM_WEBHOOK_SECRET` in the
`X-Telegram-Bot-Api-Secret-Token` header. ASTI also persists handled Telegram
`update_id` values and ignores repeated updates.

Direct `/asti/*` requests and all TESTBOX runtime API endpoints under
`/api/testbox/runtime/*` must
supply `ADMIN_API_TOKEN` in the `X-AI-Cabinet-Admin-Token` header. Without a
configured token these endpoints fail closed. In `AI_CABINET_ENV=prod`,
startup fails when `ADMIN_API_TOKEN` is missing.

For a controlled local operator session that uses protected UI controls, set
the token only in the current browser tab:

```javascript
sessionStorage.setItem("astreb.admin_token", "<ADMIN_API_TOKEN>");
```

Real Telegram execution is frozen by default. Keep
`ASTI_EXTERNAL_EXECUTION_ENABLED=false` for the read-only governed production
preview. In `AI_CABINET_ENV=prod`, startup refuses
`ASTI_EXTERNAL_EXECUTION_ENABLED=true`; enabling a real external executor
requires a separate future release line and governance decision. Raw runtime
state in `audit/` is local-only and ignored by Git; retain only anonymized
audit reports as repository evidence.

Execution moves through:

```text
pending -> approved -> execution_in_progress -> executed
```

Before an executor is called, ASTI persists `execution_in_progress`,
`execution_started_at`, and an `execution_attempt_id`. If delivery fails or
the process exits during delivery, the action is left in progress for manual
reconciliation rather than being sent again automatically.

Deployment warning: the MVP stores actions and processed webhook IDs as JSON,
and audit entries as JSONL. This storage contract supports single-process
deployment only. Do not use multiple workers or replicas until action claims
and audit transitions use transactional shared storage.

## Editorial Principle

JAZEKKER does not compete on outrage, speed, or volume.

It competes on:

- clarity
- context
- source awareness
- calm presentation
- orientation value

## Current Status

This branch is the public news-portal version of JAZEKKER.
