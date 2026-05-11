# JAZEKKER Approval Policy

## Rule

JAZEKKER may use AI to draft, classify, interpret, transform, and propose.

JAZEKKER may not use AI to publish, distribute, send, delete, change durable strategy, change policy, or update strategic memory without an approval record.

## Required Approval Cases

Human approval is required for:

- publication;
- scheduling publication;
- social distribution;
- newsletter sending;
- strategic memory updates;
- source corrections;
- sensitive public claims;
- legal, medical, financial, political, reputational, privacy, or security content;
- policy changes;
- exceptions to governance blocks.

## Status Model

```text
draft -> reviewed -> approved -> scheduled -> published
```

Hold states:

```text
needs_sources
needs_governance_review
blocked
archived
```

## Approval Record

Every approval should include:

- approval id;
- object id;
- approval type;
- requester;
- reviewer;
- decision;
- rationale;
- timestamp;
- audit ids.

Schema:

```text
ai-cabinet/schemas/approval.schema.json
```
