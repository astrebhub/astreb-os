# Free Models Setup

AI Cabinet supports a free/local-first model stack without putting API keys in source code.

## Recommended Free Stack

1. **Ollama local**
   - Provider: `ollama`
   - Model example: `qwen2.5:0.5b`
   - Cost: local compute only
   - Best for: private, sensitive, offline, draft workflows

2. **OpenRouter Free Router**
   - Provider: `openrouter`
   - Model: `openrouter/free`
   - Cost: zero-cost free-model routing when the account/model is available
   - Best for: public, low-risk experimentation
   - Requires: `OPENROUTER_API_KEY`

3. **Gemini API**
   - Provider: `gemini`
   - Model example: `gemini-2.0-flash`
   - Cost: depends on current Google tier and quota
   - Best for: public/low-risk cloud drafting
   - Requires: `GEMINI_API_KEY`

## Governance Rules

- Personal, confidential, or high-risk tasks stay local.
- PII is masked before any provider call.
- OpenRouter/Gemini should be used only for public or low-risk tasks unless policy explicitly allows more.
- Free cloud model availability and rate limits can change. Keep this layer as best-effort, not a production SLA.

## Environment Variables

```env
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/free
OPENROUTER_SITE_URL=http://127.0.0.1:8000
OPENROUTER_APP_TITLE=AI Cabinet

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash

OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:0.5b
```

## Runtime Test

Use provider `openrouter` for a public task:

```text
Write a short public summary of AI Cabinet as an AI governance control plane.
```

Expected behavior:

- If `OPENROUTER_API_KEY` exists, AI Cabinet calls `openrouter/free`.
- If no key exists, AI Cabinet safely falls back to `local-safe-fallback`.
- Audit log records provider, model, estimated tokens, and cost.
