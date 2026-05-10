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

## Local Free Model Families

AI Cabinet treats these as first-class local/free model families through the
Ollama/local runtime layer:

| Family | Example Ollama model | Best use |
| --- | --- | --- |
| Llama 3 | `llama3:latest` | General local assistant and private drafting |
| Mistral | `mistral:latest` | Fast local drafting and analysis |
| Phi | `phi3:latest` | Lightweight local tasks on weaker machines |
| Qwen | `qwen2.5-coder:latest` | Coding, structured tasks, and technical drafting |
| Gemma | `gemma2:2b` | Lightweight general local processing |

These models are free to run locally in the sense that AI Cabinet does not pay
an API provider for them. They still require local CPU/GPU resources and enough
RAM for the selected model.

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
LOCAL_GENERAL_MODEL=llama3:latest
LOCAL_CODER_MODEL=qwen2.5-coder:latest
LOCAL_REASONING_MODEL=deepseek-r1:latest
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
