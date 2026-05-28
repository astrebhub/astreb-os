from __future__ import annotations

import re
from dataclasses import dataclass

from .models import OrientationClassification


@dataclass(frozen=True)
class DomainDefinition:
    id: str
    signals: tuple[str, ...]
    intent: str


@dataclass(frozen=True)
class TermDefinition:
    variant: str
    canonical: str
    rule: str = "regulated_term"


@dataclass(frozen=True)
class OperationalIntentDefinition:
    intent: str
    signals: tuple[str, ...]


DOMAIN_REGISTRY: tuple[DomainDefinition, ...] = (
    DomainDefinition(
        "testbox_product",
        (
            "astreb testbox", "testbox", "meta-qms", "qms runtime",
            "quality management", "governance runtime", "governance and quality",
            "позиционировать", "позиционирование", "как лучше позиционировать",
            "качество", "управление качеством", "система качества",
        ),
        "strategic_positioning",
    ),
    DomainDefinition(
        "event_collaboration",
        (
            "pre-hackathon", "pre hackathon", "hackathon", "onegov",
            "leer de challenges kennen", "vind je team", "find your team",
            "хакатон", "хакатона", "хакатоне", "челлендж", "челленджи",
            "задания хакатона", "задачи хакатона", "выпуске хакатона",
            "найти команду", "познакомиться с challenge", "познакомиться с челлендж",
        ),
        "prepare_event_participation",
    ),
    DomainDefinition(
        "zzp_intermediary_contract",
        (
            "zzp", "zelfstandige", "фриланс", "самозанят",
            "агентством трудоустройства", "агентство трудоустройства",
            "агентством по трудоустройству", "intermediair", "uitzendbureau",
            "detacheringsbureau", "bemiddeling", "tussenkomst",
        ),
        "orient_zzp_intermediary_contract",
    ),
    DomainDefinition(
        "residential_parking",
        (
            "парковочное место", "место для парковки", "парковк",
            "паркинг", "parkeerplaats", "parkeervergunning",
            "парковочное разрешение", "место возле дома",
        ),
        "orient_residential_parking",
    ),
    DomainDefinition(
        "consulting_services",
        (
            "консалт", "консультационн", "консультирован",
            "consulting", "consultancy", "consultant", "advisering",
            "adviesdienst", "adviesbureau",
        ),
        "orient_consulting_services",
    ),
    DomainDefinition(
        "business_formation",
        (
            "кооператив", "создавать компанию", "создание компании", "открыть компани",
            "форма компании", "форму компании", "открыть производство",
            "запустить производство", "программного обеспечения", "команда специалистов",
            "software company", "software product", "legal structure", "cooperative",
            "cooperatie", "private limited", "startup company", "bv or", "bv или",
        ),
        "choose_business_structure",
    ),
    DomainDefinition(
        "battery_manufacturing",
        (
            "источник хранения электричества", "источников хранения электричества",
            "накопител", "аккумулятор", "батаре", "хранение энергии",
            "energy storage", "battery", "batteries", "accumulator",
        ),
        "regulated_energy_storage_manufacturing",
    ),
    DomainDefinition(
        "liability",
        (
            "велосипед", "велосипедист", "дтп", "авари", "компенсац", "ущерб",
            "fiets", "fietser", "aanrijding", "schadevergoeding", "aansprakelijk",
            "traffic accident", "cyclist", "bicycle",
        ),
        "liability_orientation",
    ),
    DomainDefinition(
        "immigration",
        ("украин", "temporary protection", "ind", "residence", "внж", "виза"),
        "immigration_orientation",
    ),
    DomainDefinition(
        "employment",
        ("salary", "wage", "зарплат", "работодател", "увольнен"),
        "employment_rights_orientation",
    ),
    DomainDefinition("tax", ("tax", "belasting", "налог", "штраф налог"), "tax_orientation"),
    DomainDefinition("contracts", ("contract", "контракт", "договор", "соглашен"), "contract_orientation"),
    DomainDefinition("insurance", ("insurance", "verzekering", "страхов"), "insurance_orientation"),
    DomainDefinition("benefits", ("benefit", "toeslag", "пособ"), "benefits_orientation"),
    DomainDefinition("data_privacy", ("gdpr", "privacy", "персональн", "данных"), "privacy_orientation"),
    DomainDefinition(
        "social_housing",
        (
            "социальное жилье", "социального жилья", "социальную аренду",
            "социальной аренды", "социальной аренде", "социальная аренда", "social housing",
            "sociale huurwoning", "woningcorporatie", "huurwoning",
        ),
        "check_social_housing_eligibility",
    ),
    DomainDefinition(
        "employment_contract",
        (
            "нулевой контракт", "нулевого контракта", "нулевому контракту",
            "контракт без часов", "нулевые часы", "0-hour contract", "nulurencontract",
            "nul uren contract", "zero-hours contract", "zero hours contract",
            "oproepcontract",
        ),
        "understand_zero_hours_employment_contract",
    ),
)

