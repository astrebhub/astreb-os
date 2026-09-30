# ASTREB Guide v0.1 — integration candidate

Status: implementation with offline preview and mocked API tests. Not deployed to astreb.nl. Live model quality and production hosting are not verified.

## What is included

- Dependency-free Node.js server (Node 22 or newer) and embeddable JS/CSS widget.
- NL / EN / RU interface, public facts, source links, bounded conversation context.
- Model-selected navigation limited to strategy, integration, workshops and contact. No URLs, selectors or code accepted from the model.
- Offline mode explicitly says that AI is not connected; topics still work.
- Contact opens a visitor-reviewed email draft, never sends email.
- Current live site is the source of truth for this initial knowledge snapshot. Repository landing content differs from live site and is not silently substituted.

## Preview and tests

```sh
node --test website_guide/server.test.mjs
node website_guide/server.mjs
```

Open http://127.0.0.1:8787. AI stays off until both server-side variables are configured. The preview page represents the public content observed on 2026-09-30, not a replacement of the repository's institutional landing.

## Production integration

1. Identify the actual astreb.nl hosting account and deployed document root. The repository contains a static SFTP landing specification, but no verified connection to the current production host was available in this task.
2. Run this standalone service behind the site's HTTPS reverse proxy. Proxy `/guide/` to the Node process on `127.0.0.1:8787`. Keep the existing site's `/` unchanged. Serve the two widget assets from the service or copy them into the host's `/guide/` path.
3. Configure `OPENAI_API_KEY` as a server secret and `GUIDE_MODEL` as an account-accessible Responses model that supports structured output. Do not place a key in HTML, JavaScript, git, chat, or browser storage. A model is intentionally not selected or activated without account setup.
4. Set `GUIDE_ORIGIN=https://astreb.nl` to the site's canonical origin. Redirect www to the canonical host or deploy a separate explicitly configured instance; there is no wildcard CORS. Configure `GUIDE_STATE_DIR` to a persistent private directory outside the web root, and `GUIDE_DAILY_REQUESTS=100` (or an owner-selected cap). Set a provider-side budget too; request counts are not a euro-denominated spending guarantee.
5. Add these elements before `</body>`:

```html
<link rel="stylesheet" href="/guide/widget.css">
<script defer src="/guide/widget.js" data-endpoint="/guide/api/"></script>
```

6. Mark the corresponding four existing blocks with `data-guide-section="strategy"`, `integration`, `workshops`, `contact`. Exact English headings and the published mailto link are fallback targets for the current live page. Keep ordinary navigation.
7. Review the public knowledge and privacy notice before enabling AI. The UI discloses OpenAI processing; `store:false` is not a promise of zero provider retention. No conversation text is written to disk by this service. Browser history is memory-only and cleared on reload or by the Clear button. Proxies/providers may have their own logging.
8. Verify NL/EN/RU answers against the approved facts, price unknowns, prompt injection attempts, navigation on mobile, provider outage and rate limits with the real configured model. These live checks remain outstanding.

## Deployment limitations

This is a single-process service. Its in-memory per-IP rate limit uses the direct socket peer; behind a reverse proxy all visitors may share that peer and limit. It deliberately ignores untrusted X-Forwarded-For. Configure edge per-visitor rate limits and request-size/time limits before public launch. Use a shared atomic quota store before horizontal scaling. Do not run multiple workers against the same daily quota file. Failed model calls consume quota to avoid retry-based abuse. The 100/day cap persists across restarts when the state directory is retained.

No forms, CRM, appointments, uploads, browsing, private ASTREB memory, or Cabinet tools are exposed. Prompt instructions reduce hallucination risk but cannot guarantee answer correctness. Source IDs and navigation are validated in code. Rich model text is rendered using textContent, never HTML.

## Governance boundary

The existing landing architecture v1 explicitly excluded an agent interface. The user's 2026-09-30 request introduces a proposed public Guide v0.1 extension. This folder isolates that extension for review without rewriting the v1 specification or modifying the existing landing/runtime. It is not represented as passing the internal AI Cabinet governance pipeline. Public knowledge is an explicit allowlist; internal Cabinet state is not accessible.

To uninstall, remove the two widget tags and the reverse proxy route, then stop the separate service. No production data migration is required.

## API reference used

https://developers.openai.com/api/docs/guides/structured-outputs

## Acceptance status

- Implemented: UI, navigation allowlist, public knowledge, API adapter, bounded inputs/output, timeout, generic errors, same-origin check, request quota, manual email draft.
- Verified locally: automated server/adapter tests with stubbed model responses (see `server.test.mjs`).
- Pending: real model/API credentials, production host access, live semantic evaluation, installation on astreb.nl.
