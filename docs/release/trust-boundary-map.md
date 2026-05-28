# Trust Boundary Map: ASTREB / JAZEKKER v0.3

Date: 2026-05-27
Target posture: read-only governed production preview

## Boundary Diagram

```text
Public
  |
  | read-only HTTP
  v
JAZEKKER UI
  |
  | privileged operator token required for runtime actions
  v
AI Cabinet / Runtime Policy Boundary
  |
  | governed routing, role and policy evaluation
  v
TESTBOX
  |
  | approval and audit boundary
  v
ASTI
  |
  | external execution boundary, frozen in preview
  v
External Services
```

## Trust Zones

| Zone | Trust Level | Allowed Capability | Forbidden Capability |
| --- | --- | --- | --- |
| Public | Untrusted | Read approved static/orientation pages. | Runtime mutation, privileged API calls, external execution. |
| JAZEKKER UI | Low trust presentation | Display orientation previews and explanations. | Authority decisions or hidden execution. |
| Operator Browser Session | Conditional trust | Store admin token in session storage for local/operator actions. | Persistent credential storage or public exposure. |
| AI Cabinet / TESTBOX API | Privileged runtime zone | Governed analysis, routing, audit, proposal creation. | Unauthenticated access or autonomous action. |
| META-QMS | Privileged governance loop | Propose improvements and record human decisions. | Apply changes automatically. |
| ASTI | Execution boundary | Queue, approve, reject and locally/no-op execute after approval. | External delivery in production preview. |
| External Services | Out of preview scope | None for read-only preview. | Telegram, WhatsApp, email or autonomous distribution. |

## Auth Boundaries

| Boundary | Mechanism | Current Evidence |
| --- | --- | --- |
| TESTBOX runtime | `X-AI-Cabinet-Admin-Token` matched to `ADMIN_API_TOKEN` | Unauthenticated runtime tests reject requests. |
| ASTI administrative API | Same shared admin token | Direct ASTI unauthenticated test rejects requests. |
| Telegram webhook | `X-Telegram-Bot-Api-Secret-Token` plus owner chat ID | Tests reject invalid secret and unknown chat. |
| Production-preview startup | `AI_CABINET_ENV=prod` config validation | Startup fails without token and now fails if external execution is enabled. |

## Approval Boundaries

| Boundary | Rule |
| --- | --- |
| High-risk orientation/LegalBox | Requires human review; response must expose approval boundary. |
| ASTI action execution | Requires `pending -> approved` before execution attempt. |
| META-QMS proposal | Human approve/reject is recorded; approval does not implement change. |
| External execution | Denied for production preview regardless of action approval. |

## Audit Boundaries

| Boundary | Audit Events |
| --- | --- |
| Runtime message processing | `MESSAGE_RECEIVED`, routing, risk, source and review events. |
| Approval decisions | `APPROVAL_GRANTED` / `APPROVAL_DENIED`. |
| ASTI action lifecycle | `created`, `approved`, `rejected`, `execution_blocked`, `execution_started`, `executed`, `execution_failed`. |
| Telegram ingress defense | `invalid_webhook_secret`, `duplicate_webhook_update`. |
| META-QMS | `QUALITY_ASSESSED`, `DEVIATION_RECORDED`, `EVOLUTION_PROPOSED`, `EVOLUTION_APPROVED`, `EVOLUTION_REJECTED`. |

## Secret Handling Zones

| Secret | Handling Zone | Rule |
| --- | --- | --- |
| `ADMIN_API_TOKEN` | Runtime environment / deployment secret manager | Never commit; fail closed if missing. |
| `TELEGRAM_BOT_TOKEN` | Future execution secret zone | Not needed for read-only preview; never commit. |
| `TELEGRAM_WEBHOOK_SECRET` | Runtime environment | Required only for webhook ingress; never log value. |
| Browser session token | Operator browser session | Session storage only; do not embed in public HTML. |

## Human Override Boundaries

Human authority can reject, pause or withhold approval at these points:

- release/merge decision;
- security gate approval;
- runtime action approval/rejection;
- META-QMS proposal decision;
- ASTI external execution release gate;
- incident response revoke switch.

No AI component may cross those boundaries autonomously.
