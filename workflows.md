# AI Cabinet Governed Workflow Profiles

Project: AI Cabinet
Version: 1.0
Profile: Editorial Governance Workspace

## Workflow Rule

Policy executes before generation. Human approval is required for critical actions, high-risk editorial outputs, durable memory updates, and external publication.

## Universal Workflow Skeleton

```text
Intake
  |
  v
Normalize
  |
  v
Classify domain, intent, data class, and risk
  |
  v
Apply policy
  |
  v
Route to workflow and agent
  |
  v
Execute controlled steps
  |
  v
Quality and risk review
  |
  v
Human approval if required
  |
  v
Audit
  |
  v
Memory proposal
  |
  v
Output
```

## Workflow Types

### Editorial Intake

Purpose: Convert raw input into a governed content task.

Steps:

- Capture request, source, language, and destination.
- Classify topic and editorial mode.
- Estimate risk.
- Identify required evidence.
- Assign workflow owner or agent.
- Create approval requirements.

Outputs:

- Content brief.
- Risk score.
- Evidence checklist.
- Recommended workflow.

### Article Draft

Purpose: Produce a reviewable article draft.

Steps:

- Validate brief.
- Request source pack from Research Agent.
- Generate outline.
- Draft article.
- Separate fact, interpretation, and open uncertainty.
- Run Editor Agent review.
- Run Risk Sentinel review.
- Place in approval queue.

Outputs:

- Draft article.
- Fact/interpretation map.
- Risk notes.
- Approval record.

### Article Revision

Purpose: Improve an existing draft while preserving governance.

Steps:

- Load current draft and audit context.
- Classify requested changes.
- Check whether changes alter meaning.
- Apply revision.
- Run quality review.
- Run policy review if risk increased.

Outputs:

- Revised draft.
- Change summary.
- Remaining issues.

### Translation And Localization

Purpose: Produce multilingual content without losing meaning.

Steps:

- Identify source and target language.
- Detect sensitive claims and terminology.
- Translate.
- Localize headings and metadata.
- Flag nuance changes.
- Request human review for high-risk material.

Outputs:

- Translated content.
- Terminology notes.
- Nuance warnings.

### SEO Optimization

Purpose: Improve discovery while protecting editorial integrity.

Steps:

- Identify search intent.
- Propose title, slug, meta description, and headings.
- Suggest internal links.
- Check for clickbait or manipulative framing.
- Send sensitive title changes for approval.

Outputs:

- SEO package.
- Integrity check.
- Approval requirement.

### Evidence Review

Purpose: Verify whether content has sufficient support.

Steps:

- Extract factual claims.
- Map each claim to evidence.
- Score source reliability.
- Flag unsupported claims.
- Recommend wording changes for uncertainty.

Outputs:

- Evidence matrix.
- Claim confidence scores.
- Correction suggestions.

### Community Moderation

Purpose: Govern community interactions.

Steps:

- Classify message or thread.
- Detect abuse, personal data, legal risk, and escalation signals.
- Draft response or moderation recommendation.
- Require approval for sanctions or sensitive public replies.

Outputs:

- Moderation classification.
- Draft response.
- Escalation recommendation.

### Newsletter Generation

Purpose: Convert editorial output into a curated newsletter.

Steps:

- Select candidate items.
- Score relevance and freshness.
- Generate concise summaries.
- Check for duplication and unsupported claims.
- Prepare subject lines.
- Require approval before send.

Outputs:

- Newsletter draft.
- Item rationale.
- Approval record.

### Trend Radar

Purpose: Detect emerging topics worth editorial attention.

Steps:

- Collect candidate signals.
- Filter noise and duplicates.
- Cluster topics.
- Score relevance to AI Cabinet.
- Propose editorial opportunities.

Outputs:

- Trend brief.
- Opportunity list.
- Confidence notes.

### Strategic Planning

Purpose: Translate signals and operations into ecosystem decisions.

Steps:

- Gather editorial, community, analytics, and governance context.
- Identify constraints and opportunities.
- Generate scenarios.
- Evaluate risk.
- Recommend next actions.
- Store only approved strategic memory.

Outputs:

- Strategic brief.
- Scenario map.
- Decision log proposal.

### GitHub Operations

Purpose: Coordinate repository work without bypassing governance.

Steps:

- Classify repository task, target repo, branch, and external-action risk.
- Inspect available repository, issue, pull request, CI, and release context.
- Draft issue, branch plan, pull request summary, review response, CI diagnosis, or release notes.
- Separate observed repository facts from proposed actions.
- Route push, merge, release, deletion, settings, or secret-related work to the approval queue.
- Audit the decision and attach evidence or command/output references where available.

Outputs:

- GitHub operations brief.
- Proposed issue, pull request, branch, or release package.
- CI or review-risk summary.
- Approval queue item for external repository actions.

## Approval Levels

- Low risk: agent may draft and recommend.
- Medium risk: human review before publish or external action.
- High risk: human approval required before output is treated as operational.
- Critical risk: block by default and escalate to owner/admin.

## Done Criteria For Phase 1

Phase 1 is complete when AI Cabinet can:

- Accept editorial requests.
- Classify risk and domain.
- Apply policy before generation.
- Route to a specialist agent.
- Produce drafts and reviews.
- Capture evidence and audit records.
- Queue high-risk work for approval.
- Propose memory updates without applying them autonomously.
