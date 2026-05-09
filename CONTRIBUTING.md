# Contributing To AI Cabinet

AI Cabinet follows one rule before all others: control before autonomy.

Contributions should preserve the governed execution pipeline:

```text
INPUT -> PII DETECTOR -> DATA CLASSIFIER -> POLICY ENGINE ->
TOKEN / COST GOVERNOR -> MODEL ROUTER -> PROVIDER ADAPTER ->
OUTPUT GUARD -> ACTION QUEUE -> AUDIT LOG -> MEMORY PROPOSAL
```

## Development Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn main:app --reload --port 8000
```

On Windows, use `.venv\Scripts\activate`.

## Pull Request Expectations

- Keep policy, routing, and action execution changes explicit.
- Add tests for PII, policy, routing, budget, output guard, or action behavior.
- Do not add real credentials, logs, local databases, model weights, or bundles.
- Do not bypass approvals for external actions.
- Document new plugins with a `manifest.yaml`.

## GitHub Manager Agent

The `github_manager_agent` may draft issues, PR plans, release notes, and CI
diagnostics. It may not push, merge, delete branches, publish releases, close
issues, alter repository settings, or handle secrets without an approval record.
