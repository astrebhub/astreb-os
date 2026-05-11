from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class GuideReply:
    answer: str
    suggestions: List[str] = field(default_factory=list)
    recommended_panel: str = "health"


GUIDE_TEXT = {
    "en": {
        "welcome": (
            "I live inside AI Cabinet as the navigation agent. I know the runtime, agents, policies, "
            "and ASTI connector layer. Current connector manifests: {connectors_total}. "
            "Tell me what you want to configure or understand."
        ),
        "pipeline": (
            "AI Cabinet works as a governed runtime, not as a plain chat. A request enters the Gateway, "
            "then goes through PII detection, data classification, policy, cost governor, model routing, "
            "provider/local fallback, output guard, action queue, audit, and memory proposal. "
            "The model is only one execution engine; the Cabinet controls the route and permissions."
        ),
        "navigation": (
            "Use the left buttons as control panels. Runtime, Plugins, Local Models, Voice, Multimodal, "
            "and Personalize are safe public panels. Audit, Actions, Approvals, Budget, Policies, Routing, "
            "Memory, Evidence, and Observability require the admin token."
        ),
        "token": (
            "Admin token unlocks governance panels. In your local demo it is stored in backend/.env. "
            "Do not publish this value. For a public or enterprise version, replace it with real AuthN/AuthZ, "
            "roles, sessions, and scoped API keys."
        ),
        "connectors": (
            "ASTI is the Agentic Secure Tool Interface. It is the safe hands layer of AI Cabinet. "
            "This runtime currently sees {connectors_total} connector manifests. They are draft/report only "
            "until a connector is signed and an action is approved."
        ),
        "models": (
            "Model routing is policy-driven. Public low-risk tasks may use cloud/free routes such as "
            "OpenRouter or Gemini when keys exist. Sensitive or high-risk tasks stay local or use "
            "local-safe-fallback. Ollama gives local models; the fallback keeps the pipeline alive."
        ),
        "microsoft": (
            "Microsoft 365 Agent can draft Outlook emails, calendar proposals, Teams updates, Planner tasks, "
            "and OneDrive/SharePoint workflows. It does not send, post, create meetings, share files, "
            "or call Microsoft Graph until a signed connector and approval record exist."
        ),
        "test": (
            "A good safe test is: choose provider local or ollama, mode microsoft_ops or github_ops, "
            "access level 3, and ask the agent to prepare a proposal without external actions. "
            "The action should enter pending_approval and can be executed only as a local report artifact."
        ),
        "security": (
            "Security is enforced before model execution: PII masking, data classification, YAML policy, "
            "local-only routing for sensitive tasks, output scanning, action approval, and audit logging. "
            "The key rule is: the model asks, the microkernel decides."
        ),
        "fallback": (
            "I am the Cabinet Guide Agent. I can explain the pipeline, buttons, models, policies, agents, "
            "ASTI connectors, Microsoft mode, tests, and safe next steps. Ask me what you want to do, "
            "and I will translate it into a governed Cabinet action."
        ),
        "suggestions": {
            "default": ["Explain pipeline", "Show runtime", "Show ASTI connectors"],
            "policy": ["Show policy", "Show audit", "Explain local-only"],
            "models": ["Show local models", "Show routing", "Run public content test"],
            "actions": ["Run safe test", "Show actions", "Show approvals"],
        },
    },
    "ru": {
        "welcome": (
            "Я живу внутри AI Cabinet как навигационный агент. Я знаю runtime, агентов, политики, "
            "ASTI-коннекторы и безопасные сценарии. Сейчас найдено манифестов коннекторов: {connectors_total}. "
            "Скажи, что ты хочешь настроить или понять."
        ),
        "pipeline": (
            "AI Cabinet работает как управляемый runtime, а не как обычный чат. Запрос входит в Gateway, "
            "проходит PII-маскирование, классификацию данных, policy engine, cost governor, маршрутизацию модели, "
            "локальный или облачный runtime, output guard, очередь действий, аудит и предложение обновления памяти. "
            "Модель только просит. Микрокернель решает маршрут, права и границы."
        ),
        "navigation": (
            "Кнопки слева — это панели управления. Runtime, Plugins, Local Models, Voice, Multimodal и Personalize "
            "можно смотреть безопасно. Audit, Actions, Approvals, Budget, Policies, Routing, Memory, Evidence и "
            "Observability требуют admin token."
        ),
        "token": (
            "Admin token открывает governance-панели. В локальной демо-версии он лежит в backend/.env. "
            "Не публикуй это значение. Для публичной или enterprise-версии нужен настоящий AuthN/AuthZ, "
            "роли, сессии и scoped API keys."
        ),
        "connectors": (
            "ASTI — это Agentic Secure Tool Interface, безопасный слой “рук” AI Cabinet. "
            "Сейчас runtime видит манифестов коннекторов: {connectors_total}. Они работают как draft/report-only, "
            "пока коннектор не подписан и действие не одобрено."
        ),
        "models": (
            "Маршрутизация моделей управляется политиками. Публичные низкорисковые задачи могут идти в "
            "OpenRouter или Gemini, если есть ключи. Чувствительные и высокорисковые задачи остаются локально "
            "или идут в local-safe-fallback. Ollama даёт локальные модели, а fallback сохраняет живой pipeline."
        ),
        "microsoft": (
            "Microsoft 365 Agent может готовить черновики Outlook, предложения календаря, Teams-ответы, "
            "Planner-задачи и сценарии OneDrive/SharePoint. Он не отправляет письма, не публикует сообщения, "
            "не создаёт встречи, не шарит файлы и не вызывает Microsoft Graph без подписанного коннектора и approval record."
        ),
        "test": (
            "Хороший безопасный тест: выбери provider local или ollama, mode microsoft_ops или github_ops, "
            "access level 3, и попроси агента подготовить proposal без внешних действий. Действие должно попасть "
            "в pending_approval и может выполняться только как локальный report artifact."
        ),
        "security": (
            "Безопасность включается до выполнения модели: PII masking, классификация данных, YAML policy, "
            "локальный маршрут для чувствительных задач, output scanning, approval действий и audit log. "
            "Главное правило: модель спрашивает, микрокернель решает."
        ),
        "fallback": (
            "Я Cabinet Guide Agent. Я могу объяснить pipeline, кнопки, модели, политики, агентов, "
            "ASTI-коннекторы, Microsoft mode, тесты и безопасные следующие шаги. Скажи, что хочешь сделать, "
            "а я переведу это в управляемое действие Cabinet."
        ),
        "suggestions": {
            "default": ["Объясни pipeline", "Покажи runtime", "Покажи ASTI-коннекторы"],
            "policy": ["Покажи policy", "Покажи audit", "Объясни local-only"],
            "models": ["Покажи локальные модели", "Покажи routing", "Запусти public content test"],
            "actions": ["Запусти безопасный тест", "Покажи actions", "Покажи approvals"],
        },
    },
    "nl": {
        "welcome": (
            "Ik leef in AI Cabinet als navigatie-agent. Ik ken de runtime, agenten, policies "
            "en de ASTI-connectorlaag. Huidige connector-manifesten: {connectors_total}. "
            "Vertel wat je wilt instellen of begrijpen."
        ),
        "pipeline": (
            "AI Cabinet werkt als een governed runtime, niet als gewone chat. Een verzoek gaat via Gateway, "
            "PII-detectie, dataclassificatie, policy engine, cost governor, model routing, lokale of cloud runtime, "
            "output guard, action queue, audit en memory update proposal. Het model is alleen een uitvoeringsengine; "
            "Cabinet bepaalt route en permissies."
        ),
        "navigation": (
            "Gebruik de knoppen links als control panels. Runtime, Plugins, Local Models, Voice, Multimodal "
            "en Personalize zijn veilige publieke panels. Audit, Actions, Approvals, Budget, Policies, Routing, "
            "Memory, Evidence en Observability vereisen de admin token."
        ),
        "token": (
            "De admin token opent governance panels. In je lokale demo staat die in backend/.env. "
            "Publiceer deze waarde niet. Voor public of enterprise gebruik is echte AuthN/AuthZ nodig."
        ),
        "connectors": (
            "ASTI is de Agentic Secure Tool Interface: de veilige handenlaag van AI Cabinet. "
            "Deze runtime ziet {connectors_total} connector-manifesten. Ze blijven draft/report-only "
            "totdat een connector is ondertekend en een actie is goedgekeurd."
        ),
        "models": (
            "Model routing is policy-driven. Publieke low-risk taken kunnen OpenRouter of Gemini gebruiken "
            "als sleutels bestaan. Gevoelige of high-risk taken blijven lokaal of gebruiken local-safe-fallback. "
            "Ollama levert lokale modellen."
        ),
        "microsoft": (
            "Microsoft 365 Agent kan Outlook e-mails, kalender voorstellen, Teams antwoorden, Planner taken "
            "en OneDrive/SharePoint workflows voorbereiden. Hij verzendt of wijzigt niets zonder signed connector "
            "en approval record."
        ),
        "test": (
            "Een veilige test: kies provider local of ollama, mode microsoft_ops of github_ops, access level 3, "
            "en vraag de agent om een proposal zonder externe acties. De actie hoort in pending_approval te komen."
        ),
        "security": (
            "Security wordt afgedwongen vóór model execution: PII masking, dataclassificatie, YAML policy, "
            "local-only routing, output scanning, action approval en audit logging. De kernregel: "
            "het model vraagt, de microkernel beslist."
        ),
        "fallback": (
            "Ik ben de Cabinet Guide Agent. Ik kan pipeline, knoppen, modellen, policies, agenten, "
            "ASTI-connectors, Microsoft mode, tests en veilige vervolgstappen uitleggen."
        ),
        "suggestions": {
            "default": ["Leg pipeline uit", "Toon runtime", "Toon ASTI-connectors"],
            "policy": ["Toon policy", "Toon audit", "Leg local-only uit"],
            "models": ["Toon lokale modellen", "Toon routing", "Start publieke contenttest"],
            "actions": ["Start veilige test", "Toon actions", "Toon approvals"],
        },
    },
}


