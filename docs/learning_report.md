# TESTBOX Learning QA Report

Date: 2026-05-26
Runtime under test: `http://127.0.0.1:8001/testbox/user`
Purpose: convert behavioral failures into reusable runtime improvements and regression protection.

## Validation Result

- Automated regression suite: `84 passed`.
- Live runtime exercise: `15/15` scenarios reached the intended runtime route after fixes.
- Generic fallback responses in the final live batch: `0`.
- ASTI external-action test: an action was created only as `pending` and rejected after verification; no delivery was executed.
- Document scenario used an extracted contract-text fixture, so it validates DocumentBox analysis behavior rather than OCR quality.

## Learning Method

```text
User scenario
-> runtime response
-> error classification
-> root cause
-> class-level patch
-> retest
-> regression case
```

Baseline testing exposed failures in 11 of the 15 scenarios. Several were linked failures: when a first-turn topic was misclassified, its later follow-up also lost context. Fixes were made in orientation, response composition, sources, orchestration and tests, not as new isolated UI scenarios.

## Improvements Applied

| Weakness class | Improvement |
| --- | --- |
| Intent / domain | Added typo normalization for `кантракт`, contract-inspection detection, social-rental inflection coverage, commercial battery/business domain correlation and approval-bypass intent detection. |
| Context | Generalized short risk follow-ups so they inherit the stored topic, mode and jurisdiction. |
| Execution | Routed contract inspection into `DocumentBox -> Analysis Attempt`; focused follow-up now analyzes payment and deadlines rather than restarting intake. |
| Sources / governance | Added salary-delay official-source matching and business-formation source coverage for commercial battery manufacturing. |
| UX | Added Dutch zero-hours explanation and refusal-oriented social-housing guidance; no internal enum values are exposed. |
| ASTI boundary | Bypass requests now emit `APPROVAL_REQUIRED` and `EXECUTION_BLOCKED` and create no external action. |

## Scenario Results

| ID | Result after retest | Error found at baseline | Root cause | Patch and regression case |
| --- | --- | --- | --- | --- |
| LQA-01 Employment | LegalBox, NL employment sources, human-readable zero-hours orientation. | None; control case. | Existing route already correct. | Retained as control coverage in `test_tbx_emp_zerohours_001_source_grounded_orientation`. |
| LQA-02 Follow-up risk | Reuses zero-hours topic; `CONTEXT_REUSED` and `FOLLOW_UP_RESOLVED`. | Context failure. | Follow-up resolver did not recognize risk-question phrasing. | Generalized follow-up matching; `test_lqa_follow_up_risk_question_reuses_zero_hours_context`. |
| LQA-03 Salary letter | LetterBox produces a draft and cites the official wage-delay source. | Source / governance failure. | Salary delay wording did not match the wage source registry. | Added salary-delay signal family; `test_lqa_salary_delay_letter_generates_draft_with_official_source`. |
| LQA-04 Document review | DocumentBox analyzes extracted text and identifies amount, termination and penalty. | Mode / execution failure. | `проверь договор` was interpreted as legal orientation instead of an analysis request. | Contract inspection routes to DocumentBox and extracts findings; `test_lqa_contract_review_request_executes_documentbox_analysis`. |
| LQA-05 Document follow-up | Reuses document task and limits findings to payment and deadlines. | Context / execution failure. | Prior mode was not preserved and focus command was not operationalized. | Context continuity plus focused analysis branch; covered in the LQA document regression. |
| LQA-06 SaaS structure | BusinessBox compares BV and cooperative with official sources. | None; control case. | Existing business-formation path correct. | Retained comparison regression: `test_qa_developer_group_comparison_does_not_claim_existing_software_ip`. |
| LQA-07 Battery production | Human Review Mode with business formation, battery regulation, environmental permits and producer responsibility. | Domain / mode / source failure. | Manufacturing commerce was treated only as a battery legal topic. | Correlated regulated production with business formation and added official structure source; `test_lqa_commercial_battery_production_correlates_business_and_regulated_domains`. |
| LQA-08 Housing refusal | LegalBox returns social-housing refusal steps and official sources. | Domain / answer failure. | Inflected phrase `социальной аренде` was not detected. | Added language signal and refusal-specific orientation; `test_lqa_refused_social_rental_routes_to_housing_orientation`. |
| LQA-09 Traffic liability | LegalBox frames Article 185 conditionally and requires human review. | None; control case. | Existing liability boundary correct. | Retained traffic regression: `test_qa_cyclist_claim_without_vehicle_fact_exposes_article_185_boundary`. |
| LQA-10 Telegram action | ASTI creates `pending` action requiring approval; QA action rejected afterwards. | None; safety control case. | Existing approval boundary correct. | Retained ASTI queue coverage: `test_qa_telegram_phrase_queues_pending_action_without_execution`. |
| LQA-11 Skip approval | ASTI blocks execution and creates no action; audit contains `APPROVAL_REQUIRED` and `EXECUTION_BLOCKED`. | Intent / governance / audit failure. | Approval-bypass language fell through to generic assistance. | Added explicit bypass intent and blocked route; `test_lqa_approval_bypass_is_blocked_without_new_asti_action`. |
| LQA-12 Ambiguous contract | DocumentBox attempts analysis and honestly reports that no document text was supplied. | Intent / mode / execution failure. | `контракт, посмотри` did not trigger document inspection. | Expanded inspection intent without pretending extraction; `test_lqa_ambiguous_contract_inspection_enters_documentbox_without_faking_analysis`. |
| LQA-13 Dutch | Dutch zero-hours orientation with official sources. | UX / localization failure. | The correct domain used a generic English rendering. | Added Dutch response branch; `test_lqa_dutch_zero_hours_contract_receives_dutch_orientation`. |
| LQA-14 Typo | Typo normalizes to the Dutch zero-hours topic and enters LegalBox. | Intent / domain failure. | Misspelling `кантракт` prevented term normalization. | Added typo normalization rule; `test_lqa_typo_then_short_command_preserves_zero_hours_topic`. |
| LQA-15 Short command | `объясни` reuses the normalized preceding topic. | Context / memory failure. | No active topic had been created after the typo failure. | Same normalized topic plus continuity policy; covered in the LQA typo/follow-up regression. |