TERM_REGISTRY: tuple[TermDefinition, ...] = (
    TermDefinition("предлогают", "предлагают", "typo_correction"),
    TermDefinition("притензии", "претензии", "typo_correction"),
    TermDefinition("докмент", "документ", "typo_correction"),
    TermDefinition("кантракт", "контракт", "typo_correction"),
    TermDefinition("жильё", "жилье", "orthographic_normalization"),
    TermDefinition("ззп", "zzp", "term_normalization"),
    TermDefinition("агенством", "агентством", "typo_correction"),
    TermDefinition("нулевой контракт", "nulurencontract"),
    TermDefinition("нулевые часы", "nulurencontract"),
    TermDefinition("zero hours contract", "nulurencontract"),
    TermDefinition("zero-hours contract", "nulurencontract"),
    TermDefinition("0-hour contract", "nulurencontract"),
    TermDefinition("cooperatie ua", "cooperatie UA"),
    TermDefinition("кооператив ua", "cooperatie UA"),
)

OPERATIONAL_INTENT_REGISTRY: tuple[OperationalIntentDefinition, ...] = (
    OperationalIntentDefinition(
        "introduce_system",
        (
            "кто ты", "что умеешь", "что ты умеешь", "расскажи о себе",
            "who are you", "what can you do", "what do you do",
            "wie ben je", "wat kun je",
        ),
    ),
    OperationalIntentDefinition(
        "draft_letter",
        (
            "подготовка письма", "подготовить письмо", "подготовь письмо", "напиши письмо",
            "составь письмо", "составь черновик письма", "черновик письма",
            "письмо претензии", "письмо-претензия",
            "draft letter", "draft a letter", "write an email", "brief opstellen",
        ),
    ),
    OperationalIntentDefinition(
        "review_document",
        (
            "проверка документа",
            "проверить документ",
            "проверь документ",
            "проверь этот документ",
            "объясни документ",
            "обьясни документ",
            "разбери документ",
            "что в этом документе",
            "проверь договор",
            "проверить договор",
            "разбери договор",
            "document review",
            "explain this document",
            "document controleren",
        ),
    ),
    OperationalIntentDefinition(
        "build_action_plan",
        ("план действий", "action plan", "stappenplan"),
    ),
    OperationalIntentDefinition(
        "assess_situation",
        ("разбор ситуации", "оценить ситуацию", "situation assessment", "situatie beoordelen"),
    ),
    OperationalIntentDefinition(
        "forecast_event_challenges",
        (
            "спрогнозировать",
            "спрогнозируй",
            "прогноз",
            "какие будут задания",
            "какие будут задачи",
            "какие задания",
            "какие задачи",
            "forecast",
            "predict",
        ),
    ),
    OperationalIntentDefinition(
        "strategic_positioning",
        (
            "позиционировать",
            "позиционирование",
            "как лучше позиционировать",
            "positioning",
            "position",
            "market positioning",
            "как представить",
            "как объяснить",
        ),
    ),
    OperationalIntentDefinition(
        "request_external_action",
        (
            "отправь сообщение", "отправь это сообщение", "отправить сообщение", "отправь письмо",
            "send message", "send email", "stuur bericht",
        ),
    ),
)

FOLLOW_UP_PHRASES = frozenset(
    {
        "объясни", "обьясни", "объясните", "объясни подробнее", "обьясни подробнее",
        "поясни", "подробнее",
        "расскажи подробнее", "что это значит", "что делать", "а дальше", "и дальше",
        "дальше", "переведи",
        "проверь", "explain", "tell me more", "leg uit",
    }
)

DOCUMENT_REVIEW_FOLLOW_UP_SIGNALS = (
    "краткое объяснение",
    "объяснение содержания",
    "поиск рисков",
    "риски",
    "проверка оплаты",
    "проверка сроков",
    "оплаты/сроков",
    "оплата",
    "сроки",
    "payment",
    "deadline",
    "risk",
    "summary",
)

REGULATED_GUARD_SIGNALS = (
    "company form", "company", "partnership", "business cooperation", "ownership",
    "supplier", "client responsibility", "registering activity", "permit", "rights",
    "obligations", "penalty", "компан", "партнер", "сотрудничеств", "владен",
    "поставщик", "клиент", "обязан", "право", "штраф", "лиценз", "разрешен",
)

