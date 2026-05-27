# Security Open Risks: v0.3 Gate

Date: 2026-05-27
Gate stance: controlled local MVP only; production blocked until required risks close

## Controls Implemented Locally

- Shared fail-closed `ADMIN_API_TOKEN` boundary for ASTI administrative routes
  and all TESTBOX runtime API endpoints.
- Authorization failures emit application-log warnings without token values.
- Telegram external execution is disabled by default unless an explicit release
  flag is enabled after governance approval.
- META-QMS redacts obvious email and telephone patterns in proposals.
- Runtime tests use isolated temporary stores.
- Raw runtime state and deployment secret files are excluded from Git.

## Open Risks

| Priority | Risk | Current State | Required Closure Evidence |
| --- | --- | --- | --- |
| P0 | External execution release | Frozen locally; no release approval granted. | Allowlist, dry-run, revoke switch, rollback plan, secrets review and human decision. |
| P1 | Durable security audit | Denied auth attempts are application-logged, not stored in a hardened immutable security audit sink. | Protected append-only audit store and retention/access review. |
| P1 | Runtime persistence | JSON/JSONL single-process stores are not suitable for resilient production deployment. | Transactional PostgreSQL/audit architecture with tested recovery. |
| P1 | Rate limiting / abuse control | No production-grade API rate limiting confirmed. | Gateway or middleware limits, abuse monitoring and automated tests. |
| P1 | Secrets operations | `.env` is local and ignored; no managed production secret service verified. | Deployment secret manager/config procedure and rotation verification. |
| P1 | Repository integration review | Controlled publication targets `origin` (`astrebhub/astreb-os`) because the configured `jazekker` remote was not available to the connected GitHub context. | Human review before merging this release branch into any canonical base. |
| P2 | Webhook exposure | Telegram webhook is secret/owner protected but is outside the `/api/asti/*` naming scheme. | Deployment ingress decision, rate control and security test evidence. |
| P2 | CI security assurance | Workflow has been updated locally but has not yet run remotely for this state. | Published branch with passing CI including dependency scan. |

## Secret Policy

- Real credentials must never be committed.
- `.env` and `.env.production` are ignored secret-bearing files.
- `.env.example` contains placeholders only.
- Test-only fixed tokens are permitted only inside tests and must not represent
  deployment credentials.

## Audit Integrity Assessment

Local audit events are timestamped JSONL and raw state is excluded from Git.
This supports local governed validation, but it is not a production-grade
immutable audit database. Production readiness remains blocked until durable
append-only storage, access control, retention and recovery are implemented.

## External Execution Gate

`ASTI_EXTERNAL_EXECUTION_ENABLED` must remain disabled for a read-only
governed preview. Any future enablement requires a separate human governance
decision and documented rollback/revocation controls.