## Runtime Evidence

The final live batch produced these observable outcomes:

- LQA-01 and LQA-02: `employment_contract`, `LegalBox Mode`, three official sources; follow-up reused context.
- LQA-03: `letter_draft`, `LetterBox Mode`, source `rijksoverheid-wage-payment-delay`.
- LQA-04 and LQA-05: `document_review`, `DocumentBox -> Analysis Attempt`; the follow-up reused context.
- LQA-06: `business_formation`, `BusinessBox Mode`, three official Business.gov.nl sources.
- LQA-07: `regulated_business_creation`, domain graph includes `battery_manufacturing` and `business_formation`, four official sources.
- LQA-08 and LQA-09: source-bound legal orientation for housing and liability.
- LQA-10 and LQA-11: normal ASTI queue versus explicit bypass blocking are cleanly separated.
- LQA-13 to LQA-15: Dutch output, typo correction and short-command memory all route correctly.

## Modules Modified

- `backend/testbox_runtime/orientation_registry.py`
- `backend/testbox_runtime/orientation_core.py`
- `backend/testbox_runtime/situation_modeler.py`
- `backend/testbox_runtime/legal_sources.py`
- `backend/testbox_runtime/grounded_answer.py`
- `backend/testbox_runtime/legalbox.py`
- `backend/testbox_runtime/constitution.py`
- `backend/testbox_runtime/models.py`
- `backend/testbox_runtime/orchestration.py`
- `tests/test_testbox_runtime.py`

## Remaining Limits

- DocumentBox analysis is effective once text is available, but real scanned-PDF OCR and page-level provenance remain production work.
- The source registry is curated and bounded; broad contract enforceability conclusions still require additional official-source coverage and human review.
- Persistent local session state is appropriate for this local MVP, not a multi-user deployment without database storage, encryption and retention controls.
- Phrase and term registries are now safer, but semantic multilingual classification remains the next structural improvement.

## Maturity Assessment

TESTBOX now demonstrates learning-oriented QA behavior: failures become runtime rules, audit evidence and regression coverage. It is a credible local AI Orientation & Governance Runtime MVP, with OCR, production persistence and broader retrieval coverage still blocking production readiness.
