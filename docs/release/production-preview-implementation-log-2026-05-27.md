# Production Preview Implementation Log: 2026-05-27

Branch: `release/local-governed-mvp-v0.3`
Objective: move the governed local MVP toward a read-only governed production
preview without enabling autonomous or external execution.

## Changed Files

| File | Purpose |
| --- | --- |
| `.github/workflows/ci.yml` | Adds explicit read-only production-preview config validation. |
| `.env.example` | Documents that external execution must remain false for preview. |
| `backend/runtime_auth.py` | Fails production-preview startup if external execution is enabled. |
| `tests/test_asti_telegram_approval.py` | Adds regression test for production-preview execution-deny config. |
| `README.md` | Clarifies that enabling real external execution requires a future release line. |
| `SECURITY.md` | Clarifies production-preview startup deny behavior. |
| `docs/release/repository-classification-report.md` | Classifies canonical, active, reference, archived and experimental artifacts. |
| `docs/release/system-inventory-v0.3.md` | Inventories routes, APIs, stores, env vars, ports and dependencies. |
| `docs/release/trust-boundary-map.md` | Maps public/UI/runtime/ASTI/external trust zones. |
| `docs/release/runtime-state-model.md` | Defines canonical lifecycle states and forbidden transitions. |
| `docs/release/security-hardening-report.md` | Records implemented security controls and open risks. |
| `docs/release/asti-execution-boundary-report.md` | Records ASTI freeze, approval and audit boundary. |
| `docs/release/incident-response-plan.md` | Defines incident handling for preview risks. |
| `docs/release/public-claims-policy.md` | Defines allowed and prohibited public claims. |
| `docs/release/deployment-checklist.md` | Marks new documentation and config-validation controls. |

## Architectural Reasoning

The implementation deliberately keeps the preview read-only. The code change is
small: it closes the highest-risk configuration gap by refusing production-mode
startup when `ASTI_EXTERNAL_EXECUTION_ENABLED=true`. This preserves local test
ability for ASTI mechanics while preventing the preview runtime from starting
with live external delivery enabled.

The documentation additions do not redesign the system. They stabilize
governance around the existing architecture: public orientation surfaces,
privileged TESTBOX runtime, ASTI execution boundary, and META-QMS human-reviewed
proposal loop.

## Status Matrix

| Requirement | Status | Notes |
| --- | --- | --- |
| Repository stabilization | Documented | Classification report created; merge-base reconciliation remains open. |
| System inventory | Documented | Routes, APIs, env vars, stores, integrations and ports listed. |
| Trust boundary map | Documented | Auth, approval, audit, secret and human override zones listed. |
| Runtime state model | Documented | Forbidden transitions and rollback rules included. |
| Security hardening | Implemented and documented | Production-preview execution-deny guard added. |
| ASTI boundary | Implemented and documented | External execution remains disabled; prod preview rejects enabled flag. |
| CI/CD | Implemented in workflow | Remote CI pass still requires verification. |
| Incident response | Documented | Preview incident playbooks created. |
| Public claims policy | Documented | Prohibited claims explicitly listed. |

## Verification

Completed in this cycle:

- `git diff --check` passed with no whitespace errors.
- Static secret-pattern scan over non-test/non-doc source returned no matches.
- New regression test was added for production-preview external execution deny.

Not completed locally in this cycle:

- Full pytest/ruff rerun is blocked because the local venv points to a missing
  Windows Store Python 3.13 executable. Prior release-gate evidence remains
  `102 passed in 12.71s`, but this new commit requires restored local Python or
  remote CI for fresh automated verification.

## Unresolved Risks

| Priority | Risk | Required Closure |
| --- | --- | --- |
| P0 | Canonical integration base is unresolved. | Human decision and scoped PR. |
| P1 | Remote CI evidence is missing for this update. | Passing GitHub Actions run. |
| P1 | Durable audit/security storage is not implemented. | Protected append-only store. |
| P1 | Rate limiting is not implemented. | Gateway or middleware limits and tests. |
| P1 | Managed production secrets are not configured. | Secret manager and rotation procedure. |
| P2 | ASTI route naming remains `/asti/*`, not `/api/asti/*`. | Versioned ingress decision. |
