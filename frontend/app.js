const $ = (id) => document.getElementById(id);
const API_BASE = window.location.protocol === "file:" ? "http://127.0.0.1:8000" : "";
const LANGUAGE_KEY = "AI_CABINET_UI_LANGUAGE";
const PROFILE_KEY = "AI_CABINET_PROFILE";
const DIALOG_MODE_KEY = "AI_CABINET_DIALOG_MODE";
const AGENT_KEY = "AI_CABINET_AGENT";
const VOICE_LANGUAGE_KEY = "AI_CABINET_VOICE_LANGUAGE";
const VOICE_TTS_KEY = "AI_CABINET_VOICE_TTS";
const GUIDE_HISTORY_KEY = "AI_CABINET_GUIDE_HISTORY";

let speechRecognition = null;
let listening = false;
let lastControlledOutput = "";

window.addEventListener("error", (event) => {
  const result = $("result");
  const status = $("status");
  if (status) status.textContent = "Frontend error";
  if (result) result.textContent = `Frontend error: ${event.message}`;
});

window.addEventListener("unhandledrejection", (event) => {
  const result = $("result");
  const status = $("status");
  if (status) status.textContent = "Frontend async error";
  if (result) result.textContent = `Frontend async error: ${event.reason?.message || event.reason}`;
});

