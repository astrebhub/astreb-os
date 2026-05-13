# JAZEKKER - Master Portal Architecture v3.0

## Purpose

JAZEKKER is an orientation-native civic intelligence platform. It is not a news site, blog, dashboard, productivity app, social feed, or generic AI portal.

Core transformation:

```text
noise -> signal
information -> context
fragmentation -> coherence
complexity -> clarity
```

Primary position:

```text
A portal for calm orientation in a complex world.
An orientation-native civic intelligence system.
```

## Information Architecture

```text
JAZEKKER
  Today's Orientation
  Signal Map
    AI & Society
    Europe & Governance
    Human Sustainability
    Future Signals
  Orientation Objects
  Trust & Governance
  AI Cabinet
  Community
  Learning
  News Signals Workspace
```

Navigation must behave like a civic orientation map, not a content wall. The first screen answers: what matters today, why it matters, what changes underneath, what to understand next, and what action should remain under human approval.

## Orientation Flow

```text
signal intake
  -> source check
  -> classifier
  -> policy engine
  -> noise/significance score
  -> orientation object draft
  -> source pack
  -> risk review
  -> human approval gate
  -> distribution proposal
  -> audit record
```

No workflow publishes directly.

## Orientation Object

Every Orientation Object contains:

- Signal: what happened.
- Context: why it matters.
- Noise level: hype versus structural significance.
- Impact horizon: immediate, medium, or long-term.
- Who should care: citizens, professionals, organizations, communities.
- Systemic effects: what changes underneath the surface.
- Next orientation step: what to understand or do next.
- Trust layer: sources, confidence, review status, AI-assisted disclosure.

Example data shape:

```json
{
  "id": "oo_2026_001",
  "status": "draft",
  "title": "EU AI governance moves from principles to enforcement",
  "signal": {"summary": "A new enforcement pattern is emerging."},
  "context": {"why_it_matters": "Organizations must shift from policy awareness to operational compliance."},
  "noise_level": {"score": "medium", "reason": "High attention, but structural implications are real."},
  "impact_horizon": ["immediate", "medium"],
  "who_should_care": ["organizations", "professionals", "communities"],
  "systemic_effects": ["procurement", "auditability", "model risk management"],
  "next_orientation_step": "Review exposure, governance owners, and evidence trail.",
  "trust": {"confidence": "medium", "review_status": "draft", "ai_assisted": true}
}
```

## Homepage System

```text
Hero
  positioning + portal actions
Today's Orientation
  compass + daily loop
Signal Map
  clustered domains and relationships
Orientation Objects
  structured signal cards
AI Cabinet
  governed runtime and coordination layer
Trust & Governance
  visible confidence, sources, review, disclosure
Human Sustainability
  cognitive load, rhythm, attention preservation
Live Signal Collection
  approved RSS to draft objects
Roadmap
  orientation media -> civic infrastructure
```

The homepage is not a feed. It is a map of meaningful signals.

## Design System

- Typography: sober system sans, large calm hero, compact operational headings.
- Spacing: generous section rhythm, dense only where comparison is needed.
- Palette: paper, ink, forest, river, clay, gold, mist.
- Motion: minimal, purposeful, no dopamine loops.
- Interaction density: limited simultaneous choices, clear hierarchy.
- Iconography: restrained navigation and system metaphors.
- Cards: only for repeated objects, metrics, phases, and tools.

Avoid cyberpunk AI visuals, neon gradients, addictive feed mechanics, and dashboard clutter.

## AI Cabinet

AI Cabinet is not a chatbot. It is:

- orientation engine;
- coordination workspace;
- contextual intelligence layer;
- governance-aware AI mediator.

Runtime:

```text
Gateway -> Classifier -> Policy Engine -> Router -> Execution Controller
  -> Audit Layer -> Memory Proposal -> Human Approval
```

AI Cabinet may analyze, draft, critique, route, and propose. It must not publish, send, delete, modify durable policy, or change strategic memory without approved authority.

## Trust And Governance

Trust is visible at object level and workflow level:

- source URL and publisher;
- source type and last checked date;
- confidence indicator;
- AI-assisted disclosure;
- review status;
- approval status;
- audit IDs;
- escalation triggers.

Governance test:

```text
Is this sourced?
Is uncertainty visible?
Is interpretation separated from fact?
Is the user asked for approval before durable action?
Is the audit trail preserved?
```

## Daily Orientation Loop

```text
Morning orientation
  -> 3 to 5 top signals
  -> why they matter
  -> noise versus significance
  -> impact horizon
  -> next orientation step

Midday recalibration
  -> new signal check
  -> changed confidence
  -> risk escalation

Weekly synthesis
  -> pattern memory proposal
  -> strategy implications
  -> editorial and product opportunities
```

The goal is orientation restoration, not engagement.

## Signal Map

The Signal Map shows relationships between events and underlying systems:

```text
AI & Society -------- Europe & Governance
      \                    /
       \                  /
        Human Sustainability
       /                  \
Future Signals -------- AI Cabinet
```

The user should feel: I can see the structure underneath events.

## Technical Architecture

```text
Node.js static generator
  content/orientation/*.json
  ai-cabinet/schemas/*.json
  governance/source-register/*.md
  governance/approvals/*.md
  frontend/*.html
  Cloudflare Pages deployment

FastAPI local runtime
  /jazekker
  /jazekker/news
  /jazekker/news/collect
  /jazekker/news/signals
```

The architecture remains lightweight: JSON content layers, deterministic validation, governed enrichment, and static delivery where possible.

## Content Strategy

Compete on clarity, contextual intelligence, trust, orientation, and systemic understanding.

Do not compete on outrage, speed, clickbait, quantity, or engagement addiction.

## Roadmap

1. Orientation media: homepage, signal map, Orientation Objects, source policy.
2. Contextual intelligence platform: collector, source packs, review queues, evidence trails.
3. AI coordination environment: AI Cabinet workflows, causal mapping, decision support.
4. Civic intelligence infrastructure: partner workspaces, calibration, governance metrics, ecosystem memory.

## Final Test

Every screen, object, and workflow must answer yes:

- Does this reduce chaos?
- Does this improve orientation?
- Does this preserve human judgment?
- Does this increase clarity?
- Does this strengthen trust?
- Does this support sovereignty?
- Does this reduce cognitive fragmentation?

If not, redesign it.

Signature: ASTREB Orientation Intelligence Architecture Engine
