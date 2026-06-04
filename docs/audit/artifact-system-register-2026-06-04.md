# Artifact System Register: 2026-06-04

Purpose: identify and systematize ASTREB / JAZEKKER / TESTBOX artifacts against
mission, governance and release-readiness boundaries.

## Repository And Branches

| Artifact | Status | Treatment |
| --- | --- | --- |
| Root repo `ai_cabinet_mvp` | Canonical workspace | Main working repository under audit. |
| Branch `codex/testbox-public-release` | Active | Current working branch; contains v0.4/v0.5 public-demo work and dirty local changes. |
| Branch `release/local-governed-mvp-v0.3` | Reference / previous gate | Published governed production-preview gate artifact, not production-ready. |
| Nested repo `distribution/Разработка_ТБ_v0.5` | Archived/generated unless selected | Separate Git repo inside distribution package; do not mix with root canonical source. |

## Product Artifacts

| Artifact | Status | Mission Fit | Notes |
| --- | --- | --- | --- |
| JAZEKKER Foundation surfaces | Reference / ecosystem | Orientation interface | Not the current branch's primary release focus. |
| TESTBOX Agent/Control/Observe UI | Active | Mission-oriented runtime and governance visibility | Current public demo focus. |
| Mission Layer | Active | Organizes user work into auditable missions | Must not become execution authority. |
| QMS Quality Layer | Active | Continuous improvement and deviation learning | Human decision required for evolution. |
| META-QMS | Active | Reviewed evolution loop | No autonomous mutation. |
| ASTI | Active controlled boundary | Responsible execution boundary | External execution remains frozen. |
| AI Cabinet modules | Experimental | Governance substrate seeds | Need integration/security decision before canonical authority. |

## Documentation Artifacts

| Path | Status | Treatment |
| --- | --- | --- |
| `README.md` | Active | Public-demo entrypoint for TESTBOX branch; keep non-production language. |
| `docs/testbox-v0.4-mission-oriented-agent-runtime.md` | Active | Current product framing. |
| `docs/testbox-v0.5-production-foundation.md` | Experimental/reference | Foundation contracts, not deployment evidence. |
| `docs/release/testbox-v0.3-governance-runtime-release.md` | Reference | Previous public demo release candidate. |
| `docs/release/*v0.3*` | Reference / previous gate | Security and production-preview gate evidence from May 2026. |
| `docs/strategy/jazekker/*` | Reference | JAZEKKER product strategy; not current TESTBOX release scope. |
| `docs/testbox-v0.1-*` | Archived | Historical evidence only. |
| `docs/testbox-v0.2-*` | Reference | Incremental architecture history. |

## Runtime / Storage Artifacts

| Path | Status | Treatment |
| --- | --- | --- |
| `audit/*.jsonl`, `audit/*.json` | Archived/runtime | Raw local state; keep ignored. |
| `audit/qms_learning_records.jsonl` | Archived/runtime | Raw local learning state; now ignored. |
| `action_queue/*.json` | Archived/runtime | Raw local ASTI queue; keep ignored. |
| `local_runtime/*` | Experimental/runtime | Local model/vector runtime staging; not public evidence. |
| `memory/*` | Experimental/runtime | Local memory staging; do not publish as authoritative memory. |

## Generated / Distribution Artifacts

| Path | Status | Treatment |
| --- | --- | --- |
| `distribution/TESTBOX_PORTABLE_v0.5/` | Generated/archive | Ignore as generated package copy. |
| `distribution/Разработка_ТБ_v0.5/` | Generated/archive with nested repo | Ignore from root repo; manage separately if needed. |
| `distribution/*.zip` | Generated archive | Already ignored. |
| `portable/*`, `development/*` | Active helper candidates | Include only after review; verify no secrets and correct claims. |

## Governance Artifacts

| Path | Status | Treatment |
| --- | --- | --- |
| `governance/approvals/*` | Active / pending review | Approval policies; should become canonical only after human decision. |
| `governance/source-register/*` | Active / pending review | Source policy; align with retrieval registry and JAZEKKER trust model. |
| `governance/testbox-starter-kit/*` | Reference | Source governance package retained for traceability. |
| `policies.yaml` | Active / pending review | Needs mapping to runtime policy engine before canonical claim. |

## Artifact Rules Going Forward

1. Source of truth lives in root repo source/docs, not generated distribution
   folders.
2. Raw runtime stores never become release evidence.
3. v0.5 is a production-foundation contract until tests and deployment evidence
   prove otherwise.
4. JAZEKKER strategy remains ecosystem context unless a JAZEKKER release scope
   is explicitly opened.
5. External execution claims require separate ASTI gate evidence.
