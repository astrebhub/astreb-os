# ASTREB Landing Architecture Spec v1

Status: foundation draft
Scope: institutional presence for `astreb.nl`

## Purpose

ASTREB Landing v1 establishes an institutional identity portal for architecture,
governance, and operational intelligence work. It should make ASTREB feel
mature, precise, and trustworthy before any product dashboard, login, or agent
surface is exposed.

The page is not a startup pitch, AI platform claim, or automation demo. It is
the public entry point for the ecosystem.

## Strategic Sequence

```text
Identity
  -> Presence
  -> Trust
  -> Infrastructure
  -> Operations
  -> Ecosystem
```

## Information Architecture

### 1. Hero

Primary signal:

```text
ASTREB
Architecture - Governance - Operational Intelligence
```

Hero goals:

- Establish the name as the first-viewport anchor.
- Use institutional language, not hype language.
- Keep the primary CTA low-pressure: contact and ecosystem orientation.
- Avoid product UI, dashboard previews, and automation claims.

### 2. Positioning

Explain ASTREB as a governance-oriented architecture practice for AI-enabled
operations.

Core concepts:

- Governance before autonomy.
- Orchestration before automation.
- Operational quality before volume.
- Human authority over durable decisions.

### 3. Core Directions

Four initial directions:

- AI Cabinet
- Governance Systems
- Orientation Intelligence
- Human-AI Interaction

Each direction should describe a field of work, not a finished product promise.

### 4. Architecture Block

Public-facing schema:

```text
Human
  |
  v
Governance
  |
  v
AI Systems
  |
  v
Operational Decisions
```

The block should visually communicate hierarchy, control, and accountability.

### 5. Contact / Links

Minimum:

- GitHub
- LinkedIn
- The Hague, Netherlands

Future:

- `contact@astreb.nl`
- `governance@astreb.nl`
- `hello@astreb.nl`

## Visual Direction

Use a restrained institutional system:

- Warm off-white base.
- Charcoal text.
- Deep green and muted steel blue accents.
- Small brass highlights.
- Dense but breathable layout.
- 8px maximum radius for cards and framed elements.
- No purple gradient identity, bokeh, decorative orbs, or generic SaaS hero.

## Deployment Structure

```text
astreb_landing/
  index.html
  styles.css
  assets/
    astreb-hero.png
```

This folder is intentionally static so it can be deployed by SFTP to the domain
root without backend complexity.

## Future DNS Map

| Subdomain | Role |
| --- | --- |
| `astreb.nl` | Institutional portal |
| `cabinet.astreb.nl` | AI Cabinet |
| `api.astreb.nl` | Gateway |
| `labs.astreb.nl` | Experiments |
| `docs.astreb.nl` | Frameworks |
| `signal.astreb.nl` | Signal / Jazekker layer |

## Explicit Non-Goals For v1

- Login
- Dashboard
- Agent interface
- Backend runtime
- Automation workflows
- Claims of enterprise readiness
- Contact forms that imply data handling before policy exists

