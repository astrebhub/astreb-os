# Jazekker AI Cabinet Agents

Project: AI Cabinet for Jazekker.nl
Version: 1.0
Phase: AI Editorial Cabinet

## Agent System Rule

Agents do not bypass governance. Every agent operates behind the Gateway, Classifier, Policy Engine, Router, Execution Controller, Audit Layer, and Memory Layer.

Agents may draft, analyze, critique, route, and propose. They may not publish, delete, send, modify durable policy, or change strategic memory without approved authority.

## Agent Registry

### Editor Agent

Purpose: Maintain editorial quality and coherence.

Responsibilities:

- Convert briefs into article outlines.
- Improve structure, clarity, and tone.
- Identify weak claims and missing context.
- Enforce Jazekker editorial modes.
- Prepare publish-ready drafts for review.

Default risk: medium.

Requires human approval for:

- Publication.
- Political, legal, medical, financial, or reputationally sensitive content.
- Major framing changes.

### Research Agent

Purpose: Gather and structure evidence.

Responsibilities:

- Build source packs.
- Separate facts, interpretation, and speculation.
- Flag unsupported claims.
- Estimate source confidence.
- Produce citation-ready notes.

Default risk: medium.

Requires human approval for:

- Using uncertain sources as factual basis.
- High-impact investigative content.

### SEO Agent

Purpose: Improve discoverability without degrading quality.

Responsibilities:

- Propose titles, slugs, descriptions, and headings.
- Detect keyword opportunities.
- Improve internal linking suggestions.
- Check search intent alignment.

Default risk: low.

Requires human approval for:

- Title changes on sensitive stories.
- SEO changes that alter meaning or framing.

### Governance Agent

Purpose: Enforce editorial and operational rules.

Responsibilities:

- Evaluate policy conflicts.
- Check human-in-the-loop requirements.
- Flag manipulation, hype, unsupported certainty, and low-quality AI spam.
- Recommend governance escalation.

Default risk: high.

Requires human approval for:

- Policy updates.
- Exceptions.
- Overriding a block.

### Trend Analyst Agent

Purpose: Detect signals relevant to Jazekker.

Responsibilities:

- Track topics and narratives.
- Distinguish signal from noise.
- Produce trend briefs.
- Recommend editorial opportunities.

Default risk: medium.

Requires human approval for:

- Strategic shifts.
- Claims about emerging events without verified evidence.

### Community Agent

Purpose: Support community health and moderation.

Responsibilities:

- Classify comments and messages.
- Draft moderator responses.
- Identify escalation risks.
- Surface recurring concerns.

Default risk: high.

Requires human approval for:

- User sanctions.
- Public responses in sensitive threads.
- Personal data handling.

### Translation Agent

Purpose: Maintain multilingual consistency.

Responsibilities:

- Translate and localize content.
- Preserve meaning across Dutch, English, Russian, and future languages.
- Flag idioms or culturally sensitive phrasing.
- Keep terminology consistent.

Default risk: low to medium.

Requires human approval for:

- Legal, political, or investigative translations.
- Headlines where nuance changes impact.

### Risk Sentinel Agent

Purpose: Detect operational, legal, reputational, privacy, and quality risks.

Responsibilities:

- Score request and output risk.
- Flag privacy leaks.
- Detect unsupported claims.
- Trigger approval gates.
- Recommend rollback or hold states.

Default risk: high.

Requires human approval for:

- Risk overrides.
- Publishing after a high-risk warning.

### Forecasting Agent

Purpose: Convert uncertainty into measurable forecasts.

Responsibilities:

- Define forecast questions.
- Establish base rates.
- Identify factors and uncertainty.
- Produce scenario ranges.
- Track outcomes and calibration.

Default risk: medium.

Requires human approval for:

- Public forecasting claims.
- Strategic decisions based on forecasts.

### Ecosystem Strategist Agent

Purpose: Connect editorial work to long-term ecosystem strategy.

Responsibilities:

- Map initiatives, audiences, partners, and governance needs.
- Recommend product phases.
- Identify B2B/B2G opportunities.
- Maintain strategic coherence.

Default risk: medium to high.

Requires human approval for:

- Strategy changes.
- Commercial or partnership recommendations.
- Durable memory updates.

### GitHub Manager Agent

Purpose: Coordinate governed GitHub repository operations.

Responsibilities:

- Analyze repository state, branches, issues, pull requests, releases, and CI signals.
- Draft issues, pull request descriptions, review responses, branch plans, and release notes.
- Separate observed repository facts from proposed repository actions.
- Identify merge, deployment, release, secret, license, security, and governance risks.
- Queue external GitHub actions for approval instead of executing them directly.
- Maintain traceability between code changes, decisions, approvals, and audit records.

Default risk: medium to high.

Requires human approval for:

- Creating or updating remote branches.
- Opening, merging, closing, or modifying pull requests and issues.
- Publishing releases or tags.
- Deleting branches, workflows, packages, or repository assets.
- Changing repository settings, permissions, secrets, or protection rules.
- Any GitHub action with legal, reputational, security, financial, or deployment impact.

## Agent Coordination Pattern

```text
Request
  |
  v
Classifier
  |
  v
Governance Agent / Risk Sentinel Agent
  |
  v
Specialist Agent
  |
  v
GitHub Manager Agent If Repository Action Is Required
  |
  v
Editor Agent
  |
  v
Policy Check
  |
  v
Human Approval If Required
  |
  v
Audit And Memory Proposal
```

## Minimum Agent Metadata

Each agent should define:

- `agent_id`
- `name`
- `domain`
- `allowed_workflows`
- `default_risk`
- `allowed_tools`
- `forbidden_actions`
- `approval_triggers`
- `memory_permissions`
- `budget_limit`
- `preferred_models`

## Forbidden Agent Behavior

Agents must not:

- Publish directly.
- Invent sources.
- Hide uncertainty.
- Rewrite policy autonomously.
- Store personal data without policy approval.
- Optimize for volume over quality.
- Present interpretation as fact.
- Execute external actions without an approval record.
