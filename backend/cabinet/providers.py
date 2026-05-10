import os
from dataclasses import dataclass
from typing import Dict, Optional

import httpx

from . import config
from .secrets_vault import SecretsVault


@dataclass
class ProviderResult:
    text: str
    model: str
    tokens_used: int
    cost_real: float


class ProviderAdapter:
    def __init__(self, secrets_vault: Optional[SecretsVault] = None):
        self.secrets_vault = secrets_vault

    def _secret(self, vault_name: str, env_name: str) -> str:
        if self.secrets_vault:
            value = self.secrets_vault.get(vault_name)
            if value:
                return value
        return os.getenv(env_name, "")

    async def call(self, provider: str, model: str, prompt: str) -> ProviderResult:
        if provider == "openai":
            return await self._openai(model, prompt)
        if provider == "gemini":
            return await self._gemini(model, prompt)
        if provider == "openrouter":
            return await self._openrouter(model, prompt)
        if provider == "ollama":
            return await self._ollama(model, prompt)
        if provider in ["claude", "deepseek", "mistral", "manual"]:
            return await self._local("local-safe-fallback", prompt, f"{provider} adapter not configured; local safe fallback used.")
        return await self._local(model, prompt)

    async def _openai(self, model: str, prompt: str) -> ProviderResult:
        openai_key = self._secret("openai_key", "OPENAI_API_KEY")
        if not openai_key:
            return await self._local("local-safe-fallback", prompt, "OpenAI key missing; local safe fallback used.")

        payload = {
            "model": model,
            "input": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": prompt},
            ],
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        text = data.get("output_text") or str(data)[:2000]
        usage = data.get("usage", {})
        tokens = int(usage.get("total_tokens", max(1, len(prompt + text) // 4)))
        return ProviderResult(text=text, model=model, tokens_used=tokens, cost_real=round(tokens * 0.0000004, 6))

    async def _gemini(self, model: str, prompt: str) -> ProviderResult:
        gemini_key = self._secret("gemini_key", "GEMINI_API_KEY")
        if not gemini_key:
            return await self._local("local-safe-fallback", prompt, "Gemini key missing; local safe fallback used.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
        payload = {"contents": [{"parts": [{"text": f"{self._system_prompt()}\n\n{prompt}"}]}]}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            text = str(data)[:2000]
        tokens = max(1, len(prompt + text) // 4)
        return ProviderResult(text=text, model=model, tokens_used=tokens, cost_real=round(tokens * 0.0000002, 6))

    async def _openrouter(self, model: str, prompt: str) -> ProviderResult:
        openrouter_key = self._secret("openrouter_key", "OPENROUTER_API_KEY")
        if not openrouter_key:
            return await self._local(
                "local-safe-fallback",
                prompt,
                "OpenRouter key missing; local safe fallback used.",
            )

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://127.0.0.1:8000"),
            "X-Title": os.getenv("OPENROUTER_APP_TITLE", "AI Cabinet"),
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            text = str(data)[:2000]
        usage = data.get("usage", {})
        tokens = int(usage.get("total_tokens", max(1, len(prompt + text) // 4)))
        pricing_is_free = model == "openrouter/free" or model.endswith(":free")
        cost = 0.0 if pricing_is_free else round(tokens * 0.0000005, 6)
        model_used = data.get("model") or model
        return ProviderResult(text=text, model=model_used, tokens_used=tokens, cost_real=cost)

    async def _local(self, model: str, prompt: str, prefix: str = "Local fallback response.") -> ProviderResult:
        governed_draft = self._local_governed_draft(prompt)
        if governed_draft:
            text = governed_draft
            tokens = max(1, len(prompt + text) // 4)
            return ProviderResult(text=text, model=model, tokens_used=tokens, cost_real=0.0)

        text = (
            f"{prefix}\n\n"
            "AI Cabinet processed this task through the local safe fallback. "
            "No external provider received the prompt.\n\n"
            f"Draft:\n{prompt[:1200]}"
        )
        tokens = max(1, len(prompt + text) // 4)
        return ProviderResult(text=text, model=model, tokens_used=tokens, cost_real=0.0)

    def _local_governed_draft(self, prompt: str) -> str:
        lowered = prompt.lower()
        if "mode: microsoft_ops" in lowered and "outlook" in lowered and "email" in lowered:
            return (
                "Microsoft 365 governed draft prepared locally.\n\n"
                "No external provider received the prompt. No email was sent. "
                "No Microsoft Graph call was made.\n\n"
                "## Outlook Draft\n\n"
                "To: [MASKED_EMAIL]\n\n"
                "Subject: Current status of the AI Cabinet project\n\n"
                "Body:\n\n"
                "Hello,\n\n"
                "I wanted to share a concise update on the current state of the AI Cabinet project.\n\n"
                "AI Cabinet is now running as a local governed AI control layer with a FastAPI backend "
                "and browser-based control center. The current build includes policy enforcement, "
                "PII masking, local/cloud routing logic, audit logging, action approval workflow, "
                "agent registry, plugin manifests, and a local-safe execution path for approved action reports.\n\n"
                "Recent progress includes dedicated governed agents for GitHub operations, local computer "
                "control planning, and Microsoft 365 workflows. The Microsoft 365 agent can prepare Outlook, "
                "Calendar, Teams, Planner, OneDrive, and SharePoint action proposals, but it does not send, "
                "post, create events, share files, or call Microsoft Graph without explicit approval and a signed connector.\n\n"
                "The system is currently suitable for controlled demonstrations of governance, routing, "
                "auditability, and human-in-the-loop execution. The next technical milestone is connecting "
                "real Microsoft 365 APIs through OAuth, scoped permissions, signed connector manifests, "
                "and approval-gated execution.\n\n"
                "Best regards,\n"
                "Viacheslav\n\n"
                "## Governance Notes\n\n"
                "- Classification: personal/high risk because the request contains an email recipient.\n"
                "- Processing: local only.\n"
                "- External action: none.\n"
                "- Required next step: human review before sending."
            )
        return ""

    async def _ollama(self, model: str, prompt: str) -> ProviderResult:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{config.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": model,
                        "prompt": f"{self._system_prompt()}\n\n{prompt}",
                        "stream": False,
                        "options": {"num_ctx": 768, "num_predict": 256, "num_thread": 2},
                    },
                )
            if response.status_code >= 400:
                return await self._local("local-safe-fallback", prompt, "Ollama returned an error; local safe fallback used.")
            data = response.json()
            text = data.get("response", "")
            tokens = int(data.get("eval_count") or max(1, len(prompt + text) // 4))
            return ProviderResult(text=text, model=model, tokens_used=tokens, cost_real=0.0)
        except Exception:
            return await self._local("local-safe-fallback", prompt, "Ollama unavailable; local safe fallback used.")

    def _system_prompt(self) -> str:
        return (
            "You are inside AI CABINET v0.2, a secure AI firewall/control layer. "
            "Return practical draft output only. Never claim that real-world actions were executed. "
            "Do not reveal or reconstruct masked values."
        )


def build_provider_prompt(
    masked_input: str,
    mode: str,
    policy_name: str,
    classification: Dict[str, str],
    governance_context: Optional[Dict[str, str]] = None,
) -> str:
    governance_context = governance_context or {}
    return (
        f"Mode: {mode}\n"
        f"Dialog mode: {governance_context.get('dialog_mode', 'operator')}\n"
        f"Agent: {governance_context.get('agent_id', 'default_agent')}\n"
        f"Profile: {governance_context.get('profile_id', 'owner_default')}\n"
        f"Policy: {policy_name}\n"
        f"Data class: {classification['data_class']}\n"
        f"Risk: {classification['risk_level']}\n\n"
        "Governance context:\n"
        f"- User preferences: {governance_context.get('profile_summary', 'Use default AI Cabinet preferences.')}\n"
        f"- Dialog contract: {governance_context.get('dialog_contract', 'Use governed, practical output.')}\n"
        f"- Agent instructions: {governance_context.get('agent_instructions', 'Follow AI Cabinet governance.')}\n"
        f"- Allowed actions: {governance_context.get('allowed_actions', 'draft, analyze, propose')}\n"
        f"- Forbidden actions: {governance_context.get('forbidden_actions', 'publish, send, delete, bypass policy')}\n\n"
        f"User task with protected data:\n{masked_input}"
    )
