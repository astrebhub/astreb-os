# Incident Response Plan: ASTREB / JAZEKKER v0.3 Preview

Date: 2026-05-27
Scope: read-only governed production preview incidents

## Response Principles

- Preserve human authority.
- Stop external action first.
- Preserve audit evidence.
- Rotate secrets rather than editing logs.
- Record every incident as a governance deviation and META-QMS learning input.

## Severity Levels

| Severity | Meaning | Initial Response |
| --- | --- | --- |
| SEV-1 | Unauthorized external execution, secret exposure, service compromise | Disable ingress, revoke tokens, preserve evidence, notify owner/security reviewer. |
| SEV-2 | Privileged API abuse, audit corruption, privilege escalation attempt | Disable affected endpoint or token, preserve logs, investigate scope. |
| SEV-3 | Hallucinated capability claim, runtime instability, UI misrepresentation | Correct claim/state, record deviation, add regression/documentation fix. |

## Incident Playbooks

### Token Leak

1. Revoke leaked token immediately.
2. Rotate `ADMIN_API_TOKEN`, `TELEGRAM_WEBHOOK_SECRET` and any affected secrets.
3. Search audit/application logs for use of the token boundary.
4. Record a security incident and correction.
5. Re-run privileged rejection tests.

### Unauthorized Execution

1. Disable external execution flag and ingress.
2. Revoke external service credentials.
3. Preserve ASTI audit and action queue state.
4. Identify action ID, actor, approval record and execution attempt ID.
5. Execute rollback/compensation plan if an external side effect occurred.
6. Keep ASTI frozen until a new governance decision.

### Audit Corruption

1. Stop writes to affected store.
2. Preserve corrupted file and filesystem metadata.
3. Compare with Git evidence and available backups.
4. Append a corruption incident record in a separate trusted channel.
5. Do not edit historical audit rows in place.

### API Abuse

1. Revoke or rotate admin token.
2. Apply temporary ingress block.
3. Review request source, endpoint, session and event IDs.
4. Add rate limiting before re-exposure.

### Hallucinated Execution Or Capability Claim

1. Correct public/internal claim.
2. Record governance deviation.
3. Add public-claims policy reference to the relevant surface.
4. Add regression or documentation guard where possible.

### Privilege Escalation

1. Disable affected privileged route or token.
2. Preserve request/audit evidence.
3. Validate all fail-closed paths.
4. Require security reviewer sign-off before re-enabling.

### Service Compromise

1. Take service offline or isolate network ingress.
2. Rotate all secrets.
3. Preserve disk/runtime evidence.
4. Rebuild from clean commit and verified dependency set.
5. Reopen only after security review.

### Runtime Instability

1. Stop accepting new privileged runtime actions.
2. Preserve queue and audit state.
3. Reproduce locally with isolated storage.
4. Add regression test before resuming preview.

## Required Incident Record

Each incident record must include:

- timestamp;
- reporter;
- affected route/service;
- affected data or action IDs;
- immediate containment;
- audit evidence location;
- decision owner;
- follow-up controls;
- public communication requirement if any.
