# LegalBox for TESTBOX

Status: AI Cabinet module for TESTBOX v0.2 direction

## Purpose

LegalBox turns TESTBOX from a simple legal question-answer surface into a
governed legal workflow environment.

LegalBox does not provide final legal advice. It provides informational legal
orientation, risk classification, source requirements, safe next steps, and
auditability.

Core rule:

```text
LegalBox must not say:
"Here is exact legal advice."

LegalBox should say:
"This is informational legal orientation. For a decision in your case, consult a
lawyer / belastingadviseur / gemeente / IND / UWV or another competent body."
```

## Workflow

```text
User question
↓
Language detection
↓
Jurisdiction detection
↓
Legal domain classification
↓
Risk classification
↓
PII / sensitive data check
↓
Source requirement
↓
Agent routing
↓
Draft answer
↓
Legal safety review
↓
Final answer + disclaimer + next steps
↓
Audit log
```

## Legal Roles

| Role | Purpose |
| --- | --- |
| Legal Intake Agent | receives the question and asks for missing context |
| Jurisdiction Agent | identifies country, region, and legal system |
| Legal Domain Classifier | classifies housing, employment, taxes, family, documents, benefits, immigration, consumer, business |
| Risk Agent | classifies low / medium / high / emergency |
| Source Agent | requires official or reliable sources |
| Legal Reasoning Agent | prepares structured informational answer |
| Compliance Guard | removes unsafe advice, guarantees, or overclaims |
| Human Review Gate | requires human review for high-risk cases |
| Audit Agent | saves logs, reasons, route, and decision basis |

## Universal Answer Structure

```text
1. Short answer
2. Legal domain
3. Jurisdiction
4. Possible consequences
5. What must be clarified
6. Needed documents
7. Where to go
8. Risks
9. Next steps
10. Disclaimer
```

## Demo Modules

```text
LegalBox Core
├── Intake
├── Classification
├── Routing
├── Source Check
├── Risk Control
├── Answer Generator
├── Human Approval
├── Audit Log
└── Demo Cockpit
```

## AI Cabinet Fit

Static Layer:

- legal roles
- policies
- source requirements
- jurisdiction rules
- risk rules
- audit schema

Dynamic Layer:

- legal workflow execution
- classification
- routing
- review gates
- answer generation

Observation Layer:

- LegalBox cockpit
- visible agents
- risk and policy explanation
- audit trail
- final answer with limitations
