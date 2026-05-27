# ASTREB META-QMS Living Evolution Mode

Status: local operational foundation, human-governed.

## Purpose

ASTREB META-QMS adds a controlled continuous-improvement loop to the existing
TESTBOX runtime. It does not create a new autonomous actor and does not replace
JAZEKKER, AI Cabinet or ASTI.

```text
JAZEKKER   = orientation interface
AI Cabinet = governance substrate
TESTBOX    = observable runtime and quality surface
ASTI       = controlled execution boundary
Meta-QMS   = reviewed improvement loop
```

## Runtime Boundary

Meta-QMS may:

- record a quality assessment;
- register a deviation;
- propose a bounded improvement;
- expose evidence, risk and acceptance conditions;
- capture a human decision in audit.

Meta-QMS may not:

- apply a policy change automatically;
- execute an external action;
- treat approval of a proposal as completed implementation;
- store obvious email or telephone identifiers unredacted in a proposal.

## Cycle

```text
Event
-> Context Analysis
-> Risk Evaluation
-> Policy Matching
-> Routing
-> AI/Human Decision
-> Execution
-> Audit
-> Reflection
-> Learning
-> Evolution Proposal
-> Human Review
```

## Implemented API

| Endpoint | Purpose |
| --- | --- |
| `GET /api/testbox/runtime/meta-qms` | Show layers, cycle, metrics and recent proposals. |
| `POST /api/testbox/runtime/meta-qms/assess` | Create a review-required evolution proposal and audit events. |
| `POST /api/testbox/runtime/meta-qms/proposals/{id}/decision` | Record human approval or rejection without executing change. |

## Audit Events

- `QUALITY_ASSESSED`
- `DEVIATION_RECORDED`
- `EVOLUTION_PROPOSED`
- `EVOLUTION_APPROVED`
- `EVOLUTION_REJECTED`

## Acceptance Rule

An improvement is not complete when a proposal is approved. It becomes
complete only after a separate governed implementation, regression evidence
and explicit review of its mission and risk effect.
