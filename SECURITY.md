# Security Policy

AI Cabinet is a governed AI control-plane MVP. Treat it as a local-first
runtime unless you have explicitly configured authentication, network
boundaries, managed secrets, and deployment hardening.

## Supported Security Posture

- Public cloud model calls must receive masked input only.
- Personal and confidential data are routed local-only by policy.
- Real-world actions are drafts or approval-queue records in the MVP.
- ASTI administrative endpoints and all TESTBOX runtime API endpoints require
  `X-AI-Cabinet-Admin-Token`; when `ADMIN_API_TOKEN` is absent these
  endpoints are disabled rather than unauthenticated.
- In `AI_CABINET_ENV=prod`, the runtime refuses startup without
  `ADMIN_API_TOKEN`.
- The read-only production preview refuses startup if
  `ASTI_EXTERNAL_EXECUTION_ENABLED=true` is configured. Real Telegram delivery
  requires a separate future release line and governance decision.
- Telegram ASTI webhooks require `X-Telegram-Bot-Api-Secret-Token` matching
  `TELEGRAM_WEBHOOK_SECRET`, in addition to owner-chat validation.

## Reporting A Vulnerability

Open a private security advisory on GitHub if available, or contact the
repository owner directly. Do not publish exploit details before maintainers
have had a reasonable chance to respond.

## Known MVP Limitations

- The development secrets store is not a production KMS. Replace it with a
  managed key-management backend before production use.
- SQLite is used for local development storage.
- Plugin sandboxing validates manifests but does not yet execute plugins in
  hardened process/container isolation.
- ASTI JSON/JSONL storage supports single-process deployment only; multiple
  workers or replicas require transactional shared storage first.
- Raw runtime stores under `audit/` are local-only and excluded from Git.
  Repository audit evidence must be an anonymized review report.
- Authentication denial attempts are written to application logs without
  token values; durable security-event storage remains required before
  production operation.