const I18N = {
  en: {
    adminTokenLabel: "Admin token",
    adminTokenPlaceholder: "Required for audit, actions, secrets, config",
    accessLevelLabel: "Access level",
    agentComputer: "Computer Control Agent",
    agentMicrosoft: "Microsoft 365 Agent",
    agentDefault: "Default Agent",
    agentEditorial: "Editorial Agent",
    agentGithub: "GitHub Manager",
    agentGovernance: "Governance Architect",
    agentLabel: "Agent",
    agentOperator: "Cabinet Operator",
    agentResearch: "Research Agent",
    agentTrend: "Trend Analyst Agent",
    agentDistribution: "Distribution Orchestrator",
    agentRisk: "Risk Sentinel",
    createForecastButton: "Create forecast",
    dialogArchitect: "Architect",
    dialogComputer: "Computer Control",
    dialogMicrosoft: "Microsoft 365",
    dialogEditorial: "Editorial",
    dialogOrientation: "Orientation",
    dialogDistribution: "Distribution",
    dialogGithub: "GitHub Manager",
    dialogLocalPrivate: "Local Private",
    dialogModeLabel: "Dialogue mode",
    dialogOperator: "Operator",
    dialogSecurity: "Security",
    forecastDeadline: "Deadline",
    forecastDescription: "Create a measurable forecast, save it, and later resolve it with Brier Score.",
    forecastDomain: "Domain",
    forecastFactors: "Factors JSON",
    forecastProbability: "User probability %",
    forecastQuestion: "Raw question",
    forecastRisks: "Risks JSON",
    forecastSuccess: "Success condition",
    forecastTitle: "Forecasting & Risk Calibration",
    gatewayDescription: "Every text, voice, image, file, browser, email, calendar, or plugin task enters the same governed microkernel pipeline.",
    gatewayTitle: "Gateway",
    inputBrowser: "Browser action",
    inputCalendar: "Calendar",
    inputEmail: "Email",
    inputFile: "File task",
    inputImage: "Image task",
    inputPlugin: "Plugin action",
    inputText: "Text",
    inputTypeLabel: "Input type",
    inputVoice: "Voice transcript",
    languageLabel: "Interface language",
    level0: "Level 0 - read only",
    level1: "Level 1 - recommendations",
    level2: "Level 2 - drafts",
    level3: "Level 3 - approval queue",
    level4: "Level 4 - controlled execution",
    level5: "Level 5 - limited autonomous",
    localOnlyLabel: "Local-only security mode",
    metricClass: "Class",
    metricCost: "Cost est.",
    metricDecision: "Decision",
    metricRisk: "Risk",
    modeAnalysis: "Analysis",
    modeCode: "Code",
    modeComputer: "Computer operations",
    modeMicrosoft: "Microsoft 365 operations",
    modeContent: "Public content",
    modeEmail: "Email draft",
    modeOrientation: "Orientation draft",
    modeDistribution: "Distribution draft",
    modeGithub: "GitHub operations",
    modeLabel: "Mode",
    modeLegal: "Legal draft",
    modePaperclip: "Paperclip task draft",
    modeStrategy: "Strategy",
    modeTelegram: "Telegram draft",
    navAccess: "Access",
    navActions: "Actions",
    navAgents: "Agents",
    navApprovals: "Approvals",
    navAudit: "Audit",
    navBudget: "Budget",
    navCalibration: "Calibration",
    navEvidence: "Evidence",
    navForecasts: "Forecasts",
    navLocalModels: "Local Models",
    navMemory: "Memory",
    navMultimodal: "Multimodal",
    navObserve: "Observe",
    navPersonalization: "Personalize",
    navPlugins: "Plugins",
    navPolicies: "Policies",
    navRouting: "Routing",
    navRuntime: "Runtime",
    navVector: "Vector",
    navVoice: "Voice",
    operationsTitle: "Operations",
    outputTitle: "Controlled Output",
    profileJazekker: "Jazekker Editorial Cabinet",
    profileJazekkerOrientation: "Jazekker Orientation Runtime",
    profileLabel: "Personalization profile",
    profileOwner: "Viacheslav / Owner",
    providerAuto: "Hybrid auto router",
    providerClaude: "Claude adapter slot",
    providerDeepSeek: "DeepSeek adapter slot",
    providerLabel: "Provider",
    providerLocal: "Local safe fallback",
    providerManual: "Manual controlled mode",
    providerMistral: "Mistral adapter slot",
    providerOllama: "Ollama local",
    providerOpenRouter: "OpenRouter free router",
    sendButton: "Run governed pipeline",
    statusBlocked: "Blocked/Error",
    statusCompleted: "Completed",
    statusCreatingForecast: "Creating forecast...",
    statusRunning: "Running governed pipeline...",
    tagline: "Governed hybrid AI operating system. Control before autonomy.",
    taskPlaceholder: "Example: create a Telegram draft for Dr. Anna Smith at anna@example.com about governed AI execution.",
    voiceAutoRunLabel: "Auto-run after final transcript",
    voiceIdle: "Voice idle",
    voiceLanguageLabel: "Voice language",
    voiceListening: "Listening...",
    voiceNoSupport: "Speech recognition is not available in this browser.",
    voiceSpeakButton: "Speak result",
    voiceStartButton: "Start voice",
    voiceStopButton: "Stop",
    voiceStopSpeechButton: "Stop speech",
    voiceTtsLabel: "Speak controlled output",
    voiceTranscriptReady: "Transcript ready"
  },
  ru: {
    adminTokenLabel: "Админ-токен",
    adminTokenPlaceholder: "Нужен для аудита, действий, секретов и конфигурации",
    accessLevelLabel: "Уровень доступа",
    agentDefault: "Базовый агент",
    agentEditorial: "Редактор",
    agentGithub: "GitHub Manager",
    agentGovernance: "Архитектор governance",
    agentLabel: "Агент",
    agentOperator: "Оператор кабинета",
    agentResearch: "Исследователь",
    agentRisk: "Risk Sentinel",
    createForecastButton: "Создать прогноз",
    dialogArchitect: "Архитектор",
    dialogEditorial: "Редакционный",
    dialogGithub: "GitHub Manager",
    dialogLocalPrivate: "Локальный приватный",
    dialogModeLabel: "Режим диалога",
    dialogOperator: "Оператор",
    dialogSecurity: "Безопасность",
    forecastDeadline: "Дедлайн",
    forecastDescription: "Создайте измеримый прогноз, сохраните его и позже проверьте через Brier Score.",
    forecastDomain: "Домен",
    forecastFactors: "Факторы JSON",
    forecastProbability: "Вероятность пользователя %",
    forecastQuestion: "Вопрос",
    forecastRisks: "Риски JSON",
    forecastSuccess: "Условие успеха",
    forecastTitle: "Прогнозирование и калибровка риска",
    gatewayDescription: "Любая задача: текст, голос, изображение, файл, браузер, почта, календарь или плагин проходит через единый управляемый microkernel pipeline.",
    gatewayTitle: "Шлюз",
    inputBrowser: "Действие в браузере",
    inputCalendar: "Календарь",
    inputEmail: "Почта",
    inputFile: "Файловая задача",
    inputImage: "Задача с изображением",
    inputPlugin: "Действие плагина",
    inputText: "Текст",
    inputTypeLabel: "Тип входа",
    inputVoice: "Голосовая расшифровка",
    languageLabel: "Язык интерфейса",
    level0: "Уровень 0 - только чтение",
    level1: "Уровень 1 - рекомендации",
    level2: "Уровень 2 - черновики",
    level3: "Уровень 3 - очередь подтверждения",
    level4: "Уровень 4 - контролируемое выполнение",
    level5: "Уровень 5 - ограниченная автономность",
    localOnlyLabel: "Локальный безопасный режим",
    metricClass: "Класс",
    metricCost: "Оценка стоимости",
    metricDecision: "Решение",
    metricRisk: "Риск",
    modeAnalysis: "Анализ",
    modeCode: "Код",
    modeContent: "Публичный контент",
    modeEmail: "Черновик email",
    modeGithub: "GitHub-операции",
    modeLabel: "Режим",
    modeLegal: "Юридический черновик",
    modePaperclip: "Черновик задачи Paperclip",
    modeStrategy: "Стратегия",
    modeTelegram: "Черновик Telegram",
    navAccess: "Доступ",
    navActions: "Действия",
    navAgents: "Агенты",
    navApprovals: "Согласования",
    navAudit: "Аудит",
    navBudget: "Бюджет",
    navCalibration: "Калибровка",
    navEvidence: "Источники",
    navForecasts: "Прогнозы",
    navLocalModels: "Локальные модели",
    navMemory: "Память",
    navMultimodal: "Мультимодальность",
    navObserve: "Наблюдение",
    navPersonalization: "Персонализация",
    navPlugins: "Плагины",
    navPolicies: "Политики",
    navRouting: "Маршрутизация",
    navRuntime: "Runtime",
    navVector: "Вектор",
    navVoice: "Голос",
    operationsTitle: "Операции",
    outputTitle: "Контролируемый вывод",
    profileJazekker: "Jazekker Editorial Cabinet",
    profileLabel: "Профиль персонализации",
    profileOwner: "Вячеслав / владелец",
    providerAuto: "Гибридная автомаршрутизация",
    providerClaude: "Слот адаптера Claude",
    providerDeepSeek: "Слот адаптера DeepSeek",
    providerLabel: "Провайдер",
    providerLocal: "Локальный безопасный fallback",
    providerManual: "Ручной контролируемый режим",
    providerMistral: "Слот адаптера Mistral",
    providerOllama: "Ollama локально",
    providerOpenRouter: "OpenRouter free router",
    sendButton: "Запустить управляемый pipeline",
    statusBlocked: "Заблокировано/ошибка",
    statusCompleted: "Готово",
    statusCreatingForecast: "Создаю прогноз...",
    statusRunning: "Запускаю управляемый pipeline...",
    tagline: "Управляемая гибридная AI-операционная система. Контроль перед автономностью.",
    taskPlaceholder: "Пример: создай черновик Telegram для Dr. Anna Smith на anna@example.com о governed AI execution."
  },
  nl: {
    adminTokenLabel: "Admin-token",
    adminTokenPlaceholder: "Nodig voor audit, acties, geheimen en configuratie",
    accessLevelLabel: "Toegangsniveau",
    agentDefault: "Standaard agent",
    agentEditorial: "Redactie-agent",
    agentGithub: "GitHub Manager",
    agentGovernance: "Governance architect",
    agentLabel: "Agent",
    agentOperator: "Cabinet operator",
    agentResearch: "Research-agent",
    agentTrend: "Trendanalist",
    agentDistribution: "Distributie-orchestrator",
    agentRisk: "Risk Sentinel",
    createForecastButton: "Forecast maken",
    dialogArchitect: "Architect",
    dialogEditorial: "Redactie",
    dialogOrientation: "Orientatie",
    dialogDistribution: "Distributie",
    dialogGithub: "GitHub Manager",
    dialogLocalPrivate: "Lokaal prive",
    dialogModeLabel: "Dialoogmodus",
    dialogOperator: "Operator",
    dialogSecurity: "Security",
    forecastDeadline: "Deadline",
    forecastDescription: "Maak een meetbare forecast, sla die op en evalueer later met Brier Score.",
    forecastDomain: "Domein",
    forecastFactors: "Factoren JSON",
    forecastProbability: "Gebruikerskans %",
    forecastQuestion: "Vraag",
    forecastRisks: "Risico's JSON",
    forecastSuccess: "Succesvoorwaarde",
    forecastTitle: "Forecasting & risicokalibratie",
    gatewayDescription: "Elke taak: tekst, stem, afbeelding, bestand, browser, e-mail, agenda of plugin gaat door dezelfde beheerde microkernel-pipeline.",
    gatewayTitle: "Gateway",
    inputBrowser: "Browseractie",
    inputCalendar: "Agenda",
    inputEmail: "E-mail",
    inputFile: "Bestandstaak",
    inputImage: "Afbeeldingstaak",
    inputPlugin: "Pluginactie",
    inputText: "Tekst",
    inputTypeLabel: "Invoertype",
    inputVoice: "Spraaktranscript",
    languageLabel: "Interfacetaal",
    level0: "Niveau 0 - alleen lezen",
    level1: "Niveau 1 - aanbevelingen",
    level2: "Niveau 2 - concepten",
    level3: "Niveau 3 - goedkeuringswachtrij",
    level4: "Niveau 4 - gecontroleerde uitvoering",
    level5: "Niveau 5 - beperkte autonomie",
    localOnlyLabel: "Alleen-lokaal beveiligingsmodus",
    metricClass: "Classificatie",
    metricCost: "Kostenraming",
    metricDecision: "Besluit",
    metricRisk: "Risico",
    modeAnalysis: "Analyse",
    modeCode: "Code",
    modeContent: "Publieke content",
    modeEmail: "E-mailconcept",
    modeOrientation: "Orientatieconcept",
    modeDistribution: "Distributieconcept",
    modeGithub: "GitHub-operaties",
    modeLabel: "Modus",
    modeLegal: "Juridisch concept",
    modePaperclip: "Paperclip-taakconcept",
    modeStrategy: "Strategie",
    modeTelegram: "Telegram-concept",
    navAccess: "Toegang",
    navActions: "Acties",
    navAgents: "Agenten",
    navApprovals: "Goedkeuring",
    navAudit: "Audit",
    navBudget: "Budget",
    navCalibration: "Kalibratie",
    navEvidence: "Bronnen",
    navForecasts: "Forecasts",
    navLocalModels: "Lokale modellen",
    navMemory: "Geheugen",
    navMultimodal: "Multimodaal",
    navObserve: "Observatie",
    navPersonalization: "Personalisatie",
    navPlugins: "Plugins",
    navPolicies: "Beleid",
    navRouting: "Routering",
    navRuntime: "Runtime",
    navVector: "Vector",
    navVoice: "Stem",
    operationsTitle: "Operaties",
    outputTitle: "Gecontroleerde output",
    profileJazekker: "Jazekker Editorial Cabinet",
    profileJazekkerOrientation: "Jazekker Orientation Runtime",
    profileLabel: "Personalisatieprofiel",
    profileOwner: "Viacheslav / eigenaar",
    providerAuto: "Hybride autorouter",
    providerClaude: "Claude-adapterslot",
    providerDeepSeek: "DeepSeek-adapterslot",
    providerLabel: "Provider",
    providerLocal: "Lokale veilige fallback",
    providerManual: "Handmatige gecontroleerde modus",
    providerMistral: "Mistral-adapterslot",
    providerOllama: "Ollama lokaal",
    providerOpenRouter: "OpenRouter free router",
    sendButton: "Beheerde pipeline starten",
    statusBlocked: "Geblokkeerd/fout",
    statusCompleted: "Voltooid",
    statusCreatingForecast: "Forecast maken...",
    statusRunning: "Beheerde pipeline draait...",
    tagline: "Beheerd hybride AI-besturingssysteem. Controle voor autonomie.",
    taskPlaceholder: "Voorbeeld: maak een Telegram-concept voor Dr. Anna Smith via anna@example.com over governed AI execution."
  }
};

