# Production Scope: Read-Only Governed Preview

Date: 2026-05-27
Status: Proposed first-production scope; not deployed

## Target Positioning

The first production target is a `READ-ONLY GOVERNED PREVIEW`, not an
autonomous AI platform.

Approved wording for present status:

```text
Locally implemented and tested governed AI orientation prototype with
controlled execution boundaries and security-baseline governance controls.
```

## Allowed In A First Production Preview

### JAZEKKER

- Foundation homepage and orientation positioning;
- orientation objects and static interaction previews;
- local-orientation and research previews using approved non-sensitive data;
- AI Cabinet governance explanation;
- TESTBOX demonstration surface.

### TESTBOX

- static observation UI;
- controlled, authenticated demonstration scenarios only;
- explainability of routing, approval and audit principles;
- no live external execution.

### META-QMS

- quality review and proposal-flow visualization behind authorization;
- human approve/reject recording for controlled demo evidence;
- explicit `approved, not executed` messaging.

## Explicitly Excluded

- autonomous publishing;
- Telegram, WhatsApp or email delivery;
- autonomous distribution;
- self-modifying runtime;
- self-approved evolution proposals;
- unreviewed live data ingestion;
- raw session/audit data exposure;
- claims of a deployed civic AI infrastructure before validation.

## Architecture Classification

| Artifact Or Capability | Status | Basis |
| --- | --- | --- |
| `docs/testbox-v0.3-situational-orientation-architecture.md` | Canonical | Active target architecture for TESTBOX/ASTI development. |
| `docs/canonical-architecture-decision-2026-05-27.md` | Canonical | Current governed component and security boundary decision. |
| `release/local-governed-mvp-v0.3` | Canonical | Published review snapshot for this gate; not a production deployment or release approval. |
| JAZEKKER Foundation frontend surfaces | Active | Implemented locally and covered by tests. |
| TESTBOX backend runtime | Active | Implemented locally; authenticated demo/runtime only. |
| ASTI executor layer | Active | Implemented with external execution frozen by default. |
| META-QMS backend/UI flow | Active | Implemented locally; human-reviewed proposal loop. |
| `docs/testbox-v0.2-*` | Reference | Earlier incremental architecture and acceptance material. |
| `governance/testbox-starter-kit/` | Reference | Imported governance baseline/source package. |
| `_incoming/testbox_starter_kit/` | Archived | Duplicate intake copy; do not publish as canonical content. |
| `scripts/local_jazekker_server.mjs` | Experimental | Earlier frontend-only local helper; does not serve the current secured runtime scope and is excluded from the snapshot. |
| `docs/testbox-v0.1-*` | Archived | Historical MVP evidence only. |
| Raw `audit/` runtime state | Archived | Local operational state, not repository evidence. |
| Rate limiting and durable audit security sink | Experimental | Required production work not yet implemented. |

## Conflicts Requiring Resolution

| Conflict | Current Finding | Required Resolution |
| --- | --- | --- |
| API naming | Gate references `/api/asti/*`; implementation exposes `/asti/*`. | Choose stable versioned API convention before deployment. |
| Repository target | Both remotes are configured, but verification found `jazekker` unavailable while `origin` exposes `ai-cabinet-full`. This snapshot targets an isolated `origin` review branch. | Record human integration decision before any merge or production interpretation. |
| JSON/JSONL stores | Useful for local MVP but not durable production infrastructure. | Migrate to protected transactional/audit storage. |
| Historic documentation | v0.1/v0.2 materials remain useful but can be read as current. | Keep classified register and mark canonical docs in release communication. |
