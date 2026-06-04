# Security Hardening Report: ASTREB / JAZEKKER v0.3

Date: 2026-05-27
Scope: local MVP to read-only governed production preview hardening

## Summary

Security posture is improved for a controlled preview, but production approval
is not granted. The system is acceptable for continued review only if external
execution remains disabled and privileged runtime access remains protected.

## Verified Controls

| Control | Status | Evidence |
| --- | --- | --- |
| Fail-closed privileged endpoints | Implemented | `backend/runtime_auth.py`; ASTI and TESTBOX tests reject unauthenticated calls. |
| Production token requirement | Implemented | `AI_CABINET_ENV=prod` fails startup without `ADMIN_API_TOKEN`. |
| Production-preview execution deny | Implemented; regression test added | `AI_CABINET_ENV=prod` fails startup if `ASTI_EXTERNAL_EXECUTION_ENABLED=true`. |
| No Git-exposed secret stores | Implemented | `.env`, `.env.production`, `backend/.env`, key files ignored. |
| Raw runtime stores excluded | Implemented | `audit/`, `action_queue/`, local DB ignored. |
| Debug bypass scan | No active bypass found | Approval-bypass intent is blocked in tests; no allow-all runtime flag found. |
| PII redaction in META-QMS | Implemented for obvious patterns | Email/phone redaction tests pass. |
| Append-only local audit | Implemented locally | ASTI and TESTBOX write JSONL append events. |
| Isolated test storage | Implemented | Runtime tests use `tmp_path`. |

## CI/CD Hardening

The GitHub Actions pipeline now includes:

```text
install -> lint -> config validation -> tests -> dependency audit -> artifact build
```

Remote CI execution evidence is still required before a deployment gate can
close.

Local rerun note for this implementation cycle: the repository venv currently
points to a missing Windows Store Python 3.13 executable, so the newly added
test must be verified by restored local Python or remote CI before any
deployment decision.

## Secret And Credential Findings

- `.env.example` contains placeholders only.
- Test fixtures use fixed fake tokens; these are not deployment credentials.
- Telegram executor avoids returning token values in metadata.
- Failure tests assert secret values do not appear in responses or audit
  metadata.

## Audit Integrity

Current audit is append-only JSONL at local file level. This is sufficient for
local evidence and regression tests, but not sufficient for a production
preview exposed to multiple users or processes.

Required before production preview:

- protected append-only storage;
- retention policy;
- access controls;
- corruption detection/recovery;
- security-event sink for denied auth attempts.

## Open Security Risks

| Priority | Risk | Reason Not Closed |
| --- | --- | --- |
| P0 | External execution | Must remain frozen; no separate release decision exists. |
| P1 | Rate limiting | Not implemented in app or ingress. |
| P1 | Durable audit/session storage | Local JSON/JSONL only. |
| P1 | Managed secrets | No production secret manager configured. |
| P1 | Canonical base reconciliation | Initial PR diff is too broad for safe merge review. |
| P2 | Webhook ingress | Endpoint exists; should not be publicly exposed until ingress/rate-limit review. |

## Decision

Security baseline supports a read-only governed preview build path, not a
production release. Any future executor release must be handled as a separate
governance and security project.
