# Runtime State Model: ASTREB / JAZEKKER v0.3

Date: 2026-05-27
Scope: canonical lifecycle states for governed preview behavior

## Orientation And Runtime Lifecycle

| State | Meaning | Transition Authority | Required Audit | Rollback / Correction |
| --- | --- | --- | --- | --- |
| `captured` | User/operator input is received. | Runtime API after auth where required. | `MESSAGE_RECEIVED` / `USER_MESSAGE_RECEIVED`. | Mark as ignored or superseded; do not delete audit. |
| `interpreted` | Intent, language, domain and situation are derived. | TESTBOX runtime. | `INTENT_DETECTED`, `DOMAIN_GRAPH_CREATED`, `SITUATION_MODEL_CREATED`. | Publish correction event or reprocess under new session. |
| `routed` | Runtime selects role/workflow path. | AI Cabinet / TESTBOX policy logic. | `ROLE_ASSIGNMENT_SELECTED`, `ROUTE_SELECTED`. | Re-route with new audit event. |
| `review_required` | Human review is required. | Policy engine or runtime risk logic. | `HUMAN_REVIEW_REQUIRED`. | Human may approve, deny, or request revision. |
| `approved` | Human approved a bounded step. | Human operator/governance reviewer. | `APPROVAL_GRANTED` or ASTI `approved`. | Revoke by separate rejection/incident record; do not erase original approval. |
| `rejected` | Human rejected a bounded step. | Human operator/governance reviewer. | `APPROVAL_DENIED` or ASTI `rejected`. | New action/proposal required; no direct execution. |
| `queued` | ASTI action exists but is not executed. | ASTI after governed creation. | ASTI `created`. | Reject or archive; no external delivery. |
| `execution_in_progress` | Executor has been called after approval. | ASTI service only. | `execution_started`. | Manual reconciliation after failure; no automatic retry in MVP. |
| `executed` | Local/no-op or approved executor completed. | ASTI service only. | `executed`. | Compensating audit and rollback plan required. |
| `audited` | Evidence is persisted. | Runtime/audit store append. | JSONL event row with timestamp. | Append correction; do not mutate previous event. |
| `archived` | State retained for history/reference. | Human governance/auditor. | Classification or archive note. | Restore only through new review decision. |

## ASTI Action Lifecycle

```text
pending -> approved -> execution_in_progress -> executed
pending -> rejected
pending/approved/rejected/executed -> execution_blocked on invalid execute attempt
```

Forbidden transitions:

- `pending -> executed`
- `rejected -> executed`
- `approved -> executed` without `execution_started`
- `executed -> pending`
- any state -> external Telegram delivery in production preview
- any state -> autonomous approval

## META-QMS Proposal Lifecycle

```text
review_required -> approved_for_implementation
review_required -> rejected
```

Forbidden transitions:

- `approved_for_implementation -> implemented` inside META-QMS;
- `review_required -> external execution`;
- `approved_for_implementation -> code mutation`;
- proposal creation without audit events;
- proposal storage with obvious unredacted email or phone patterns.

## Required Approval Roles

| Transition | Required Role |
| --- | --- |
| Runtime high-risk review | Human operator or governance reviewer. |
| ASTI approval/rejection | Strategic owner, runtime operator or authorized executor depending on policy. |
| META-QMS decision | Governance reviewer. |
| Production deployment | Strategic owner plus security reviewer. |
| External execution enablement | Separate governance decision; not available in read-only preview. |

## Rollback Rules

- Audit records are append-only; corrections are new events.
- Failed external execution remains `execution_in_progress` for manual
  reconciliation and cannot be retried blindly.
- Production-preview deployment rollback must disable runtime ingress first,
  revoke tokens second, and preserve audit evidence third.
- Any accidental public claim must be corrected in public-facing documentation
  and recorded as a governance deviation.
