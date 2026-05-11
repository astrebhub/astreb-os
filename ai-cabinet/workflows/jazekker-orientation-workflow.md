# JAZEKKER Orientation Workflow

## Purpose

Convert raw signals into governed Orientation Objects and distribution drafts without bypassing human approval.

## Pipeline

```text
signal intake
-> classification
-> source pack
-> orientation object draft
-> governance review
-> editorial review
-> human approval
-> distribution draft
-> publish queue proposal
-> strategic memory proposal
```

## Step Contracts

### 1. Signal Intake

Input: raw link, note, observation, article, regulation, project update, community signal, or manual idea.

Output: normalized signal candidate.

Required fields:

- signal summary;
- signal type;
- why now;
- source references;
- submitter or intake method.

### 2. Classification

Input: normalized signal candidate.

Output: risk level, data class, sensitive domains, required policy.

Governance rule: personal, confidential, legal, medical, financial, political, reputational, privacy, and security domains require review.

### 3. Source Pack

Input: signal candidate and source references.

Output: source records with confidence, verification status, last checked date, and notes on uncertainty.

Governance rule: claims without sources cannot move beyond `needs_sources`.

### 4. Orientation Object Draft

Input: classified signal and source pack.

Output: Orientation Object in `draft` state.

Required schema: `ai-cabinet/schemas/orientation-object.schema.json`.

### 5. Governance Review

Input: draft Orientation Object.

Output: `reviewed`, `needs_governance_review`, or `blocked`.

Governance rule: review must explicitly check unsupported certainty, manipulative framing, privacy risk, and sensitive public claims.

### 6. Editorial Review

Input: reviewed Orientation Object.

Output: clarified object ready for human approval.

Editorial rule: separate fact, interpretation, and speculation.

### 7. Human Approval

Input: reviewed object.

Output: approval record and object state update to `approved` or `blocked`.

Approval schema: `ai-cabinet/schemas/approval.schema.json`.

### 8. Distribution Draft

Input: approved object.

Output: channel drafts for website, newsletter, LinkedIn, Telegram, and RSS.

Governance rule: distribution drafts are not publication.

### 9. Publish Queue Proposal

Input: approved distribution draft.

Output: scheduled proposal requiring approval.

Governance rule: no external publication without an approval record.

### 10. Strategic Memory Proposal

Input: final object, review trail, and response data.

Output: memory proposal.

Governance rule: strategic memory updates require human approval.
