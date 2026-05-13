# JAZEKKER - Governed Editorial Workflow

## Updated Architecture

```text
Source intake
  -> deduplication
  -> classification
  -> signal extraction
  -> canonical Orientation Object
  -> risk classification
  -> editorial draft
  -> governance review
  -> human approval
  -> publication queue
  -> local/external publication
  -> audit trail
```

## Backend Structure

- `backend/cabinet/orientation_workflow.py`: canonical workflow, status transitions, scoring, governance metadata, audit writes.
- `backend/cabinet/news_collector.py`: RSS intake, rubric mapping, draft signal creation.
- `backend/cabinet/database.py`: `orientation_objects` and `editorial_audit` tables.
- `backend/main.py`: editorial API endpoints and dashboard route.
- `frontend/jazekker-editorial.html`: local editorial control panel.

## Canonical Orientation Object

Required fields are defined in:

```text
ai-cabinet/schemas/orientation-object.schema.json
```

Core fields:

```yaml
id:
title:
summary:
signal:
context:
impact:
confidence_score:
risk_level:
orientation_score:
recommended_action:
rubric:
sources:
source_count:
status:
created_at:
updated_at:
review_required:
governance_notes:
human_approved:
human_reviewer:
publication_target:
```

## Workflow State Machine

```text
collected
  -> classified
  -> drafted
  -> review_required
  -> approved
  -> scheduled
  -> published_local
  -> published_external
  -> archived

blocked can return to review_required or archive.
```

## API Endpoints

```text
GET  /jazekker/editorial
GET  /jazekker/orientation-objects
GET  /jazekker/orientation-objects/{object_id}
GET  /jazekker/editorial/audit
POST /jazekker/orientation-objects/ingest-local
POST /jazekker/orientation-objects/ingest-news
POST /jazekker/orientation-objects/{object_id}/action
```

Supported actions:

```text
review
approve
reject
block
escalate
schedule
publish_local
publish_external
archive
edit
```

## Governance Logic

- RSS items default to `review_required` before publication.
- Local seed articles may be `published_local`.
- External publishing always requires prior human approval.
- High-risk content requires review notes.
- Every transition writes to `editorial_audit`.
- Publication is separated into `published_local` and `published_external`.

## Database Model

```text
orientation_objects
  id
  created_at
  updated_at
  status
  rubric
  title
  publication_target
  risk_level
  confidence_score
  orientation_score
  record

editorial_audit
  id
  created_at
  object_id
  stage
  actor
  action
  from_status
  to_status
  metadata
```

## Audit Model

Every workflow stage produces an audit row:

```json
{
  "object_id": "oo-...",
  "stage": "Governance Review",
  "actor": "news_collector",
  "action": "transition",
  "from_status": "drafted",
  "to_status": "review_required",
  "metadata": {"notes": "Human review required before publication."}
}
```

## Publication Flow

```text
published_local
  local readable state
  no external distribution
  reversible by archive

published_external
  requires prior approval
  requires audit trail
  should later call ASTI connectors
```

## Rollback Strategy

Current rollback is conservative:

- archive object;
- preserve audit trail;
- do not delete source provenance;
- do not remove prior state history.

Future rollback may add restoration from audit snapshots.

## Operational Rule

AI Cabinet thinks.
ASTI acts.
JAZEKKER orients.
Human approves.
Governance binds everything.
