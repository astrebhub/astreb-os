from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class GuideReply:
    answer: str
    suggestions: List[str] = field(default_factory=list)
    recommended_panel: str = "health"


class CabinetGuideAgent:
    """Built-in navigation agent for explaining and operating AI Cabinet safely."""

    def reply(self, message: str, ui_state: Dict[str, Any], runtime: Dict[str, Any]) -> GuideReply:
        text = message.lower().strip()
        if not text:
            return self._welcome(runtime)

        if any(word in text for word in ["pipeline", "пайп", "как работает", "работает"]):
            return GuideReply(
                answer=(
                    "AI Cabinet works as a governed runtime, not as a plain chat. "
                    "A request enters the Gateway, then goes through PII detection, data classification, "
                    "policy, cost governor, model routing, provider/local fallback, output guard, "
                    "action queue, audit, and memory proposal. The model is only one execution engine; "
                    "the Cabinet controls the route and permissions."
                ),
                suggestions=["Show runtime", "Explain policy", "Run safe test"],
                recommended_panel="health",
            )

        if any(word in text for word in ["button", "кноп", "не понимаю", "navigation", "навига"]):
            return GuideReply(
                answer=(
                    "Use the left buttons as control panels. Runtime, Plugins, Local Models, Voice, "
                    "Multimodal, and Personalize are safe public panels. Audit, Actions, Approvals, "
                    "Budget, Policies, Routing, Memory, Evidence, and Observability require the admin token. "
                    "Enter the token from backend/.env into the sidebar before opening admin panels."
                ),
                suggestions=["Show runtime", "Show ASTI connectors", "Explain admin token"],
                recommended_panel="health",
            )

        if any(word in text for word in ["token", "admin", "токен", "доступ"]):
            return GuideReply(
                answer=(
                    "Admin token unlocks governance panels. In your local demo it is stored in backend/.env. "
                    "Do not publish this value. For a public or enterprise version, replace it with real AuthN/AuthZ, "
                    "roles, sessions, and scoped API keys."
                ),
                suggestions=["Show actions", "Show audit", "Explain security"],
                recommended_panel="access",
            )

        if any(word in text for word in ["asti", "connector", "plugin", "плагин", "коннектор"]):
            total = runtime.get("connectors_total", 0)
            return GuideReply(
                answer=(
                    f"ASTI is the Agentic Secure Tool Interface. It is the safe hands layer of AI Cabinet. "
                    f"This runtime currently sees {total} connector manifests. They are draft/report only until "
                    "a connector is signed and an action is approved. This is how Cabinet keeps AI actions controlled."
                ),
                suggestions=["Show ASTI connectors", "Explain signed connector", "Create action scenario"],
                recommended_panel="plugins",
            )

        if any(word in text for word in ["model", "ollama", "openrouter", "gemini", "модель", "модел"]):
            return GuideReply(
                answer=(
                    "Model routing is policy-driven. Public low-risk tasks may use cloud/free routes such as "
                    "OpenRouter or Gemini when keys exist. Sensitive or high-risk tasks stay local or use "
                    "local-safe-fallback. Ollama gives local models; the fallback keeps the pipeline alive even "
                    "when cloud keys are missing."
                ),
                suggestions=["Show local models", "Show routing", "Run public content test"],
                recommended_panel="localRuntime",
            )

        if any(word in text for word in ["microsoft", "outlook", "teams", "office"]):
            return GuideReply(
                answer=(
                    "Microsoft 365 Agent can draft Outlook emails, calendar proposals, Teams updates, Planner tasks, "
                    "and OneDrive/SharePoint workflows. It does not send, post, create meetings, share files, "
                    "or call Microsoft Graph until a signed connector and approval record exist."
                ),
                suggestions=["Prepare Outlook draft", "Show ASTI connectors", "Explain approval"],
                recommended_panel="plugins",
            )

        if any(word in text for word in ["test", "тест", "сценар"]):
            return GuideReply(
                answer=(
                    "A good safe test is: choose provider local or ollama, mode microsoft_ops or github_ops, "
                    "access level 3, and ask the agent to prepare a proposal without external actions. "
                    "The action should enter pending_approval and can be executed only as a local report artifact."
                ),
                suggestions=["Run safe test", "Show actions", "Show approvals"],
                recommended_panel="actions",
            )

        if any(word in text for word in ["security", "безопас", "risk", "риск"]):
            return GuideReply(
                answer=(
                    "Security is enforced before model execution: PII masking, data classification, YAML policy, "
                    "local-only routing for sensitive tasks, output scanning, action approval, and audit logging. "
                    "The key rule is: the model asks, the microkernel decides."
                ),
                suggestions=["Show policy", "Show audit", "Explain local-only"],
                recommended_panel="policy",
            )

        return GuideReply(
            answer=(
                "I am the Cabinet Guide Agent. I can explain the pipeline, buttons, models, policies, agents, "
                "ASTI connectors, Microsoft mode, tests, and safe next steps. Ask me what you want to do, "
                "and I will translate it into a governed Cabinet action."
            ),
            suggestions=["Explain pipeline", "Show runtime", "Show ASTI connectors"],
            recommended_panel="health",
        )

    def _welcome(self, runtime: Dict[str, Any]) -> GuideReply:
        return GuideReply(
            answer=(
                "I live inside AI Cabinet as the navigation agent. I know the runtime, agents, policies, "
                f"and ASTI connector layer. Current connector manifests: {runtime.get('connectors_total', 0)}. "
                "Tell me what you want to configure or understand."
            ),
            suggestions=["Explain pipeline", "Show runtime", "Show ASTI connectors"],
            recommended_panel="health",
        )
