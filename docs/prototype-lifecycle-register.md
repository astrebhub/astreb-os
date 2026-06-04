# Prototype Lifecycle Register

Date: 2026-05-27
Authority: Canonical architecture decision for the security baseline

| Artifact or component | Status | Governance treatment |
| --- | --- | --- |
| AI Cabinet governance substrate | active | Canonical policy and authorization authority. |
| JAZEKKER public orientation surfaces | active | Canonical public interface; no privileged control authority. |
| TESTBOX v0.3 situational orientation runtime blueprint | active | Canonical runtime architecture target. |
| Current TESTBOX backend runtime and cockpit | active | Controlled local implementation under the security baseline. |
| ASTI approval and Telegram boundary | active | Active only with external execution frozen pending release decision. |
| ASTREB META-QMS Living Evolution Mode | active | Active reviewed improvement loop; no automatic system change. |
| TESTBOX v0.2 refactor architecture and implementation plan | reference | Useful incremental design record, superseded as canonical target by v0.3. |
| TESTBOX starter kit governance package | reference | Source governance package retained for mapping and traceability. |
| TESTBOX v0.1 acceptance report and operations guide | archived | Historical MVP evidence; not an active architecture or security claim. |
| Raw runtime audit stores and session state | archived | Local operational data only; excluded from Git and not governance evidence. |

## Living Update - 2026-06-04

Current working branch `codex/testbox-public-release` contains additional v0.4
and v0.5 artifacts. They extend the mission-oriented runtime story but do not
cancel the security/release boundaries above.

| Artifact or component | Status | Governance treatment |
| --- | --- | --- |
| TESTBOX v0.4 mission-oriented runtime | active | Active product framing: Agent, Control, Observe and Mission Layer. Must preserve approval, source and audit boundaries. |
| TESTBOX v0.5 production foundation contracts | experimental | Useful contracts for integrations, OCR, retrieval, storage and security registries. Not production deployment evidence. |
| `backend/testbox_runtime/mission_layer.py` | active | Mission projection layer; may organize work but cannot authorize execution. |
| `backend/testbox_runtime/quality_layer.py` | active | QMS quality/deviation/evolution loop; proposals remain human-reviewed. |
| `backend/testbox_runtime/*_registry.py` and `ocr_pipeline.py` | experimental | Production-foundation visibility contracts; require tests and deployment review before canonical release. |
| `backend/cabinet/*` | experimental | AI Cabinet module seeds; not yet canonical authority until integrated with policy/auth tests. |
| `docs/testbox-v0.4-*` | active/reference | Current mission-oriented product framing and presentation readiness. |
| `docs/testbox-v0.5-production-foundation.md` | experimental/reference | Production foundation roadmap; must not be described as production-ready. |
| `distribution/TESTBOX_PORTABLE_v0.5/` and `distribution/Разработка_ТБ_v0.5/` | archived/generated | Distribution copies, not canonical source. Keep generated folders out of root repository commits. |
| `audit/qms_learning_records.jsonl` | archived/runtime | Raw runtime learning store; excluded from Git. |

## Rule

An artifact marked `reference` may inform active work but must not override the
canonical architecture or current security controls. An artifact marked
`archived` is retained only for historical traceability and must not be used to
claim current runtime readiness.
