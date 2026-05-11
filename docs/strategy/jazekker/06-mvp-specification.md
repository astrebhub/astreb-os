# JAZEKKER - MVP Specification

## MVP Objective

Build the smallest useful JAZEKKER system that can turn signals into governed Orientation Objects and prepare public-ready outputs without bypassing human approval.

The MVP must prove:

- JAZEKKER can identify meaningful signals.
- AI Cabinet can turn signals into structured Orientation Objects.
- Sources, confidence, uncertainty, and approval status are visible.
- One approved object can become multiple channel-specific drafts.
- No publication or distribution happens without approval.

## Core Object

The Orientation Object is the source-of-truth unit.

Schema:

```text
ai-cabinet/schemas/orientation-object.schema.json
```

Examples:

```text
content/orientation/2026-05-11-ai-governance-signal.json
content/orientation/2026-05-11-local-first-ai-infrastructure.json
content/orientation/2026-05-11-agentic-media-runtime.json
```

## Required Workflow States

```text
draft -> reviewed -> approved -> scheduled -> published
```

Additional hold states:

```text
needs_sources
needs_governance_review
blocked
archived
```

Only `approved` objects may be transformed into publish-ready distribution drafts. Only `scheduled` objects may move toward channel execution. Publication still requires an external approval record.

## Minimum Agents

### Trend Analyst Agent

Turns raw signals into signal candidates and assigns preliminary noise level, impact horizon, and audience relevance.

### Research Agent

Builds source packs, checks claims, separates fact from interpretation, and estimates confidence.

### Governance Agent / Risk Sentinel

Checks sensitive domains, unsupported certainty, manipulation risk, privacy risk, and approval requirements.

### Editor Agent

Improves clarity, structure, tone, and public readability after evidence and governance checks.

### Distribution Orchestrator

Creates channel-specific drafts only after approval. It may not publish.

## MVP Pipeline

```text
1. Signal intake
2. Classification and risk scoring
3. Source pack creation
4. Orientation Object draft
5. Governance and uncertainty review
6. Editorial refinement
7. Human approval
8. Distribution draft generation
9. Publish queue proposal
10. Strategic memory proposal
```

## Audit Events

Every object should record:

- source intake time;
- classifier result;
- policy result;
- agent drafts;
- evidence review;
- confidence change;
- approval state change;
- distribution draft creation;
- memory proposal.

## Do-Not-Build List For MVP

- No infinite personalized feed.
- No direct auto-publishing.
- No engagement optimization loop.
- No unsupported breaking-news claims.
- No anonymous source claims without explicit governance review.
- No strategic memory writes without approval.

## First Product Surface

The first public surface should show:

- a calm homepage hero;
- Daily Orientation;
- Meaningful Signals Map;
- selected Orientation Objects;
- source and confidence indicators;
- AI Cabinet trust architecture;
- clear paths for people and organizations.

## Success Criteria

The MVP is successful when a user can understand what matters today, why it matters, what is uncertain, who is affected, and what the next orientation step should be without entering a chaotic content feed.
