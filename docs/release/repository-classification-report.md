# Repository Classification Report: ASTREB / JAZEKKER v0.3

Date: 2026-05-27
Branch: `release/local-governed-mvp-v0.3`
Scope: repository stabilization for read-only governed production preview

## Executive Classification

This repository is a governed local MVP snapshot prepared for a read-only
production preview gate. It is not a production deployment and not an
autonomous execution platform.

| Category | Artifacts | Treatment |
| --- | --- | --- |
| Canonical | `docs/release/*`, `docs/canonical-architecture-decision-2026-05-27.md`, `docs/testbox-v0.3-situational-orientation-architecture.md`, `release/local-governed-mvp-v0.3` | Source of truth for v0.3 gate decisions and preview constraints. |
| Active | `backend/main.py`, `backend/runtime_auth.py`, `backend/testbox_runtime/*`, `backend/asti/*`, `frontend/foundation.*`, `frontend/jazekker-*.html`, `frontend/testbox.html`, current tests | Operational local governed runtime and read-only preview surfaces. |
| Reference | `docs/testbox-v0.2-*`, `docs/testbox-starter-kit-comparison.md`, `governance/testbox-starter-kit/*`, `docs/legalbox-for-testbox.md` | Informational design history; must not override v0.3 release boundaries. |
| Archived | `docs/testbox-v0.1-*`, `_incoming/testbox_starter_kit/`, raw `audit/`, raw `action_queue/`, local `backend/ai_cabinet.db` | Historical or local runtime state; not release evidence. |
| Experimental | durable audit/security sink design, rate limiting design, `scripts/local_jazekker_server.mjs`, ignored `backend/cabinet/__pycache__`, local `runtime/reports/*` | Do not present as production capability. |

## Detected Duplicate Or Conflicting Architecture

| Finding | Classification | Decision |
| --- | --- | --- |
| TESTBOX v0.1 operations guide and acceptance report describe browser-local/demo storage. | Archived | Retain as history only. |
| TESTBOX v0.2 plans describe backend migration and PostgreSQL targets. | Reference | Useful design lineage; v0.3 gate controls supersede release claims. |
| TESTBOX v0.3 architecture describes future PostgreSQL/Redis/WebSocket/worker stages. | Canonical target architecture | Not implemented as production infrastructure in this snapshot. |
| `governance/testbox-starter-kit/` and `_incoming/testbox_starter_kit/` duplicate starter-kit material. | Reference plus Archived duplicate | Use `governance/testbox-starter-kit/` only; `_incoming/` remains ignored. |
| `/api/asti/*` appears in planning language, while implementation exposes `/asti/*`. | Active conflict | API versioning decision required before production ingress. |
| `slakov/jazekker` remote is configured but inaccessible to current GitHub context. | Operational conflict | Current review publication target is `origin` / `astrebhub/astreb-os`. |

## Orphan And Runtime-State Findings

Ignored local artifacts were found and intentionally excluded from the release
snapshot:

- `backend/ai_cabinet.db`
- `audit/*.jsonl`
- `audit/*.json`
- `action_queue/*.json`
- `runtime/reports/*`
- `_incoming/testbox_starter_kit/`
- `scripts/local_jazekker_server.mjs`
- Python cache directories

These are local state or historical intake artifacts. They must not be used as
repository evidence, production data or deployment inputs.

## Deprecated Or Abandoned Runtime Logic

| Artifact | Status | Rationale |
| --- | --- | --- |
| `scripts/local_jazekker_server.mjs` | Experimental / excluded | Earlier frontend-only helper; does not expose the secured runtime boundaries. |
| `backend/cabinet/__pycache__` | Experimental / ignored | Bytecode remnants only; no source files are canonical in this snapshot. |
| TESTBOX browser-local audit behavior in `frontend/testbox.html` | Reference/demo behavior | Full runtime authority is now backend API plus audit JSONL; browser local storage is presentation-only. |
| Raw local runtime reports | Archived / ignored | Generated local operational records; not sanitized release evidence. |

## Stabilization Actions Completed

- Release branch published as a review snapshot.
- Raw runtime stores and secrets are ignored.
- `.env.example` uses placeholders only.
- Release documentation was centralized under `docs/release/`.
- CI workflow exists for lint, config validation, tests, dependency audit and
  artifact build.
- Production-preview configuration now rejects `AI_CABINET_ENV=prod` with
  `ASTI_EXTERNAL_EXECUTION_ENABLED=true`.

## Unresolved Risks

| Priority | Risk | Required Resolution |
| --- | --- | --- |
| P0 | Canonical merge base is unresolved; initial PR had a broad cross-lineage diff. | Human architecture decision and scoped integration branch. |
| P1 | Durable audit and session persistence remain local JSON/JSONL. | PostgreSQL or equivalent protected append-only storage. |
| P1 | Rate limiting is not implemented. | Gateway or middleware limits plus tests. |
| P1 | API naming for ASTI is not versioned under `/api/asti/*`. | Stable ingress convention before deployment. |
| P2 | Historic docs can still be misread as current. | Keep this classification report linked from release communication. |
