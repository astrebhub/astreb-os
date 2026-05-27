# Release Gate v0.3: ASTREB Local Governed MVP

Date: 2026-05-27
Release designation: `ASTREB Local Governed MVP v0.3`
Gate status: Local freeze branch prepared; production release not approved
Canonical freeze branch: `release/local-governed-mvp-v0.3`
Branch base commit at gate opening: `b8a62934fe4564484793cadf0382696c15c4fef2`

## Purpose

This gate records a locally implemented and tested governed AI orientation
prototype with controlled execution boundaries and security-baseline controls.
The controlled snapshot branch was subsequently published for review as
commit `43ad6a08388f8931f89fd7095560ab8d9183c744`; this does not represent a
production deployment or a live external-execution release.

## Repository State At Gate Opening

- The freeze branch was created locally on 2026-05-27 from commit
  `b8a62934fe4564484793cadf0382696c15c4fef2`.
- The working tree already contained modified and untracked Foundation,
  TESTBOX, ASTI, META-QMS, documentation and governance materials.
- Those changes require controlled review and an intentional commit before the
  branch can become an immutable reproducible snapshot.
- The duplicate `_incoming/` starter-kit copy and stale local Node preview
  helper were identified as non-canonical and excluded from the snapshot.
- Two configured remotes exist: `jazekker` and `origin`. Publication
  verification on 2026-05-27 found `slakov/jazekker` unavailable to the
  connected GitHub context, while `astrebhub/astreb-os` exposes the existing
  `ai-cabinet-full` branch. The controlled snapshot publication target is
  therefore `origin` (`astrebhub/astreb-os`) as a separate review branch.

## Canonical System Boundary

```text
JAZEKKER        = human-facing orientation interface
AI Cabinet      = governed intelligence runtime / governance substrate
TESTBOX         = observable AI governance and quality environment
ASTI            = controlled execution boundary
ASTREB META-QMS = reviewed continuous-improvement loop
```

## Current Gate Decision

Approved locally for continued controlled validation:

- Foundation MVP public orientation surfaces;
- static read-only governed preview positioning;
- TESTBOX runtime only behind admin-token authorization;
- META-QMS proposal visualization and human decision recording behind auth;
- external execution frozen by default;
- isolated runtime test storage;
- anonymized repository audit reports only.

Not approved:

- production deployment;
- autonomous publication or distribution;
- Telegram, WhatsApp or email execution;
- self-modifying or self-approved runtime changes;
- any claim that the published review snapshot is a production release.

## Required Before Next Gate

1. Review the complete controlled commit scope before publication.
2. Create a clean controlled commit on the freeze branch.
3. Execute CI with tests and dependency/security scanning after publication to `origin`.
4. Implement durable security-event and audit storage for production use.
5. Add rate limiting and deployment-grade secret management.
6. Complete human security and release-governance approval.

## Governing Principles

- Intelligence is not authority.
- Governance before execution.
- Orientation over automation.
- Human sovereignty remains primary.
- No approval means no execution.