function currentLanguage() {
  const saved = localStorage.getItem(LANGUAGE_KEY);
  if (saved && I18N[saved]) return saved;
  const selected = $("language")?.value;
  if (selected && I18N[selected]) return selected;
  return "ru";
}

function t(key) {
  const language = currentLanguage();
  return I18N[language]?.[key] || I18N.en[key] || key;
}

function applyLanguage(language) {
  const selectedLanguage = I18N[language] ? language : "ru";
  localStorage.setItem(LANGUAGE_KEY, selectedLanguage);
  document.documentElement.lang = selectedLanguage;
  if ($("language")) $("language").value = selectedLanguage;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
}

function restoreSelect(id, storageKey, fallback) {
  const node = $(id);
  if (!node) return;
  node.value = localStorage.getItem(storageKey) || fallback;
  node.addEventListener("change", (event) => localStorage.setItem(storageKey, event.target.value));
}

const MODE_DEFAULT_AGENT = {
  operator: "cabinet_operator",
  architect: "governance_architect",
  editorial: "editorial_agent",
  orientation: "trend_analyst_agent",
  distribution: "distribution_orchestrator_agent",
  security: "risk_sentinel",
  github_manager: "github_manager_agent",
  computer_control: "computer_control_agent",
  microsoft_365: "microsoft_365_agent",
  local_private: "risk_sentinel"
};

