# TESTBOX v0.1 Acceptance Report

Date: 2026-05-20

Status:

```text
TESTBOX v0.1 = passed local functional smoke test.
Ready for backend integration phase.
```

## Executive Summary

TESTBOX has reached an MVP working state as a local AI operations and governance
environment for ASTREB OS.

The v0.1 smoke test confirms that TESTBOX is no longer only a concept or static
dashboard. It now demonstrates a working local cockpit with roles, scenarios,
routing explanation, audit activity, local memory, approval actions, legal demo
flow, and voice-command fallback.

## Confirmed Capabilities

| Block | Status |
| --- | --- |
| UI buttons | working |
| Roles | 8/8 working |
| Scenarios | legal / routing / audit working |
| Audit stream | accumulating |
| Memory | updating |
| Approval/actions | passing |
| Console errors | 0 |
| Voice fallback | working |
| Local MVP stability | confirmed |

## Functional Smoke Test Results

Test route:

```text
http://127.0.0.1:8123/testbox/audit
```

Results:

```text
Visible buttons: 53
Automated button checks: 52
Passed button checks: 52
Failed button checks: 0
Role/scenario checks: 24
Passed role/scenario checks: 24
Failed role/scenario checks: 0
Console errors: 0
Audit stream: 86 events
Memory: 18 local workflow memories stored
Final route: /testbox/audit
Final scenario: Audit Replay
Final role: CRM Dispatcher
Runtime status: standby
```

Skipped intentionally:

```text
Start Voice
```

Reason: browser microphone permission must be tested separately and explicitly
by an operator.

## Architecture Confirmed

TESTBOX v0.1 confirms the intended separation:

```text
Static Layer:
roles / routes / skills / settings

Dynamic Layer:
scenarios / actions / audit / memory

Observation Layer:
cockpit / routing / audit / demo pages
```

This separation keeps AI Cabinet and TESTBOX distinct:

```text
AI Cabinet = static governance architecture
TESTBOX = dynamic operations and demonstration environment
```

## Route Surface

The TESTBOX shell supports:

```text
/testbox
/testbox/cockpit
/testbox/orchestration
/testbox/legal
/testbox/legal-demo
/testbox/audit
/testbox/routing
/testbox/memory
/testbox/settings
/testbox/training
/testbox/hackathon
```

The primary route is not treated as a normal dashboard page. It acts as an
operational cockpit shell with live state, activity streams, routing, approvals,
system narration, and scenario modes.

## v0.1 Boundaries

v0.1 is a local functional MVP. The following blocks are intentionally local,
mocked, or browser-native:

- Audit persistence uses browser local state.
- Memory persistence uses browser local state.
- Legal source retrieval uses local in-page sources.
- LLM drafting is simulated as governed local drafting.
- QMS checks are local deterministic checks.
- Voice fallback works through text command input.
- Browser STT/TTS support depends on browser permissions and capabilities.

## v0.2 Integration Backlog

1. Voice permission test as a separate operator-controlled test.
2. Real backend events instead of mock/local state.
3. Persistent audit storage.
4. Real PII masking pipeline.
5. Legal source retrieval integration.
6. Real approval workflow.
7. Exportable demo report.

## Acceptance Decision

TESTBOX v0.1 is accepted as a local functional smoke-test pass.

Next phase:

```text
Backend integration phase for TESTBOX v0.2
```
