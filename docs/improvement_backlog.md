# TESTBOX Improvement Backlog

Date: 2026-05-26
Basis: Learning QA batch `LQA-01` to `LQA-15`.

## Completed In This Cycle

| Area | Improvement | Evidence |
| --- | --- | --- |
| Follow-up continuity | Risk follow-ups reuse employment topic and mode. | LQA-02; `CONTEXT_REUSED`, `FOLLOW_UP_RESOLVED`. |
| LetterBox sources | Salary-delay drafting retrieves the official wage source. | LQA-03; `rijksoverheid-wage-payment-delay`. |
| DocumentBox execution | Contract-review wording enters active analysis; focused follow-up filters the output. | LQA-04/LQA-05; DocumentBox regressions. |
| Regulated business | Battery sales/manufacturing correlates business formation with EU product and environmental regulation. | LQA-07; four retrieved official sources. |
| Housing language | Social-rental refusal inflection routes correctly and receives practical refusal orientation. | LQA-08. |
| ASTI safety | Approval bypass is explicitly blocked and audited without action creation. | LQA-11; `EXECUTION_BLOCKED`. |
| Multilingual/typo handling | Dutch answer rendering and `кантракт` normalization are protected by tests. | LQA-13/LQA-14/LQA-15. |

## Remaining Priority Work

| Priority | Work item | Why it matters | Acceptance condition |
| --- | --- | --- | --- |
| P0 | Real OCR and page-level document provenance. | DocumentBox cannot reliably analyze scans or photos from actual user uploads. | PDF/image ingestion produces page-level text, confidence, provenance and honest failure reasons; QA includes scanned documents. |
| P0 | Production session and audit persistence. | Local JSON storage is not adequate for concurrent users, secure retention or operational recovery. | PostgreSQL-backed session/audit data, encrypted sensitive fields, retention rules and concurrency tests. |
| P1 | Broader official retrieval coverage for contracts and administrative decisions. | DocumentBox can find clauses but cannot ground all legal consequences in official sources. | Contract/refusal orientations retrieve jurisdiction-specific official sources or clearly scoped human review. |
| P1 | Semantic multilingual orientation layer. | Registry matching still requires maintenance for new wording and spelling variation. | Evaluated RU/NL/EN corpus demonstrates stable domain/mode classification across paraphrases without new scenario templates. |
| P1 | ASTI conversational action binding. | A safe later command such as "approve that draft" needs unambiguous reference to one pending action. | Session-bound pending-action selection, confirmation UI and audit evidence; never execute ambiguous actions. |
| P2 | Automated learning-QA evidence exporter. | Current report assembly is deliberate but partly manual. | Runner records expected/actual/error/patch/retest/audit evidence and exports report artifacts without external action side effects. |
| P2 | Response localization coverage. | Some future modes may regress to English or technical phrasing. | Snapshot/behavior checks for Russian, Dutch and English human-facing outputs in every active mode. |

## Design Rule

New work should improve orientation, execution or governance boundaries across a class of requests. Avoid adding one-off scenarios whose only purpose is to make a single prompt pass.
