# ASTREB TESTBOX

AI Operations & Governance Console

TESTBOX is a QMS-driven governance runtime for observing, evaluating and improving AI-assisted processes.

It is not a chatbot, a dashboard, a workflow engine, or an autonomous agent. It is a public demo and developer baseline for:

- scenario execution
- governance skill evaluation
- deviation detection
- quality interventions
- audit events
- learning records
- human approval boundaries
- skill evolution proposals

## Public Demo Scope

This branch is prepared as:

```text
TESTBOX v0.1 public demo + developer release
```

Included:

- TESTBOX UI: `/testbox`
- TESTBOX user console: `/testbox/user`
- QMS runtime endpoints: `/api/testbox/runtime/qms/*`
- governed runtime message API: `/api/testbox/runtime/message`
- AI Cabinet demo shell as ecosystem context
- local-only audit and learning stores

Not included as full public modules:

- JAZEKKER product portal
- ASTI external execution fabric
- Telegram execution
- real external providers
- production secret management

JAZEKKER and ASTI may be mentioned as ecosystem context, but this release focuses on TESTBOX.

## Positioning

Recommended one-liner:

```text
ASTREB TESTBOX is a QMS-driven AI governance runtime for observing, correcting and improving AI-assisted processes.
```

Short public description:

```text
TESTBOX shows how AI-assisted workflows can be routed, governed, evaluated, audited and improved without giving AI autonomous authority.
```

## Architecture

```text
Scenario
-> Governance Skills
-> Runtime Processing
-> Quality Evaluation
-> Deviation Detection
-> Intervention
-> Learning Repository
-> Skill Evolution Proposal
-> Human Decision
```

Core backend modules:

```text
backend/main.py
backend/runtime_auth.py
backend/testbox_runtime/
  api.py
  legalbox.py
  orchestration.py
  orientation_core.py
  quality_layer.py
  meta_qms.py
  skills/
```

Core frontend:

```text
frontend/testbox.html
```

Supporting documentation:

```text
docs/testbox-qms-quality-runtime.md
docs/testbox-operations-guide.md
docs/testbox-v0.3-situational-orientation-architecture.md
docs/ai-runtime-constitution-v2.md
docs/publication-audit-testbox-v0.1.md
```

## Run Locally

Create a local environment and install dependencies:

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

Set a local admin token:

```bash
set ADMIN_API_TOKEN=replace-with-local-secret
```

Start the server:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/testbox
http://127.0.0.1:8000/testbox/user
```

For protected runtime calls from the browser, set the token in the current tab only:

```javascript
sessionStorage.setItem("astreb.admin_token", "<ADMIN_API_TOKEN>");
```

No token is embedded in the public HTML.

## API Surface

Protected TESTBOX endpoints:

```text
POST /api/testbox/runtime/message
GET  /api/testbox/runtime/events
GET  /api/testbox/runtime/roles
GET  /api/testbox/runtime/constitution
GET  /api/testbox/runtime/qms/skills
GET  /api/testbox/runtime/qms/scenarios
GET  /api/testbox/runtime/qms/learning
GET  /api/testbox/runtime/qms/meta
POST /api/testbox/runtime/qms/skills/{skill_id}/evolution
POST /api/testbox/runtime/qms/skills/evolution/{proposal_id}/decision
GET  /api/testbox/runtime/meta-qms
POST /api/testbox/runtime/meta-qms/assess
POST /api/testbox/runtime/meta-qms/proposals/{proposal_id}/decision
```

All protected endpoints require:

```text
X-AI-Cabinet-Admin-Token: <ADMIN_API_TOKEN>
```

## Safety Boundaries

This public demo must not:

- create legal effects
- approve decisions autonomously
- modify procedural deadlines
- dispatch official responses
- execute Telegram or other external actions
- store real credentials in Git
- publish local audit logs or memory

Human authority remains mandatory for approvals, skill evolution and any future external execution.

## Smoke Test Summary

Current local verification:

```text
111 passed
```

Covered areas:

- TESTBOX runtime routing
- QMS Quality Layer
- Scenario Layer
- Skill Evolution Layer
- Meta-QMS review loop
- privileged admin-token boundaries
- public UI token hygiene
- governed action safety boundaries

## Public Limitations

This is a public demo/developer release, not production infrastructure.

Known limitations:

- local JSON/JSONL storage only
- no managed production secret service
- no multi-worker transactional action claims
- no real external execution enabled
- no production identity provider
- no public hosting configuration yet
- no deployment approval granted

## Roadmap v0.2

- split TESTBOX into a smaller standalone package
- replace local stores with durable transactional storage
- add proper identity and scoped operator roles
- add a public read-only demo mode
- add deployment-grade secret management
- add CI publication gate
- add scenario authoring UI
- add anonymized demo audit dataset
- add more governance skills and skill version migration rules

## License

MIT. See `LICENSE`.
