# TESTBOX QMS Quality Runtime

## Mission

TESTBOX now includes a runtime Quality Layer before final output release.

The runtime path is:

```text
Expected State
-> Action
-> Result
-> Observation
-> Deviation Detection
-> Intervention
-> Learning
-> Improvement
```

## Runtime Integration

Every `/api/testbox/runtime/message` response now contains:

- loaded governance skills
- quality score
- detected deviations
- interventions
- approval events
- learning events
- release decision

TESTBOX should be positioned as:

```text
A QMS-driven Governance Runtime for observing, correcting and improving AI-assisted processes.
```

It is not a chatbot, dashboard, workflow engine, or standalone evaluation tool.

Quality events are emitted before `ANSWER_GENERATED`:

```text
ANSWER_STRATEGY_SELECTED
-> QUALITY_SKILLS_LOADED
-> QUALITY_EVALUATED
-> QUALITY_INTERVENTION_APPLIED, if needed
-> LEARNING_CAPTURED, if needed
-> ANSWER_GENERATED
```

## Governance Skill Library

Canonical skills live in:

```text
backend/testbox_runtime/skills/
```

Initial skills:

- Human Approval Required
- Procedural Integrity
- Deadline Governance
- Neutral Administrative Tone
- Uncertainty Disclosure
- Evidence-Based Responses
- Clarifying Questions Required

Each skill has:

- purpose
- constraints
- evaluation rules
- intervention rules
- improvement history

## Scenario Layer

The Scenario Layer defines realistic execution contexts.

Endpoint:

```text
GET /api/testbox/runtime/qms/scenarios
```

Initial scenarios:

- citizen request
- permit request
- policy consultation
- QMS skill evolution

Each scenario contains:

- expected outcome
- constraints
- governance rules

## Skill Evolution Layer

Skills are living artifacts.

Lifecycle:

```text
Skill
-> Use
-> Evaluation
-> Deviation
-> Improvement Proposal
-> Human Decision
-> New Skill Version
```

Endpoints:

```text
POST /api/testbox/runtime/qms/skills/{skill_id}/evolution
POST /api/testbox/runtime/qms/skills/evolution/{proposal_id}/decision
```

Rules:

- proposals default to `review_required`
- automatic execution is false
- approved changes require explicit human decision
- history is preserved in the skill improvement log

## Meta-QMS Layer

Endpoint:

```text
GET /api/testbox/runtime/qms/meta
```

Tracks:

- frequent deviations
- recurring scenarios
- governance gaps
- successful interventions
- recommendations for TESTBOX improvement

## Learning Repository

Deviations and interventions are persisted in:

```text
audit/qms_learning_records.jsonl
```

This makes QMS behavior observable and measurable over time.

## Observation Endpoints

```text
GET /api/testbox/runtime/qms/skills
GET /api/testbox/runtime/qms/learning
```

Both endpoints require the admin token.

## Safety Boundary

The Quality Layer may detect, flag, explain, and add safe limitation language.

It may not:

- create legal effect
- grant final approval
- modify procedural deadlines
- dispatch official responses
- execute external actions

Human authority remains the final boundary.

## CAPA: ASTREB TESTBOX Positioning Fallback

Date: 2026-05-29

Observed deviation:

```text
ASTREB TESTBOX как лучше позиционировать
```

was routed to generic intake instead of strategic positioning.

Root cause:

- missing product-positioning domain
- missing strategic-positioning intent
- no quality skill requiring clarifying questions for strategic ambiguity

Corrective action:

- added `testbox_product` domain
- added `strategic_positioning` intent and response renderer
- routed request to `Orientation -> Strategic Positioning`

Preventive action:

- added `clarifying_questions_required` governance skill
- added regression tests for strategic positioning and QMS skill behavior

Human authority boundary:

The system may suggest positioning and ask questions. It does not publish, approve market claims, or perform external communication automatically.