function syncModeDefaults() {
  const mode = $("dialogMode")?.value;
  if (!mode) return;
  const defaultAgent = MODE_DEFAULT_AGENT[mode];
  if (defaultAgent && $("agent")) {
    $("agent").value = defaultAgent;
    localStorage.setItem(AGENT_KEY, defaultAgent);
  }
  if ($("localOnly") && mode === "local_private") {
    $("localOnly").checked = true;
  }
}

function voiceRecognitionApi() {
  return window.SpeechRecognition || window.webkitSpeechRecognition;
}

function setVoiceStatus(message) {
  if ($("voiceStatus")) $("voiceStatus").textContent = message;
}

function appendTranscript(text, final = true) {
  if (!text.trim()) return;
  const current = $("voiceTranscript")?.textContent || "";
  if ($("voiceTranscript")) {
    $("voiceTranscript").textContent = final ? `${current}${text.trim()}\n` : text;
  }
  if (final && $("task")) {
    const separator = $("task").value.trim() ? "\n" : "";
    $("task").value = `${$("task").value}${separator}${text.trim()}`;
    if ($("inputType")) $("inputType").value = "voice";
  }
}

function initVoiceRuntime() {
  if ($("voiceLanguage")) {
    $("voiceLanguage").value = localStorage.getItem(VOICE_LANGUAGE_KEY) || "ru-RU";
    $("voiceLanguage").addEventListener("change", (event) => {
      localStorage.setItem(VOICE_LANGUAGE_KEY, event.target.value);
    });
  }
  if ($("voiceTtsEnabled")) {
    $("voiceTtsEnabled").checked = localStorage.getItem(VOICE_TTS_KEY) === "true";
    $("voiceTtsEnabled").addEventListener("change", (event) => {
      localStorage.setItem(VOICE_TTS_KEY, String(event.target.checked));
    });
  }
  setVoiceStatus(voiceRecognitionApi() ? t("voiceIdle") : t("voiceNoSupport"));
}

function startVoiceInput() {
  const Recognition = voiceRecognitionApi();
  if (!Recognition) {
    setVoiceStatus(t("voiceNoSupport"));
    return;
  }
  if (listening && speechRecognition) return;

  speechRecognition = new Recognition();
  speechRecognition.lang = $("voiceLanguage")?.value || "ru-RU";
  speechRecognition.continuous = false;
  speechRecognition.interimResults = true;
  listening = true;
  setVoiceStatus(t("voiceListening"));

  speechRecognition.onresult = (event) => {
    let interim = "";
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        appendTranscript(transcript, true);
        setVoiceStatus(t("voiceTranscriptReady"));
        if ($("voiceAutoRun")?.checked) $("sendBtn").click();
      } else {
        interim += transcript;
      }
    }
    if (interim && $("voiceTranscript")) $("voiceTranscript").textContent = interim;
  };
  speechRecognition.onerror = (event) => {
    listening = false;
    setVoiceStatus(`Voice error: ${event.error}`);
  };
  speechRecognition.onend = () => {
    listening = false;
    if ($("voiceStatus")?.textContent === t("voiceListening")) setVoiceStatus(t("voiceIdle"));
  };
  speechRecognition.start();
}

function stopVoiceInput() {
  if (speechRecognition) speechRecognition.stop();
  listening = false;
  setVoiceStatus(t("voiceIdle"));
}

function speakText(text) {
  if (!("speechSynthesis" in window) || !text.trim()) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = $("voiceLanguage")?.value || "ru-RU";
  window.speechSynthesis.speak(utterance);
}

function guideHistory() {
  try {
    return JSON.parse(localStorage.getItem(guideHistoryKey()) || "[]");
  } catch (_) {
    return [];
  }
}

function saveGuideHistory(history) {
  localStorage.setItem(guideHistoryKey(), JSON.stringify(history.slice(-30)));
}

function guideHistoryKey() {
  return `${GUIDE_HISTORY_KEY}_${currentLanguage()}`;
}

function appendGuideMessage(role, text) {
  const container = $("guideMessages");
  if (!container) return;
  const message = document.createElement("div");
  message.className = `guide-message ${role}`;
  message.textContent = text;
  container.appendChild(message);
  container.scrollTop = container.scrollHeight;
  const history = guideHistory();
  history.push({role, text, at: new Date().toISOString()});
  saveGuideHistory(history);
}

function restoreGuideMessages() {
  const container = $("guideMessages");
  if (!container) return;
  container.innerHTML = "";
  const history = guideHistory();
  if (!history.length) {
    appendGuideMessage(
      "agent",
      guideWelcomeText(currentLanguage())
    );
    renderGuideSuggestions(guideDefaultSuggestions(currentLanguage()));
    return;
  }
  history.forEach((item) => {
    const message = document.createElement("div");
    message.className = `guide-message ${item.role}`;
    message.textContent = item.text;
    container.appendChild(message);
  });
  container.scrollTop = container.scrollHeight;
}