NON_REGULATED_DOMAINS = {"event_collaboration", "testbox_product"}


def signal_matches(value: str, signal: str) -> bool:
    """Avoid short token matches such as IND inside the Dutch word `vind`."""
    if signal.isascii() and signal.isalnum() and len(signal) <= 3:
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(signal)}(?![a-z0-9])", value))
    return signal in value


def normalize_terms(text: str) -> tuple[str, list[dict[str, str]]]:
    normalized = text
    changes: list[dict[str, str]] = []
    for term in TERM_REGISTRY:
        if term.variant.casefold() in normalized.casefold():
            normalized = re.sub(
                re.escape(term.variant),
                term.canonical,
                normalized,
                flags=re.IGNORECASE,
            )
            changes.append(
                {"from": term.variant, "to": term.canonical, "rule": term.rule}
            )
    return normalized, changes


def is_follow_up(text: str) -> bool:
    value = re.sub(r"[?!.,;:]+$", "", text.casefold().strip())
    value = re.sub(r"\s+", " ", value)
    if value in FOLLOW_UP_PHRASES:
        return True
    return bool(
        re.fullmatch(
            r"(?:а\s+)?(?:какие|в\s+чем)\s+"
            r"(?:риски|минусы|последствия|опасности)(?:\s+для\s+меня)?",
            value,
        )
    )


def classify_orientation(text: str) -> OrientationClassification:
    value = text.casefold()
    candidates = [
        domain.id
        for domain in DOMAIN_REGISTRY
        if any(signal_matches(value, signal) for signal in domain.signals)
    ]
    # A recognized employment term must not be degraded into an ambiguous generic contract.
    if "employment_contract" in candidates and "contracts" in candidates:
        candidates.remove("contracts")
    if "zzp_intermediary_contract" in candidates and "contracts" in candidates:
        candidates.remove("contracts")
    if "consulting_services" in candidates and "business_formation" in candidates:
        candidates.remove("business_formation")
    if "event_collaboration" in candidates:
        candidates = [
            candidate
            for candidate in candidates
            if candidate == "event_collaboration"
            or candidate not in {"immigration"}
        ]
    if (
        "battery_manufacturing" in candidates
        and "business_formation" not in candidates
        and any(
            signal in value
            for signal in (
                "производить", "производств", "продават", "выводить на рынок",
                "manufactur", "produce", "sell", "market", "verkopen", "produceren",
            )
        )
    ):
        candidates.append("business_formation")
    if len(candidates) == 1:
        non_regulated = candidates[0] in NON_REGULATED_DOMAINS
        return OrientationClassification(
            primary_domain=candidates[0],
            domain_candidates=candidates,
            confidence=0.92,
            regulated_domain_guard=not non_regulated,
            source_required=not non_regulated,
        )
    if len(candidates) > 1:
        return OrientationClassification(
            primary_domain=candidates[0],
            domain_candidates=candidates,
            confidence=0.65,
            classification_mode="multi_domain",
            regulated_domain_guard=True,
            source_required=True,
            uncertain=True,
        )
    if any(signal in value for signal in REGULATED_GUARD_SIGNALS):
        return OrientationClassification(
            primary_domain="regulated_domain_candidate",
            domain_candidates=["legal_general", "business_formation", "contracts"],
            confidence=0.45,
            classification_mode="multi_domain",
            regulated_domain_guard=True,
            source_required=True,
            uncertain=True,
        )
    return OrientationClassification(primary_domain="general")


def identify_intent(classification: OrientationClassification, text: str = "") -> str:
    domains = set(classification.domain_candidates)
    value = text.casefold()
    if (
        any(signal in value for signal in ("без подтверждения", "без одобрения", "без approve", "without approval"))
        and any(signal in value for signal in ("отправ", "send", "stuur", "execute", "выполн"))
    ):
        return "request_unapproved_external_execution"
    if "cooperatie ua" in text.casefold():
        return "explain_cooperative_ua"
    if {"business_formation", "battery_manufacturing"}.issubset(domains):
        return "launch_regulated_energy_storage_manufacturing_business"
    for definition in OPERATIONAL_INTENT_REGISTRY:
        if any(signal in value for signal in definition.signals):
            return definition.intent
    for definition in DOMAIN_REGISTRY:
        if definition.id in domains:
            return definition.intent
    if classification.regulated_domain_guard:
        return "regulated_domain_orientation"
    return "general_assistance"
