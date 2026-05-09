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

    async def _local(self, model: str, prompt: str, prefix: str = "Local fallback response.") -> ProviderResult:
        text = (
            f"{prefix}\n\n"
            "AI Cabinet processed this task through the local safe fallback. "
            "No external provider received the prompt.\n\n"
            f"Draft:\n{prompt[:1200]}"
        )
        tokens = max(1, len(prompt + text) // 4)
        return ProviderResult(text=text, model=model, tokens_used=tokens, cost_real=0.0)

    async def _ollama(self, model: str, prompt: str) -> ProviderResult:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{config.OLLAMA_BASE_URL}/api/generate",
                    json={"model": model, "prompt": f"{self._system_prompt()}\n\n{prompt}", "stream": False},
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


def build_provider_prompt(masked_input: str, mode: str, policy_name: str, classification: Dict[str, str]) -> str:
    return (
        f"Mode: {mode}\n"
        f"Policy: {policy_name}\n"
        f"Data class: {classification['data_class']}\n"
        f"Risk: {classification['risk_level']}\n\n"
        f"User task with protected data:\n{masked_input}"
    )