function currentUiState() {
  return {
    language: currentLanguage(),
    profile: $("profile")?.value,
    dialog_mode: $("dialogMode")?.value,
    agent: $("agent")?.value,
    provider: $("provider")?.value,
    mode: $("mode")?.value,
    input_type: $("inputType")?.value,
    access_level: $("accessLevel")?.value,
    local_only: $("localOnly")?.checked,
    has_admin_token: Boolean($("adminToken")?.value),
    last_status: $("status")?.textContent || "",
    last_metrics: {
      risk: $("riskMetric")?.textContent,
      data_class: $("classMetric")?.textContent,
      decision: $("decisionMetric")?.textContent,
      cost: $("costMetric")?.textContent
    }
  };
}

function guideWelcomeText(language) {
  if (language === "ru") {
    return "Я Cabinet Guide Agent. Спроси меня, как работает pipeline, какую кнопку нажать, как настроить модели или как запустить безопасный тест агента.";
  }
  if (language === "nl") {
    return "Ik ben de Cabinet Guide Agent. Vraag mij hoe de pipeline werkt, welke knop je nodig hebt, hoe je modellen instelt of hoe je een veilige agenttest start.";
  }
  return "I am the Cabinet Guide Agent. Ask me how the pipeline works, which button to press, how to configure models, or how to run a safe agent test.";
}

function guideDefaultSuggestions(language) {
  if (language === "ru") return ["Объясни pipeline", "Покажи runtime", "Покажи ASTI-коннекторы"];
  if (language === "nl") return ["Leg pipeline uit", "Toon runtime", "Toon ASTI-connectors"];
  return ["Explain pipeline", "Show runtime", "Show ASTI connectors"];
}

function panelButtonForSuggestion(suggestion) {
  const key = suggestion.toLowerCase();
  if (key.includes("runtime")) return "healthBtn";
  if (key.includes("asti") || key.includes("connector") || key.includes("коннектор")) return "pluginsBtn";
  if (key.includes("local model") || key.includes("локальные модели") || key.includes("lokale modellen")) return "localRuntimeBtn";
  if (key.includes("routing")) return "routingBtn";
  if (key.includes("policy")) return "policyBtn";
  if (key.includes("audit")) return "auditBtn";
  if (key.includes("action")) return "actionsBtn";
  if (key.includes("approval")) return "approvalsBtn";
  return "";
}

function renderGuideSuggestions(suggestions = []) {
  const box = $("guideSuggestions");
  if (!box) return;
  box.innerHTML = "";
  suggestions.forEach((suggestion) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = suggestion;
    button.addEventListener("click", () => {
      const target = panelButtonForSuggestion(suggestion);
      if (target && $(target)) {
        $(target).click();
        appendGuideMessage("user", suggestion);
        appendGuideMessage("agent", `Opened panel: ${suggestion}`);
      } else {
        $("guideInput").value = suggestion;
        $("guideForm").requestSubmit();
      }
    });
    box.appendChild(button);
  });
}

async function sendGuideMessage(message) {
  appendGuideMessage("user", message);
  const thinkingText = currentLanguage() === "ru" ? "Думаю внутри AI Cabinet..." : currentLanguage() === "nl" ? "Ik denk binnen AI Cabinet..." : "Thinking inside AI Cabinet...";
  appendGuideMessage("agent", thinkingText);
  const data = await postJSON("/guide/chat", {
    message,
    ui_state: currentUiState()
  });
  const messages = $("guideMessages")?.querySelectorAll(".guide-message.agent");
  const last = messages?.[messages.length - 1];
  if (last && last.textContent === thinkingText) {
    last.textContent = data.answer;
    const history = guideHistory();
    const lastHistory = history[history.length - 1];
    if (lastHistory?.text === thinkingText) {
      lastHistory.text = data.answer;
      saveGuideHistory(history);
    }
  } else {
    appendGuideMessage("agent", data.answer);
  }
  renderGuideSuggestions(data.suggestions || []);
}

function adminHeaders() {
  const token = $("adminToken")?.value || localStorage.getItem("AI_CABINET_ADMIN_TOKEN") || "";
  if (token) localStorage.setItem("AI_CABINET_ADMIN_TOKEN", token);
  return token ? {"X-AI-Cabinet-Admin-Token": token} : {};
}

async function postJSON(url, body = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    method: "POST",
    headers: {"Content-Type": "application/json", ...adminHeaders()},
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(await readableError(res));
  return await res.json();
}

async function getJSON(url) {
  const res = await fetch(`${API_BASE}${url}`, {headers: adminHeaders()});
  if (!res.ok) throw new Error(await readableError(res));
  return await res.json();
}

async function readableError(res) {
  const raw = await res.text();
  let detail = raw;
  try {
    const parsed = JSON.parse(raw);
    detail = parsed.detail || parsed.message || raw;
  } catch (_) {
    detail = raw;
  }
  if (res.status === 403) {
    return "Admin token required. Enter ADMIN_API_TOKEN in the sidebar, then click the button again.";
  }
  if (res.status === 503) {
    return "Admin API token is not configured on the backend.";
  }
  return `${res.status} ${res.statusText}: ${detail}`;
}

