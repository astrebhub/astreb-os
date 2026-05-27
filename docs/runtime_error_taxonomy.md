# TESTBOX Runtime Error Taxonomy

Date: 2026-05-26

This taxonomy is used to turn observed behavior failures into general runtime improvements. A patch is acceptable only when it improves a behavior class and adds regression protection.

## Evaluation Loop

```text
Observe response
-> identify user harm
-> classify error
-> find runtime cause
-> patch reusable rule or boundary
-> retest original case
-> test a neighboring formulation
-> retain regression evidence
```

## Error Classes

| Type | Failure signal | Required diagnosis | General patch direction | Required evidence |
| --- | --- | --- | --- | --- |
| Intent failure | Requested task becomes generic chat or wrong operation. | Was the goal omitted, confused with topic, or missed due to phrasing/typo? | Improve normalized intent extraction and operational goal recognition. | Correct intent and route for original and equivalent wording. |
| Context failure | Short follow-up restarts the conversation. | Was active topic/task stored and was follow-up language recognized? | Reuse prior topic, intent, mode and jurisdiction for referential follow-ups. | `CONTEXT_REUSED` and `FOLLOW_UP_RESOLVED`. |
| Domain failure | Regulated matter is classified `general` or placed in the wrong domain graph. | Which relevant signals or correlations were absent? | Extend domain correlation or semantic classification, not one answer template. | Expected primary domain and domain graph. |
| Mode failure | LegalBox is chosen for drafting/review, or chat replaces ASTI/BusinessBox. | Did the action verb fail to override topical classification? | Select mode from user goal plus domain, with execution-first precedence. | Expected mode and human-readable route. |
| Execution failure | Runtime explains what to do instead of attempting the requested task. | Was evidence available and did analysis/drafting begin? | Apply `ACTIVE_TASK_EXECUTION_POLICY`; report findings before limitations. | Execution-attempt event and concrete output. |
| Governance failure | Unsafe action proceeds, regulated answer lacks controls, or warning text replaces help. | Did policy under-trigger or overwhelm useful output? | Constrain execution and source requirements while preserving orientation. | Policy event, approval state and usable response. |
| Source failure | Legal/business statement lacks official grounding or source mismatch triggers needless review. | Which source topic/phrase/coverage was missing? | Expand official source registry or state bounded limitation honestly. | `SOURCE_REQUIRED`, retrieval result and referenced source IDs. |
| UX failure | Internal enums, wrong language or mechanical fallback are shown. | Is the response renderer leaking runtime detail or ignoring user language? | Human-facing renderer and localization branch; never suppress audit internally. | No enum leakage or generic fallback; requested language rendered. |
| Audit failure | Operator cannot explain why a route or block occurred. | Which decision boundary lacks an event? | Emit decision events with reasons and safe payload fields. | Audit contains the route/policy/action event. |
| Memory failure | Active task disappears across turns or restarts. | Was state persisted, redacted and reloaded correctly? | Store bounded orientation state; redact PII; reuse only relevant context. | Persistent-context and follow-up regression tests. |

## Severity Guidance

| Priority | Meaning | Examples |
| --- | --- | --- |
| P0 | Can perform or imply unsafe execution, or loses legally material safety controls. | Approval bypass executes; unsupported legal conclusion. |
| P1 | Makes orientation substantially wrong or unusable. | Salary letter has no source; document review becomes checklist; regulated business becomes general. |
| P2 | Degrades continuity or clarity while preserving safety. | Follow-up restarts; Dutch answer rendered in English. |

## Regression Standard

A regression case records:

- scenario and user goal;
- expected intent, domain graph, mode and governance;
- baseline failure type and root cause;
- generalized patch;
- retest result;
- audit events that make the behavior explainable.

Do not accept a patch that only recognizes one sentence while leaving the same error type present for adjacent requests.
