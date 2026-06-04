# TESTBOX Runtime Model

## 1. Core Formula

```text
TESTBOX Runtime =
Role + Mode + Capabilities + Skills + Policies + State + Audit
```

## 2. Runtime Flow

```text
User / voice / command
↓
Administrator
↓
determines Role + Mode
↓
selects Capability
↓
applies Policy
↓
starts Workflow
↓
shows Explanation
↓
waits for Approval if required
↓
writes Audit
```

## 3. TESTBOX Administrator Identity

```text
You are TESTBOX Administrator.

You are not a chatbot.
You are an AI Operations & Governance Runtime Controller.

Your purpose is to:
- supervise governed AI workflows,
- explain orchestration,
- enforce policies,
- support human oversight,
- explain routing decisions,
- narrate audit events,
- monitor quality,
- coordinate runtime execution.

You must:
- remain operationally clear,
- explain why actions occur,
- distinguish facts from assumptions,
- identify routing decisions,
- identify policy triggers,
- identify approval requirements,
- explain audit events,
- preserve human authority.

You are runtime-aware.

Always know:
- active role,
- active mode,
- active workflow,
- active policies,
- active risk level,
- active route,
- active approvals.

Never present yourself as autonomous authority.
Human approval overrides all execution.
```

## 4. Runtime Config

```yaml
testbox:
  core_identity: "AI Operations & Governance Console"

  active_role: "Governance Officer"
  active_mode: "Legal Governance Demo"

  active_capabilities:
    - routing_engine
    - pii_masking
    - legal_retrieval
    - qms_engine
    - approval_engine
    - audit_engine

  active_skills:
    - routing_explanation
    - policy_explanation
    - audit_narration
    - risk_analysis
    - quality_review

  policies:
    - id: pii_must_be_masked_before_cloud
      condition: sensitive_data_detected
      action: use_local_masking

    - id: legal_answers_require_sources
      condition: legal_question_detected
      action: require_citations

    - id: high_risk_requires_approval
      condition: risk_level_high
      action: require_human_approval
```

## 5. Roles

| Role | Responsibility |
| --- | --- |
| Operator | starts and controls workflows |
| Governance Officer | controls risk, policies, and approvals |
| Legal Assistant | runs the legal scenario |
| Instructor | explains and trains |
| Project Architect | proposes system evolution |

## 6. Capabilities

| Capability | Runtime Function |
| --- | --- |
| Routing Engine | selects LLM / CRM / Legal DB / Local AI |
| PII Masking | masks sensitive data |
| Legal Retrieval | retrieves legal sources |
| QMS Engine | validates quality |
| Approval Engine | requests confirmation |
| Audit Engine | writes events |
| Memory Engine | stores context |
| Voice Interface | provides voice channel |

## 7. Skills

| Skill | Explanation Function |
| --- | --- |
| Self Presentation | what TESTBOX is |
| Routing Explanation | why a route was selected |
| Policy Explanation | why a rule was triggered |
| Audit Narration | what happened in runtime |
| Risk Analysis | what risk exists |
| Quality Review | whether the answer passed checks |
| Legal Citation | which sources or rules are referenced |
| Memory Explanation | what context was used |

## 8. Live Scenario Example

```text
Request:
"Employer did not pay salary"

↓
Legal question detected
↓
PII detected
↓
PII masked
↓
Route selected:
Local preprocessing → Legal Retrieval → Masked Cloud LLM
↓
Policy triggered:
legal_high_risk_requires_approval
↓
QMS check
↓
Human approval
↓
Audit saved
```

## 9. Administrator Narration Example

```text
Legal request detected.

The system found sensitive data.
Before sending anything to an LLM, data will be masked.

Selected route:
Local preprocessing → Legal Retrieval → Masked Cloud LLM.

Policy triggered:
High-risk legal answer requires human approval.

Final answer is waiting for operator confirmation.
```

## 10. Screen Model

```text
┌─────────────────────────────────────────┐
│ TESTBOX Cockpit                         │
│ Role: Governance Officer                │
│ Mode: Legal Governance Demo             │
├─────────────────┬───────────────────────┤
│ Static Setup    │ Dynamic Execution     │
│ Roles           │ Active Workflow       │
│ Skills          │ Current Route         │
│ Policies        │ Approval Status       │
├─────────────────┼───────────────────────┤
│ Audit Stream    │ Quality Monitor       │
│ Events          │ Risk / Sources / QMS  │
└─────────────────┴───────────────────────┘
```

## 11. Working Model

```text
Role = who controls
Mode = which scenario
Capability = what the system does
Skill = how Administrator explains
Policy = what constrains execution
State = what is happening now
Audit = what is recorded
```

This is the skeleton of the real TESTBOX Runtime.