window.addEventListener("DOMContentLoaded", () => {
  const savedToken = localStorage.getItem("AI_CABINET_ADMIN_TOKEN");
  if (savedToken && $("adminToken")) $("adminToken").value = savedToken;
  restoreSelect("profile", PROFILE_KEY, "owner_default");
  restoreSelect("dialogMode", DIALOG_MODE_KEY, "operator");
  restoreSelect("agent", AGENT_KEY, "default_agent");
  $("dialogMode")?.addEventListener("change", syncModeDefaults);
  applyLanguage(currentLanguage());
  initVoiceRuntime();
  $("language")?.addEventListener("change", (event) => applyLanguage(event.target.value));
  $("voiceStartBtn")?.addEventListener("click", startVoiceInput);
  $("voiceStopBtn")?.addEventListener("click", stopVoiceInput);
  $("speakResultBtn")?.addEventListener("click", () => speakText(lastControlledOutput || $("result")?.textContent || ""));
  $("stopSpeechBtn")?.addEventListener("click", () => window.speechSynthesis?.cancel());
  $("guideLauncher")?.addEventListener("click", () => {
    $("guidePanel").hidden = false;
    restoreGuideMessages();
    $("guideInput")?.focus();
  });
  $("guideClose")?.addEventListener("click", () => {
    $("guidePanel").hidden = true;
  });
  $("guideForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const input = $("guideInput");
    const message = input.value.trim();
    if (!message) return;
    input.value = "";
    try {
      await sendGuideMessage(message);
    } catch (e) {
      appendGuideMessage("agent", `Guide error: ${e.message}`);
    }
  });
  if ($("status")) $("status").textContent = "UI ready";
});

function renderSide(data) {
  $("sideOutput").textContent = JSON.stringify(data, null, 2);
}

function renderSidePanel(title, data) {
  const rendered = `${title}\n${"=".repeat(Math.min(title.length, 60))}\n\n${JSON.stringify(data, null, 2)}`;
  $("sideOutput").textContent = rendered;
  $("result").textContent = rendered;
  $("meta").innerHTML = `<span class="badge">panel: ${title}</span>`;
  $("status").textContent = "Panel loaded";
}

function renderProcessMap(data) {
  const lines = [
    data.principle || "The model asks. The microkernel decides.",
    "",
    ...(data.pipeline || []).map((item, index) => `${index + 1}. ${item.step} [${item.owner}] - ${item.decision}`),
    "",
    "Routing rules:",
    ...(data.routing_rules || []).map((rule) => `- ${rule}`)
  ];
  $("sideOutput").textContent = lines.join("\n");
  $("result").textContent = lines.join("\n");
  $("meta").innerHTML = `<span class="badge">panel: Process Map</span>`;
  $("status").textContent = "Process map loaded";
}

function renderPanelAudit(data) {
  const lines = [
    "Control Center Panel Audit",
    "==========================",
    "",
    `Total panels: ${data.summary?.total_panels}`,
    `Public panels: ${data.summary?.public_panels}`,
    `Admin panels: ${data.summary?.admin_panels}`,
    "",
    ...(data.panels || []).map((panel) => {
      return `${panel.panel}: ${panel.status} | access=${panel.access} | ${panel.purpose}`;
    })
  ];
  $("sideOutput").textContent = lines.join("\n");
  $("result").textContent = lines.join("\n");
  $("meta").innerHTML = `<span class="badge">panel: Panel Audit</span>`;
  $("status").textContent = "Panel audit loaded";
}

