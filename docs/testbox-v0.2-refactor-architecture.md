# ASTREB TESTBOX v0.2 Refactor Architecture

## Executive Goal

TESTBOX v0.2 moves the project from a frontend-heavy governance demo to an
event-driven AI governance runtime environment.

The current v0.1 UI is preserved as the observation and demo surface. Runtime
authority moves to the backend.

```text
AI Cabinet = static governance architecture
TESTBOX = dynamic runtime + orchestration + explainability + observation
```

```text
TESTBOX Runtime = Role + Mode + Capabilities + Skills + Policies + State + Audit
```

## Layer Separation

### Static Layer

Owns configuration and governance definitions:

- roles
- skills
- policies
- connectors
- legal source registry
- memory rules
- audit schema
- routing configuration
- UI configuration

### Runtime Layer

Owns execution:

- event creation
- policy evaluation
- LegalBox pipeline
- routing decision
- answer generation
- human review state
- audit persistence
- memory update intent

### Observation Layer

Owns visibility, not execution:

- TESTBOX cockpit
- routing monitor
- audit stream
- LegalBox demo view
- user chat surface
- role/skill visibility
- quality and explainability panels

Observation surfaces must never pretend to be the backend runtime.

## v0.2 Backend Runtime Skeleton

The first v0.2 implementation introduces:

```text
backend/testbox_runtime/
  models.py          runtime event, request, response, source models
  audit_store.py     JSONL audit persistence
  event_bus.py       in-memory event stream + audit append
  policy_engine.py   structured policy evaluation
  legal_sources.py   official source registry + retrieval
  legalbox.py        explicit LegalBox pipeline
  api.py             FastAPI runtime endpoints
```

## Event System

Core runtime events:

- USER_MESSAGE_RECEIVED
- LANGUAGE_DETECTED
- LEGAL_CLASSIFIED
- CLASSIFICATION_UNCERTAIN
- JURISDICTION_DETECTED
- RISK_FLAGGED
- PII_DETECTED
- SOURCE_REQUIRED
- LEGAL_RETRIEVAL_COMPLETED
- ROUTING_SELECTED
- ANSWER_GENERATED
- DISCLAIMER_ATTACHED
- HUMAN_REVIEW_REQUIRED
- AUDIT_EVENT_CREATED
- MEMORY_UPDATED
- APPROVAL_GRANTED
- APPROVAL_DENIED

## Orientation Safety Layer

TESTBOX applies a regulated-domain guard before allowing a message to use the
general interaction route.

```text
ambiguous practical request
-> detect regulated signals
-> produce domain candidates and confidence
-> require sources if regulatory signals exist
-> require human review when confidence is low or source coverage is missing
```

Runtime settings:

```json
{
  "classification_mode": "multi_domain",
  "allow_general_fallback": false,
  "regulated_domain_guard": true,
  "source_required_on_regulated_signal": true,
  "human_review_on_low_confidence": true
}
```

The safety principle is: prefer routing into governance over silently routing
a potentially regulated request into ordinary chat.

## LegalBox Pipeline

```text
User Question
-> language detection
-> jurisdiction detection
-> legal domain classification
-> risk classification
-> PII/sensitive check
-> source requirement
-> legal retrieval
-> routing
-> governed answer draft
-> legal safety review
-> disclaimer injection
-> final response
-> audit log
```

## Source Governance

Legal answers must be source-bound.

They must separate:

- informational guidance
- source facts
- risk warning
- next steps
- human consultation recommendation
- disclaimer

LegalBox is not a legal advice engine. It is a governed legal orientation
workflow.

## Human Review Rules

`REQUIRES_HUMAN_REVIEW` is required for:

- immigration
- tax penalties
- employment termination
- fraud accusations
- liability
- contracts
- litigation
- benefits sanctions

## Audit Object

```json
{
  "id": "uuid",
  "timestamp": "ISO-8601",
  "user_session": "session id",
  "role": "Legal Assistant",
  "route": "Legal Retrieval -> Governed Draft -> Human Review",
  "policy": ["legal_answers_require_sources"],
  "risk_level": "high",
  "jurisdiction": "Netherlands",
  "source_refs": ["wetten-wvw-article-185"],
  "action": "LEGAL_RETRIEVAL_COMPLETED",
  "approval_state": "REQUIRES_HUMAN_REVIEW",
  "payload": {}
}
```

## v0.2 Roadmap

1. Backend runtime API and audit persistence.
2. WebSocket event stream for cockpit observation.
3. Frontend migration from local simulation to backend events.
4. Backend-enforced approval workflow.
5. Document extraction service.
6. OCR pipeline.
7. Real legal retrieval adapters.
8. PostgreSQL audit storage.
9. Redis event queue.
10. LangGraph workflow orchestration.

## v0.3 Roadmap

1. Multi-session operator console.
2. PostgreSQL + pgvector retrieval.
3. Real connector framework for CRM, Legal DB, OpenAI, Claude, Ollama.
4. Role/skill/policy administration UI.
5. Signed exportable audit reports.
6. Deployment hardening with Docker Compose profiles.
7. Monitoring, retention policy, and privacy controls.

## Critical Anti-Patterns

- Do not collapse runtime into one AI agent.
- Do not hardcode governance decisions in frontend buttons.
- Do not treat audit as cosmetic UI logging.
- Do not allow LegalBox to answer without sources.
- Do not overload `/testbox/user` with cockpit internals.
- Do not merge roles, skills, policies, workflows, and prompts.