class CabinetGuideAgent:
    """Built-in navigation agent for explaining and operating AI Cabinet safely."""

    def reply(self, message: str, ui_state: Dict[str, Any], runtime: Dict[str, Any]) -> GuideReply:
        language = self._language(ui_state)
        text = message.lower().strip()
        if not text:
            return self._reply(language, "welcome", runtime, "default", "health")

        if self._matches(text, ["pipeline", "пайп", "как работает", "работает", "proces", "werkt"]):
            return self._reply(language, "pipeline", runtime, "default", "health")

        if self._matches(text, ["button", "кноп", "не понимаю", "navigation", "навига", "knop", "navigatie"]):
            return self._reply(language, "navigation", runtime, "default", "health")

        if self._matches(text, ["token", "admin", "токен", "доступ", "toegang"]):
            return self._reply(language, "token", runtime, "policy", "access")

        if self._matches(text, ["asti", "connector", "plugin", "плагин", "коннектор"]):
            return self._reply(language, "connectors", runtime, "default", "plugins")

        if self._matches(text, ["model", "ollama", "openrouter", "gemini", "модель", "модели"]):
            return self._reply(language, "models", runtime, "models", "localRuntime")

        if self._matches(text, ["microsoft", "outlook", "teams", "office"]):
            return self._reply(language, "microsoft", runtime, "actions", "plugins")

        if self._matches(text, ["test", "тест", "сценар", "scenario"]):
            return self._reply(language, "test", runtime, "actions", "actions")

        if self._matches(text, ["security", "безопас", "risk", "риск", "veilig"]):
            return self._reply(language, "security", runtime, "policy", "policy")

        return self._reply(language, "fallback", runtime, "default", "health")

    def _welcome(self, runtime: Dict[str, Any]) -> GuideReply:
        return self._reply("en", "welcome", runtime, "default", "health")

    def _reply(
        self,
        language: str,
        key: str,
        runtime: Dict[str, Any],
        suggestion_key: str,
        panel: str,
    ) -> GuideReply:
        texts = GUIDE_TEXT.get(language, GUIDE_TEXT["en"])
        answer = texts[key].format(connectors_total=runtime.get("connectors_total", 0))
        suggestions = texts["suggestions"].get(suggestion_key, texts["suggestions"]["default"])
        return GuideReply(answer=answer, suggestions=suggestions, recommended_panel=panel)

    def _language(self, ui_state: Dict[str, Any]) -> str:
        language = str(ui_state.get("language") or "").lower()
        if language in GUIDE_TEXT:
            return language
        return "en"

    def _matches(self, text: str, patterns: List[str]) -> bool:
        return any(pattern in text for pattern in patterns)
