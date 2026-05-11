# Deployment Plan

## Goal

Attach a safe activation and rollout layer to the JAZEKKER strategic package.

The package should support:

- placement into a repository;
- creation of recommended project folders;
- future nightly orientation draft automation;
- future GitHub Actions integration;
- manual review before publishing.

## What Must Not Happen

- No script should publish content automatically.
- No script should run from email automatically.
- No AI output should bypass human approval.
- No deployment should overwrite production files without review.

## Repository Placement

Recommended strategy location:

```text
docs/strategy/jazekker/
```

Recommended runtime folders:

```text
content/
  orientation/
  briefings/
  articles/
  explainers/
  governance-notes/
  future-signals/

ai-cabinet/
  prompts/
  workflows/
  schemas/
  audit/
  memory/

distribution/
  website/
  linkedin/
  telegram/
  newsletter/
  rss/

governance/
  policies/
  approvals/
  source-register/
```

## Rollout Steps

### Phase 1 - Manual Placement

Copy this package into the repository and commit it as strategy documentation.

### Phase 2 - Structure Creation

Create recommended folders and placeholders.

### Phase 3 - Content Schema

Add schemas for:

- Orientation Object;
- Source;
- Approval;
- Distribution metadata;
- Strategic memory note.

### Phase 4 - Nightly Orientation

Use `nightly-orientation-task.example.ps1` only as a future template.

The nightly job should create drafts only.

Human approval remains required before publication.

### Phase 5 - CI/CD

Use `github-actions-nightly-orientation.yml` as a future GitHub Actions template.

Do not enable production publishing until governance checks are implemented.
