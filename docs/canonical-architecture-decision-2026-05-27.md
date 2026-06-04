# Canonical Architecture Decision: Security Baseline

Date: 2026-05-27
Decision status: Approved for controlled local validation
Decision owner: Human governance review required for external release
Working branch: `codex/meta-qms-security-baseline`

## Decision

The canonical integrated architecture is:

```text
JAZEKKER   = public orientation interface
AI Cabinet = constitutional, policy and authorization authority
TESTBOX    = observable governed runtime and operator surface
ASTI       = approval-gated execution boundary
META-QMS   = reviewed quality, learning and evolution loop
```

`docs/testbox-v0.3-situational-orientation-architecture.md` is the active
architecture blueprint. Earlier TESTBOX descriptions remain supporting
reference or historical evidence as classified in
`docs/prototype-lifecycle-register.md`.

## Canonical Branch Rule

`codex/meta-qms-security-baseline` is the review branch for the integrated
AI Cabinet + JAZEKKER + TESTBOX + ASTI + META-QMS security baseline. It may be
merged into the governed product branch only after human review of this
decision, secrets/configuration verification and approval of external-release
controls.

## Mandatory Controls

- Real Telegram delivery is frozen unless
  `ASTI_EXTERNAL_EXECUTION_ENABLED=true` is explicitly released.
- ASTI administrative endpoints and all TESTBOX runtime API endpoints require
  the shared `X-AI-Cabinet-Admin-Token` control.
- Missing `ADMIN_API_TOKEN` disables privileged endpoints; production startup
  also fails closed.
- Raw runtime stores are local-only and excluded from Git.
- Repository audit evidence is limited to anonymized reports.
- Runtime tests must use isolated `tmp_path` stores.

## Release Gate

External execution remains prohibited until a human governance decision records
closure of the auth-bypass finding, verifies deployment secrets and approves a
deliberate change of `ASTI_EXTERNAL_EXECUTION_ENABLED` from its frozen state.