function escapeHTML(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function parseMaybeJSON(value, fallback) {
  if (Array.isArray(value) || (value && typeof value === "object")) return value;
  if (typeof value !== "string" || !value.trim()) return fallback;
  try {
    return JSON.parse(value);
  } catch {
    return fallback;
  }
}

function compactAgentName(agentId) {
  return String(agentId || "agent")
    .replace(/_agent$/u, "")
    .replaceAll("_", " ")
    .replace(/\b\w/gu, (letter) => letter.toUpperCase());
}

function inferAgentTriggers(agent) {
  const role = String(agent.role || "");
  const risk = String(agent.risk_level || "medium");
  const base = [
    "policy conflict",
    "PII or sensitive data",
    "external side effect",
    "durable memory update"
  ];
  if (risk === "high") base.unshift("owner approval required before execution");
  if (role.includes("github")) base.push("push, merge, release, issue, PR, repo setting change");
  if (role.includes("microsoft")) base.push("send email, post Teams message, create meeting, share file");
  if (role.includes("computer")) base.push("shell command, file deletion, install, registry/startup change");
  if (role.includes("editorial")) base.push("publication, sensitive framing, unsupported claim");
  if (role.includes("research")) base.push("uncertain source used as fact");
  if (role.includes("risk")) base.push("risk override or blocked output");
  if (role.includes("navigation")) base.push("configuration change requested by owner");
  return [...new Set(base)].slice(0, 7);
}

function renderAgentCloud(agent) {
  const permissions = parseMaybeJSON(agent.permissions, []);
  const tools = parseMaybeJSON(agent.tools, []);
  const budget = parseMaybeJSON(agent.budget, {});
  const triggers = inferAgentTriggers(agent);
  const risk = String(agent.risk_level || "medium").toLowerCase();
  const agentId = agent.id || "agent";
  return `
    <article class="agent-cloud">
      <div class="agent-cloud-header">
        <div class="agent-cloud-title">
          <h3>${escapeHTML(compactAgentName(agentId))}</h3>
          <span>${escapeHTML(agentId)} · ${escapeHTML(agent.role || "controlled agent")}</span>
        </div>
        <span class="agent-risk ${escapeHTML(risk)}">${escapeHTML(risk)}</span>
      </div>
      <div class="agent-cloud-section">
        <strong>Who he is</strong>
        <p>${escapeHTML(agent.instructions || "Governed AI Cabinet agent operating behind the microkernel.")}</p>
      </div>
      <div class="agent-cloud-section">
        <strong>Operations</strong>
        <div class="agent-chip-row">
          ${permissions.slice(0, 10).map((item) => `<span class="agent-chip">${escapeHTML(item)}</span>`).join("") || "<span class=\"agent-chip\">draft</span>"}
        </div>
      </div>
      <div class="agent-cloud-section">
        <strong>Tools under control</strong>
        <div class="agent-chip-row">
          ${tools.slice(0, 8).map((item) => `<span class="agent-chip">${escapeHTML(item)}</span>`).join("") || "<span class=\"agent-chip\">model_router</span>"}
        </div>
      </div>
      <div class="agent-cloud-section">
        <strong>What it waits for</strong>
        <div class="agent-chip-row">
          ${triggers.map((item) => `<span class="agent-chip">${escapeHTML(item)}</span>`).join("")}
        </div>
      </div>
      <div class="agent-cloud-section">
        <strong>Limits</strong>
        <p>Memory: ${escapeHTML(agent.memory_scope || "operational")} · Daily budget: ${escapeHTML(budget.daily_cost ?? "-")} · Max/request: ${escapeHTML(budget.max_cost_per_request ?? "-")} · Status: ${escapeHTML(agent.status || "active")}</p>
      </div>
      <div class="agent-cloud-actions">
        <button class="primary-action" type="button" data-select-agent="${escapeHTML(agentId)}">Use agent</button>
        <button type="button" data-draft-agent-test="${escapeHTML(agentId)}">Draft test</button>
      </div>
    </article>
  `;
}

async function loadAgentsForCenter() {
  try {
    return await getJSON("/agents");
  } catch {
    const personalization = await getJSON("/runtime/personalization");
    return personalization.agents || [];
  }
}

async function openAgentCenter() {
  const modal = $("agentCenterModal");
  const grid = $("agentCloudGrid");
  const status = $("agentCenterStatus");
  if (!modal || !grid || !status) return;
  modal.hidden = false;
  grid.innerHTML = "";
  status.textContent = "Loading governed agents...";
  try {
    const agents = await loadAgentsForCenter();
    grid.innerHTML = agents.map(renderAgentCloud).join("");
    status.textContent = `${agents.length} governed agents loaded. Direct execution remains approval-gated.`;
    renderSidePanel("Agent Center", {
      agents_loaded: agents.length,
      execution_model: "draft, analyze, propose, queue; execute only after approval",
      agents
    });
  } catch (e) {
    status.textContent = `Agent Center error: ${e.message}`;
    grid.innerHTML = `<div class="agent-cloud"><strong>Could not load agents</strong><p>${escapeHTML(e.message)}</p></div>`;
  }
}

function closeAgentCenter() {
  const modal = $("agentCenterModal");
  if (modal) modal.hidden = true;
}

function selectAgentFromCenter(agentId) {
  const select = $("agent");
  if (select) {
    select.value = agentId;
    localStorage.setItem(AGENT_KEY, agentId);
  }
  $("status").textContent = `Selected agent: ${agentId}`;
  closeAgentCenter();
}

function draftAgentTest(agentId) {
  const task = $("task");
  if (task) {
    task.value = `Run a safe governed test for ${agentId}. Explain what you can do, what you cannot do, which approval triggers apply, and prepare a draft action report without executing external actions.`;
  }
  selectAgentFromCenter(agentId);
}

function renderSideMessage(title, message, extra = {}) {
  renderSidePanel(title, {message, ...extra});
}

async function runPanel(buttonId, title, loader) {
  const button = $(buttonId);
  if (!button) return;
  const originalText = button.textContent;
  button.disabled = true;
  button.classList.add("loading");
  button.textContent = "Loading...";
  $("status").textContent = `Loading ${title}...`;
  renderSideMessage(title, "Loading...");
  try {
    const data = await loader();
    renderSidePanel(title, data);
  } catch (e) {
    renderSideMessage(title, e.message, {
      hint: "Public panels work without a token. Governance/admin panels require the ADMIN_API_TOKEN from backend/.env.",
      token_present: Boolean($("adminToken")?.value)
    });
  } finally {
    button.disabled = false;
    button.classList.remove("loading");
    button.textContent = originalText;
  }
}

function setMetrics(data) {
  $("riskMetric").textContent = data.risk_level || "-";
  $("classMetric").textContent = data.data_class || "-";
  $("decisionMetric").textContent = data.local_cloud_decision || "-";
  $("costMetric").textContent = data.cost_estimated === undefined ? "-" : `$${data.cost_estimated.toFixed(6)}`;
}

$("sendBtn").onclick = async () => {
  $("status").textContent = t("statusRunning");
  $("result").textContent = "";
  $("meta").innerHTML = "";

  try {
    const data = await postJSON("/submit", {
      profile_id: $("profile").value,
      dialog_mode: $("dialogMode").value,
      agent_id: $("agent").value,
      provider: $("provider").value,
      mode: $("mode").value,
      input_type: $("inputType").value,
      access_level: Number($("accessLevel").value),
      local_only: $("localOnly").checked,
      task: $("task").value
    });

    setMetrics(data);
    $("meta").innerHTML = `
      <span class="badge">provider: ${data.provider}</span>
      <span class="badge">model: ${data.model}</span>
      <span class="badge">route: ${data.route_reason}</span>
      <span class="badge">input: ${data.normalized_input_type}</span>
      <span class="badge">state: ${data.state}</span>
      <span class="badge">policy: ${data.policy_applied}</span>
      <span class="badge">tokens: ${data.tokens_estimated}/${data.tokens_used}</span>
      ${data.action_id ? `<span class="badge">action: ${data.action_status}</span>` : ""}
      ${data.memory_proposal_id ? `<span class="badge">memory proposal</span>` : ""}
    `;
    $("result").textContent = [
      data.result,
      "",
      `Action ID: ${data.action_id || "-"}`,
      `Memory proposal ID: ${data.memory_proposal_id || "-"}`,
      `PII detected: ${JSON.stringify(data.pii_detected)}`,
      `Output scan: ${JSON.stringify(data.output_scan)}`
    ].join("\n");
    lastControlledOutput = data.result || "";
    if ($("voiceTtsEnabled")?.checked) speakText(lastControlledOutput);
    $("status").textContent = t("statusCompleted");
  } catch (e) {
    $("status").textContent = t("statusBlocked");
    $("result").textContent = e.message;
  }
};

$("healthBtn").onclick = () => runPanel("healthBtn", "Runtime Status", () => getJSON("/health"));
$("processMapBtn").onclick = () => runPanel("processMapBtn", "Process Map", async () => {
  const data = await getJSON("/control-center/process-map");
  renderProcessMap(data);
  return data;
});
$("panelAuditBtn").onclick = () => runPanel("panelAuditBtn", "Panel Audit", async () => {
  const data = await getJSON("/control-center/panel-audit");
  renderPanelAudit(data);
  return data;
});
$("policyBtn").onclick = () => runPanel("policyBtn", "Policy Configuration", () => getJSON("/config/policy"));
$("routingBtn").onclick = () => runPanel("routingBtn", "Model Routing", () => getJSON("/config/model-routing"));
$("budgetBtn").onclick = () => runPanel("budgetBtn", "Budget Monitor", () => getJSON("/budget/status"));
$("pluginsBtn").onclick = () => runPanel("pluginsBtn", "ASTI Connectors", () => getJSON("/connectors/status"));
$("actionsBtn").onclick = () => runPanel("actionsBtn", "Action Queue", () => getJSON("/actions"));
$("approvalsBtn").onclick = () => runPanel("approvalsBtn", "Approval Center", () => getJSON("/approvals"));
$("memoryLayersBtn").onclick = () => runPanel("memoryLayersBtn", "Memory Layers", () => getJSON("/memory/layers"));
$("auditBtn").onclick = () => runPanel("auditBtn", "Audit Log", () => getJSON("/audit"));
$("localRuntimeBtn").onclick = () => runPanel("localRuntimeBtn", "Local Model Runtime", () => getJSON("/local-runtime/status"));
$("vectorBtn").onclick = async () => {
  await runPanel("vectorBtn", "Vector Memory Search", () => postJSON("/vector-memory/search", {
      namespace: "project",
      query: $("task").value || "AI Cabinet",
      limit: 5
    }).then((data) => ({
      namespace: "project",
      query: $("task").value || "AI Cabinet",
      results: data
    }))
  );
};
$("voiceBtn").onclick = () => runPanel("voiceBtn", "Voice Runtime", () => getJSON("/voice/status"));
$("multimodalBtn").onclick = () => runPanel("multimodalBtn", "Multimodal Runtime", () => getJSON("/multimodal/status"));
$("accessBtn").onclick = () => runPanel("accessBtn", "Access Control", () => getJSON("/access/users"));
$("agentsBtn").onclick = () => openAgentCenter();
$("agentCenterClose").onclick = () => closeAgentCenter();
$("agentCenterBackdrop").onclick = () => closeAgentCenter();
$("agentCenterRefresh").onclick = () => openAgentCenter();
$("agentCloudGrid").addEventListener("click", (event) => {
  const selectButton = event.target.closest("[data-select-agent]");
  if (selectButton) {
    selectAgentFromCenter(selectButton.dataset.selectAgent);
    return;
  }
  const testButton = event.target.closest("[data-draft-agent-test]");
  if (testButton) {
    draftAgentTest(testButton.dataset.draftAgentTest);
  }
});
$("personalizationBtn").onclick = () => runPanel("personalizationBtn", "Personalization", () => getJSON("/runtime/personalization"));
$("evidenceBtn").onclick = () => runPanel("evidenceBtn", "Evidence Sources", () => getJSON("/evidence"));
$("collectNewsBtn").onclick = () => runPanel("collectNewsBtn", "Jazekker News Collector", () => postJSON("/jazekker/news/collect", {
  topic: $("task").value || "AI governance",
  limit_per_source: 5,
  max_total: 12
}));
$("observabilityBtn").onclick = () => runPanel("observabilityBtn", "Observability Events", () => getJSON("/observability/events"));
$("forecastsBtn").onclick = () => runPanel("forecastsBtn", "Forecast Records", () => getJSON("/forecasts"));
$("calibrationBtn").onclick = () => runPanel("calibrationBtn", "Forecast Calibration", () => getJSON("/forecasts/calibration-profile"));
$("createForecastBtn").onclick = async () => {
  $("forecastStatus").textContent = t("statusCreatingForecast");
  try {
    const data = await postJSON("/forecasts", {
      raw_question: $("forecastQuestion").value,
      domain: $("forecastDomain").value,
      deadline: $("forecastDeadline").value,
      success_condition: $("forecastSuccess").value,
      user_initial_probability: Number($("forecastProbability").value),
      available_evidence: ["operator-provided structured forecast evidence"],
      factors: JSON.parse($("forecastFactors").value || "[]"),
      risks: JSON.parse($("forecastRisks").value || "[]")
    });
    $("forecastStatus").textContent = `Saved ${data.forecast_id}`;
    $("result").textContent = data.report;
    setMetrics({
      risk_level: data.risk_summary.total_risk_score >= 2 ? "high" : "medium",
      data_class: data.domain,
      local_cloud_decision: "local deterministic engine",
      cost_estimated: 0
    });
    renderSidePanel("Forecast Created", data);
  } catch (e) {
    $("forecastStatus").textContent = t("statusBlocked");
    $("result").textContent = e.message;
  }
};
