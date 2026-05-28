# Publication Audit: TESTBOX v0.1 Public Demo

Branch:

```text
codex/testbox-public-release
```

Goal:

```text
Clean public TESTBOX v0.1 branch for demo, hackathon use and future backend integration.
```

## Scope

Included:

- TESTBOX UI and QMS runtime
- AI Cabinet demo shell/context
- QMS skill library
- Scenario, observation, learning and skill evolution endpoints
- local developer startup instructions

Excluded as full public modules:

- JAZEKKER as product portal
- ASTI as external execution fabric
- Telegram execution
- real external provider integrations

## Publication Checks

| Check | Status | Notes |
| --- | --- | --- |
| Secrets scan | Passed with notes | No real credentials found. Test fixtures contain fake tokens. |
| Hardcoded demo admin token | Corrected | Removed local demo-token value from public HTML. |
| Local paths | Passed with notes | Docs may reference local development context; README avoids local user paths. |
| Env files | Passed | `.env` and `backend/.env` are ignored. `.env.example` contains placeholders only. |
| Audit logs | Passed | Runtime audit logs are local-only and ignored. |
| Memory files | Passed with notes | Local memory directories are not part of the public README scope. |
| External execution | Passed | Direct public ASTI router removed from FastAPI surface; TESTBOX keeps human-governed stubs only. |
| README | Updated | Repositioned as TESTBOX public demo/developer release. |
| Smoke tests | Passed | `111 passed`. |

## Remaining Publication Notes

- This branch is not production-ready.
- Deployment is intentionally not performed.
- Public demo requires an operator-provided `ADMIN_API_TOKEN`.
- Before hosting, add managed secret storage and a read-only public demo mode.

## Human Authority Boundary

TESTBOX may propose, evaluate and record improvements.

TESTBOX may not:

- approve itself into production
- execute external actions
- publish official responses
- modify procedural deadlines
- create legal effects
