# TESTBOX Starter Kit Comparison And Integration

Date: 2026-05-22

Source archive:

```text
local source archive, not committed
```

Integrated location:

```text
governance/testbox-starter-kit/
```

## Summary

The starter kit is a governance and specification package, not a replacement
frontend application.

It contains:

```text
README.md
roles.json
role_prompts.md
policies.yaml
runtime_config.json
TESTBOX_Runtime_Governance_Ontology.md
TESTBOX_Technical_Specification.docx
```

The current TESTBOX implementation contains the working cockpit UI, route shell,
playbooks, local runtime behavior, PII masking demo, routing monitor, audit
stream, memory updates, quality monitoring, and Administrator narration.

## Comparison

| Area | Starter Kit | Current TESTBOX |
| --- | --- | --- |
| Purpose | Baseline governance package | Working local operations cockpit |
| Frontend UI | none | `frontend/testbox.html` |
| Routes | listed in README | implemented in FastAPI and local server |
| Roles | 3 roles | 8 roles |
| Policies | 2 baseline policies | local policy behavior + explanations |
| Runtime config | static JSON | live browser runtime state |
| Legal demo | route listed | working local scenario |
| PII masking | capability listed | working local masking visualization |
| Audit | capability listed | working local audit stream |
| Memory | not detailed | working local memory count |
| Voice | not detailed | text fallback + STT/TTS controls |
| Technical spec | DOCX included | docs + implemented cockpit |

## Starter Kit Roles

The starter kit defines:

```text
GovernanceOfficer
Operator
LegalAssistant
```

These map into the current TESTBOX role system:

```text
GovernanceOfficer -> Governance Officer
Operator -> Operator
LegalAssistant -> Legal Assistant
```

The current TESTBOX also includes:

```text
Instructor
Project Architect
Demo Presenter
Hackathon Mentor
CRM Dispatcher
```

## Starter Kit Policies

The starter kit defines two baseline policies:

```text
pii_must_be_masked_before_cloud
high_risk_requires_approval
```

These are already represented in current TESTBOX behavior:

```text
Sensitive data -> local PII masking before cloud-style drafting
High risk legal workflow -> human approval gate
```

## Integration Decision

Do not replace `frontend/testbox.html` with the starter kit because the archive
does not include an equivalent frontend runtime.

Instead:

```text
Starter Kit = governance baseline / source package
Current TESTBOX = working v0.1 runtime cockpit
```

The practical replacement is:

```text
Replace loose conceptual baseline with the starter kit governance package.
Keep the current TESTBOX cockpit as the executable implementation.
```

## Integrated Files

Copied into:

```text
governance/testbox-starter-kit/
```

Files:

```text
README.md
roles.json
role_prompts.md
policies.yaml
runtime_config.json
TESTBOX_Runtime_Governance_Ontology.md
TESTBOX_Technical_Specification.docx
```

## Next Step

For v0.2, the frontend should load or mirror these files as real configuration
through a backend endpoint:

```text
GET /testbox/config/roles
GET /testbox/config/policies
GET /testbox/config/runtime
GET /testbox/config/ontology
```

This will turn the starter kit from a source package into live TESTBOX runtime
configuration.
