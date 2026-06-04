# ASTI Execution Boundary Report: v0.3

Date: 2026-05-27
Scope: ASTI execution boundary for read-only governed production preview

## Boundary Decision

External execution remains disabled. The read-only production preview must not
send Telegram, WhatsApp, email or any other external action.

## Implemented Controls

| Control | Status | Evidence |
| --- | --- | --- |
| Queue before action | Implemented | `POST /asti/task` creates `pending` action. |
| Human approval required | Implemented | `execute` rejects non-approved actions. |
| Rejection terminality | Implemented | Rejected actions cannot execute. |
| Duplicate execution protection | Implemented | Executed/in-progress actions emit duplicate/block events. |
| External Telegram freeze | Implemented | Missing release flag blocks Telegram executor with `external_execution_frozen`. |
| Production-preview config deny | Implemented | Prod startup rejects `ASTI_EXTERNAL_EXECUTION_ENABLED=true`. |
| Audit logging | Implemented locally | ASTI writes JSONL lifecycle events. |
| Webhook secret and owner check | Implemented | Telegram webhook requires secret and configured owner chat. |
| Webhook replay protection | Implemented locally | Duplicate Telegram update IDs are ignored and audited. |

## Dry-Run And Non-External Behavior

Local non-external executors exist:

- `local_report`
- `no_op`

These support local validation without external side effects. A formal
production dry-run mode for all future external channels remains a required
future control before any executor release.

## Current Execution Rules

```text
pending -> approved -> execution_in_progress -> executed
pending -> rejected
```

For the production preview:

```text
approved Telegram action -> execution_blocked(external_execution_frozen)
```

In `AI_CABINET_ENV=prod`, the runtime refuses startup if
`ASTI_EXTERNAL_EXECUTION_ENABLED=true`, so the preview cannot accidentally
start with external execution enabled.

## Required Before Any Future External Execution Gate

- separate human governance decision;
- executor allowlist;
- dry-run evidence;
- revocation switch;
- rollback strategy;
- abuse detection and rate limiting;
- managed secrets;
- durable execution audit;
- operator identity and approval UI verification.

## Decision

ASTI is acceptable as a controlled local execution boundary and explanation
surface. It is not approved for live external delivery.
