# TESTBOX v0.2 Implementation Plan

## 1. Full Architecture Refactor Plan

Preserve the v0.1 UI as the observation console and move runtime authority to
FastAPI backend services.

Phases:

1. Introduce backend runtime API.
2. Emit structured events for every runtime decision.
3. Persist audit events.
4. Migrate frontend buttons from local state mutation to backend calls.
5. Add WebSocket live event stream.
6. Replace local source registry with retrieval adapters.
7. Add document/OCR pipeline.
8. Add LangGraph orchestration.

## 2. Updated Folder Structure

```text
backend/
  main.py
  testbox_runtime/
    api.py
    audit_store.py
    event_bus.py
    legal_sources.py
    legalbox.py
    models.py
    policy_engine.py

audit/
  testbox_runtime_events.jsonl

docs/
  testbox-v0.2-refactor-architecture.md
  testbox-v0.2-implementation-plan.md
```

## 3. Backend / Runtime Separation

Backend owns:

- events
- routing
- policies
- risk classification
- legal retrieval
- approval state
- audit persistence

Frontend owns:

- display
- user input
- operator controls
- observation panels
- explanation views

## 4. Event System Architecture

The current implementation adds a runtime event bus with JSONL audit append.

Next step:

- add WebSocket streaming
- add event replay cursor
- add Redis queue adapter
- add PostgreSQL audit adapter

## 5. LegalBox Backend Workflow

Implemented first backend pipeline:

```text
message
-> language detection
-> jurisdiction detection
-> domain classification
-> risk classification
-> PII check
-> policy evaluation
-> source retrieval
-> route selection
-> answer generation
-> disclaimer
-> human review flag
-> audit event persistence
```

## 6. LangGraph Orchestration Proposal

Future graph nodes:

- intake_node
- language_node
- jurisdiction_node
- domain_node
- risk_node
- pii_node
- policy_node
- retrieval_node
- routing_node
- draft_node
- safety_review_node
- approval_node
- audit_node
- memory_node

Edges are controlled by risk, policy, source availability, and approval state.

## 7. Audit Persistence Design

v0.2 starts with JSONL:

```text
audit/testbox_runtime_events.jsonl
```

Target production adapter:

```sql
testbox_audit_events(
  id uuid primary key,
  timestamp timestamptz,
  user_session text,
  role text,
  route text,
  policy jsonb,
  risk_level text,
  jurisdiction text,
  source_refs jsonb,
  action text,
  approval_state text,
  payload jsonb
)
```

## 8. Policy Engine Structure

Current policies:

- `pii_must_be_masked_before_cloud`
- `legal_answers_require_sources`
- `high_risk_requires_approval`

Next:

- external YAML policy loading
- policy versioning
- policy evaluation traces
- policy test fixtures

## 9. Human Approval Workflow

Current API:

```text
POST /api/testbox/runtime/approval
```

Next:

- approval queue
- pending answer state
- operator decision record
- reject reason
- override reason
- replay from approval point

## 10. Legal Retrieval Architecture

Current:

- curated official source registry
- keyword/domain scoring
- source-bound answer enforcement

Next:

- source adapters
- official URL fetcher
- cached source snapshots
- source freshness metadata
- citation verifier
- pgvector semantic retrieval

## 11. Frontend Observation Redesign

Frontend should consume:

- `POST /api/testbox/runtime/message`
- `GET /api/testbox/runtime/events`
- future `/ws/testbox/runtime/events`

User chat must stay clean. Cockpit can show:

- event timeline
- route graph
- policy triggers
- approval queue
- audit replay
- source references

## 12. Runtime State Model

Runtime state is derived from events:

```text
session_state =
  current_role
  current_mode
  latest_route
  risk_level
  jurisdiction
  active_policies
  source_refs
  approval_state
  final_response
```

## 13. Security Model

Rules:

- never persist raw PII unless explicitly required
- persist metadata before content
- mask before external model/tool call
- source-bound legal answers
- require human review for high-risk domains
- log all approvals and overrides

## 14. PII Handling Strategy

Current:

- regex detection only
- policy trigger only

Next:

- local masking service
- placeholder map
- encrypted local rehydration
- PII retention policy
- no raw PII in audit payloads

## 15. Upload / Document Pipeline

Target flow:

```text
upload
-> file validation
-> malware/type checks
-> text extraction
-> OCR if needed
-> PII scan
-> document summary
-> runtime event
```

## 16. OCR Pipeline Proposal

Recommended:

- local OCR first
- scanned PDF/image detection
- confidence score
- operator-visible extraction quality
- manual correction state
- never send raw scans externally before PII masking

## 17. Production Deployment Architecture

Target services:

- frontend static app
- FastAPI runtime
- PostgreSQL
- Redis
- object/file storage
- OCR worker
- retrieval worker
- optional local model worker

## 18. v0.2 Roadmap

1. Backend runtime API.
2. JSONL audit persistence.
3. Frontend chat calls backend runtime.
4. Cockpit reads backend events.
5. Approval endpoint becomes enforced gate.
6. Document extraction moves to backend.
7. Official source registry is expanded.
8. WebSocket event streaming.

## 19. v0.3 Scalability Roadmap

1. PostgreSQL audit schema.
2. Redis event queue.
3. pgvector retrieval.
4. LangGraph workflow engine.
5. Connector plugin framework.
6. Multi-user sessions.
7. Signed audit exports.
8. Deployment profiles.

## 20. Critical Anti-Patterns To Avoid

- frontend-only fake orchestration
- chatbot-first UX
- role/skill/policy mixing
- legal answers without sources
- cosmetic audit
- hidden routing
- raw PII in logs
- one-agent monolith
- overloading `/testbox/user`
- treating LegalBox as a lawyer replacement
