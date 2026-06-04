# Repository And Chat Context Audit: 2026-06-04

## Repository Map

| Location | Status | Finding |
| --- | --- | --- |
| `C:\Users\Viacheslav\OneDrive\Документы\ai_cabinet_mvp` | Primary repository | Active branch `codex/testbox-public-release`; dirty working tree with v0.4/v0.5 additions. |
| `distribution/Разработка_ТБ_v0.5` | Nested repository | Packaged/development copy; should not be treated as root source of truth without explicit decision. |
| `C:\Users\Viacheslav\Documents\Codex` | Codex workspace | No additional Git repos found by this scan. |

## Current Git State Summary

Observed branch:

```text
codex/testbox-public-release
```

Observed base commit:

```text
a313074 Prepare TESTBOX public QMS demo release
```

Important previous gate commit:

```text
fb8269d632d28cae8ac0db546d05a618d7e6dcd1
Implement read-only production preview gate artifacts
```

The working tree contains many pre-existing modified and untracked files. This
audit does not revert or overwrite them.

## Chat Context Available In This Thread

The available chat context shows these governance decisions and artifacts:

| Date/Phase | Decision Or Artifact |
| --- | --- |
| 2026-05-27 | ASTREB META-QMS living mode activated as governance concept. |
| 2026-05-27 | JAZEKKER / ASTREB Notion project page updated with local Foundation MVP state. |
| 2026-05-27 | Security baseline: unified privileged auth, external execution freeze, raw stores excluded, isolated tests. |
| 2026-05-27 | `ASTREB Local Governed MVP v0.3` release gate created. |
| 2026-05-27 | Review branch `release/local-governed-mvp-v0.3` published; PR closed as blocked due cross-lineage diff. |
| 2026-05-27 | Production readiness report created. |
| 2026-05-27 | Read-only production-preview gate artifacts implemented and pushed at `fb8269d...`. |
| 2026-05-28 to 2026-06-04 | Python verification gap remains unresolved in local environment. |
| 2026-06-04 | Current repository state has advanced to TESTBOX public release / v0.4-v0.5 artifact set. |

## Chat Audit Limitation

Only this active thread context is available inside Codex. A full audit of "all
chats" requires exported chat transcripts or Notion/Slack/Teams records made
available as files or connector search results.

Recommended intake convention:

```text
docs/audit/chat-exports/YYYY-MM-DD/<source>.md
```

Each exported chat should be classified as:

- decision;
- requirement;
- deviation;
- implementation evidence;
- strategy/reference;
- superseded/archive.

## Alignment Rule

Chat-derived requirements become authoritative only after they are converted
into one of:

- release gate document;
- governance decision;
- test/evidence artifact;
- issue/task;
- accepted implementation commit.
