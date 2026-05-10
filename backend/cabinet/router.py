import os
from dataclasses import dataclass
from typing import Any, Dict

from .policy import PolicyDecision


@dataclass
class RouteDecision:
    provider: str
    model: str
    reason: str


class ModelRouter:
    def __init__(self, routing_config: Dict[str, Any]):
        self.routing_config = routing_config

    def route(
        self,
        requested_provider: str,
        mode: str,
        risk_level: str,
        cost_estimated: float,
        policy: PolicyDecision,
    ) -> RouteDecision:
        if policy.local_only or not policy.allow_cloud:
            return RouteDecision("local", "local-safe-fallback", "policy_requires_local")

        if risk_level == "high":
            return RouteDecision("local", "local-safe-fallback", "high_risk_requires_local")

        if requested_provider != "auto":
            return self._requested_route(requested_provider)

        routes = self.routing_config.get("routes", [])
        for route in routes:
            when = route.get("when", {})
            if when.get("risk_level") not in [None, risk_level]:
                continue
            if when.get("mode") not in [None, mode]:
                continue
            if cost_estimated > float(when.get("max_cost", 999999)):
                continue
            return RouteDecision(route["provider"], self._model_for(route["provider"]), route.get("reason", "matched_route"))

        if risk_level == "low" and os.getenv("OPENROUTER_API_KEY"):
            return RouteDecision("openrouter", self._model_for("openrouter"), "low_risk_free_cloud")
        if risk_level == "low" and os.getenv("GEMINI_API_KEY"):
            return RouteDecision("gemini", self._model_for("gemini"), "low_risk_low_cost")
        return RouteDecision("openai", self._model_for("openai"), "default_cloud_route")

    def _requested_route(self, provider: str) -> RouteDecision:
        if provider == "local":
            return RouteDecision("local", "local-safe-fallback", "requested_local")
        return RouteDecision(provider, self._model_for(provider), "requested_provider")

    def _model_for(self, provider: str) -> str:
        if provider == "openai":
            return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        if provider == "gemini":
            return os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        if provider == "openrouter":
            return os.getenv("OPENROUTER_MODEL", "openrouter/free")
        if provider == "ollama":
            return os.getenv("OLLAMA_MODEL", "llama3:latest")
        if provider == "claude":
            return os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet")
        if provider == "deepseek":
            return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        if provider == "mistral":
            return os.getenv("MISTRAL_MODEL", "mistral-small")
        return "local-safe-fallback"
