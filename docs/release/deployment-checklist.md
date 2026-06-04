# Deployment Checklist: Read-Only Governed Preview

Date: 2026-05-27
Target: future first production preview; not yet authorized

## Release Governance

- [x] Local freeze branch created: `release/local-governed-mvp-v0.3`.
- [x] External execution remains off by default.
- [x] Local canonical boundaries and open risks documented.
- [x] Repository classification, inventory, trust boundary, state model,
  incident response and public-claims policy documented.
- [x] Controlled snapshot remote selected: `origin` (`astrebhub/astreb-os`) after access verification.
- [ ] Human integration decision recorded before merging the review branch.
- [ ] Controlled commit reviewed and approved.
- [ ] Pull request reviewed with CI evidence.
- [ ] Security reviewer approves preview gate.
- [ ] Strategic owner approves deployment.

## Repository And CI

- [x] `.env.example` contains placeholders only.
- [x] `.env` and `.env.production` are excluded from Git.
- [x] Raw runtime stores are excluded from Git.
- [x] Local CI workflow includes validation, tests, dependency audit and artifact build.
- [x] CI workflow includes read-only production-preview config validation.
- [ ] Workflow executes successfully on the selected remote branch.
- [ ] Build artifact is retained with commit SHA and test evidence.

## Public Preview Scope

- [ ] Deploy only approved JAZEKKER public/static preview routes.
- [ ] Present AI Cabinet and TESTBOX as explanations/demonstrations.
- [ ] Keep runtime endpoints operator-authorized.
- [ ] Do not claim production autonomous capability.
- [ ] Do not ingest unreviewed live source data.

## Runtime And Security

- [x] TESTBOX runtime API fails closed without an admin token locally.
- [x] ASTI administrative API fails closed without an admin token locally.
- [x] META-QMS decisions require authorization locally.
- [x] Auth denials are logged without tokens locally.
- [x] Production-preview startup rejects enabled external execution in config.
- [ ] Implement rate limiting and abuse monitoring.
- [ ] Configure HTTPS and hardened ingress.
- [ ] Move secrets to managed production configuration.
- [ ] Replace local stores with protected durable persistence.
- [ ] Verify backup, retention and recovery for audit/session data.

## External Execution Explicit Deny List

- [x] No Telegram delivery in the preview.
- [x] No WhatsApp delivery in the preview.
- [x] No email sending in the preview.
- [x] No autonomous publishing or distribution.
- [x] No self-approved or self-applied META-QMS changes.

## Separate Future ASTI Release Gate

Before enabling any real executor:

- [ ] Define execution allowlist.
- [ ] Validate human approval UI and identity controls.
- [ ] Provide dry-run mode evidence.
- [ ] Provide execution audit and reconciliation process.
- [ ] Document revoke switch and rollback strategy.
- [ ] Implement abuse detection.
- [ ] Record separate human governance decision.
