from __future__ import annotations

import re
from pathlib import Path

from .constitution import instructions_for
from .document_intelligence import assess_document_input
from .event_bus import RuntimeEventBus
from .grounded_answer import AnswerContext, GroundedAnswerComposer
from .jurisdiction_resolver import (
    detect_jurisdiction as resolve_detect_jurisdiction,
    infer_jurisdiction,
)
from .legal_sources import retrieve_sources
from .models import (
    ApprovalState,
    EventType,
    OrientationClassification,
    RiskLevel,
    RuntimeEvent,
    RuntimeResponse,
    SessionContext,
    UserMessageRequest,
)
from .orientation_core import OrientationCore
from .policy_engine import (
    ACTIVE_TASK_EXECUTION_POLICY,
    GOVERNANCE_BALANCE_POLICY,
    HUMAN_REVIEW_POLICY,
    LIMITATION_REPORTING_POLICY,
)
from .roles import role_assignment_for
from .session_store import JsonSessionContextStore


def detect_language(text: str, requested_language: str | None = None) -> str:
    if requested_language in {"ru", "nl", "en"}:
        return requested_language
    if re.search(r"[А-Яа-яЁё]", text):
        return "ru"
    if any(token in text.casefold() for token in ["fiets", "auto", "schade", "gemeente"]):
        return "nl"
    return "en"


def detect_jurisdiction(text: str) -> str:
    value = text.casefold()
    if any(
        token in value
        for token in [
            "netherlands",
            "nederland",
            "amsterdam",
            "ind",
            "uwv",
            "gemeente",
            "belasting",
            "нидерланд",
            "голланд",
            "fiets",
            "fietser",
            "wegenverkeerswet",
        ]
    ):
        return "Netherlands"
    return "unknown"


DOMAIN_SIGNALS = {
    "business_formation": [
        "кооператив", "создавать компанию", "создание компании", "открыть компани", "форма компании",
        "программного обеспечения", "команда специалистов", "software company",
        "software product", "legal structure", "cooperative", "cooperatie",
        "private limited", "startup company", "bv or", "bv или",
    ],
    "battery_manufacturing": [
        "источник хранения электричества", "источников хранения электричества",
        "накопител", "аккумулятор", "батаре", "хранение энергии",
        "energy storage", "battery", "batteries", "accumulator",
    ],
    "liability": [
        "велосипед", "велосипедист", "дтп", "авари", "компенсац", "ущерб",
        "fiets", "fietser", "aanrijding", "schadevergoeding", "aansprakelijk",
        "traffic accident", "cyclist", "bicycle",
    ],
    "immigration": ["украин", "temporary protection", "ind", "residence", "внж", "виза"],
    "employment": ["salary", "wage", "зарплат", "работодател", "увольнен"],
    "tax": ["tax", "belasting", "налог", "штраф налог"],
    "contracts": ["contract", "договор", "соглашен"],
    "insurance": ["insurance", "verzekering", "страхов"],
    "benefits": ["benefit", "toeslag", "пособ"],
    "data_privacy": ["gdpr", "privacy", "персональн", "данных"],
    "social_housing": [
        "социальное жилье", "социального жилья", "социальную аренду",
        "социальной аренды", "социальная аренда", "social housing",
        "sociale huurwoning", "woningcorporatie", "huurwoning",
    ],
    "employment_contract": [
        "нулевой контракт", "нулевого контракта", "нулевому контракту",
        "контракт без часов", "нулевые часы", "0-hour contract", "nulurencontract",
        "nul uren contract", "zero-hours contract", "zero hours contract",
        "oproepcontract",
    ],
}

REGULATED_GUARD_SIGNALS = [
    "company form", "company", "partnership", "business cooperation", "ownership",
    "supplier", "client responsibility", "registering activity", "permit", "rights",
    "obligations", "penalty", "компан", "партнер", "сотрудничеств", "владен",
    "поставщик", "клиент", "обязан", "право", "штраф", "лиценз", "разрешен",
]


def classify_orientation(text: str) -> OrientationClassification:
    value = text.casefold()
    candidates = [
        domain for domain, signals in DOMAIN_SIGNALS.items()
        if any(signal in value for signal in signals)
    ]
    if "employment_contract" in candidates and "contracts" in candidates:
        candidates.remove("contracts")
    if len(candidates) == 1:
        return OrientationClassification(
            primary_domain=candidates[0],
            domain_candidates=candidates,
            confidence=0.92,
            regulated_domain_guard=True,
            source_required=True,
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


def classify_domain(text: str) -> str:
    return classify_orientation(text).primary_domain


TERM_NORMALIZATION_RULES = [
    ("предлогают", "предлагают", "typo_correction"),
    ("нулевой контракт", "nulurencontract", "regulated_term"),
    ("нулевые часы", "nulurencontract", "regulated_term"),
    ("zero hours contract", "nulurencontract", "regulated_term"),
    ("zero-hours contract", "nulurencontract", "regulated_term"),
    ("0-hour contract", "nulurencontract", "regulated_term"),
    ("cooperatie ua", "cooperatie UA", "regulated_term"),
    ("кооператив ua", "cooperatie UA", "regulated_term"),
]

FOLLOW_UP_PHRASES = {
    "объясни", "обьясни", "объясните", "поясни", "подробнее",
    "расскажи подробнее", "что это значит", "что делать", "переведи",
    "проверь", "explain", "tell me more", "leg uit",
}


def normalize_terms(text: str) -> tuple[str, list[dict[str, str]]]:
    normalized = text
    changes: list[dict[str, str]] = []
    for original, replacement, rule in TERM_NORMALIZATION_RULES:
        if original.casefold() in normalized.casefold():
            normalized = re.sub(re.escape(original), replacement, normalized, flags=re.IGNORECASE)
            changes.append({"from": original, "to": replacement, "rule": rule})
    return normalized, changes


def identify_intent(classification: OrientationClassification, text: str = "") -> str:
    domains = set(classification.domain_candidates)
    if "cooperatie ua" in text.casefold():
        return "explain_cooperative_ua"
    if {"business_formation", "battery_manufacturing"}.issubset(domains):
        return "launch_regulated_energy_storage_manufacturing_business"
    if "business_formation" in domains:
        return "choose_business_structure"
    if "employment" in domains:
        return "employment_rights_orientation"
    if "social_housing" in domains:
        return "check_social_housing_eligibility"
    if "employment_contract" in domains:
        return "understand_zero_hours_employment_contract"
    if "liability" in domains:
        return "liability_orientation"
    if classification.regulated_domain_guard:
        return "regulated_domain_orientation"
    return "general_assistance"


def human_review_reason(
    classification: OrientationClassification,
    risk: RiskLevel,
) -> str | None:
    if "battery_manufacturing" in classification.domain_candidates:
        return "regulated_energy_storage_manufacturing_requires_specialist_review"
    if classification.uncertain:
        return "low_classification_confidence"
    if risk == RiskLevel.HIGH:
        return "high_risk_policy"
    if risk == RiskLevel.EMERGENCY:
        return "critical_risk_policy"
    return None


class LegalBoxRuntime:
    def __init__(self, audit_path: Path) -> None:
        self.events = RuntimeEventBus(audit_path)
        self.session_context = JsonSessionContextStore(
            audit_path.parent / "testbox_session_context.json"
        )
        self.answer_composer = GroundedAnswerComposer()
        self.orientation_core = OrientationCore()

    def _event(
        self,
        request: UserMessageRequest,
        action: EventType,
        *,
        route: str,
        policies: list[str],
        risk: RiskLevel,
        jurisdiction: str,
        source_refs: list[str] | None = None,
        approval_state: ApprovalState = ApprovalState.AUTO,
        payload: dict | None = None,
    ) -> RuntimeEvent:
        return self.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route=route,
                policy=policies,
                risk_level=risk,
                jurisdiction=jurisdiction,
                source_refs=source_refs or [],
                action=action,
                approval_state=approval_state,
                payload=payload or {},
            )
        )

    def process_message(self, request: UserMessageRequest) -> RuntimeResponse:
        message_value = request.message.strip()
        stored_context = self.session_context.get(request.user_session)
        document_processing = assess_document_input(
            request.document_text,
            request.attachment_names,
            request.document_extraction,
        )
        document_text = document_processing.extracted_text
        language = detect_language(
            f"{message_value}\n\n{document_text or ''}".strip(), request.language
        )
        orientation = self.orientation_core.orient(
            message_value,
            language=language,
            document_text=document_text,
            attachment_names=request.attachment_names,
            stored_context=stored_context,
            conversation_history=request.conversation_history,
        )
        previous_topic = orientation.previous_topic
        reused_context = orientation.context_reused
        orientation_text = orientation.original_text
        normalized_text = orientation.normalized_text
        normalization_changes = orientation.normalization_changes
        combined_text = orientation.combined_text
        route = "Intake"
        emitted: list[RuntimeEvent] = []

        jurisdiction = orientation.jurisdiction
        classification = orientation.classification
        intent = orientation.intent
        answer_strategy = orientation.answer_strategy
        runtime_roles = role_assignment_for(orientation)
        domain = classification.primary_domain
        risk = orientation.risk_level
        approval_state = orientation.approval_state
        policies = orientation.policies
        pii_detected = orientation.pii_detected
        retrieval_domains = (
            classification.domain_candidates
            if classification.source_required
            else []
        )
        sources = []
        seen_source_ids: set[str] = set()
        for retrieval_domain in retrieval_domains:
            for source in retrieve_sources(
                combined_text,
                retrieval_domain,
                require_keyword_match=(
                    classification.uncertain or retrieval_domain == "employment"
                ),
            ):
                if source.id not in seen_source_ids:
                    sources.append(source)
                    seen_source_ids.add(source.id)
        if answer_strategy == "explain_cooperative_ua":
            sources = [source for source in sources if source.id == "businessgov-cooperative"]
        if (
            reused_context
            and stored_context
            and jurisdiction == "unknown"
            and stored_context.jurisdiction_candidate != "unknown"
        ):
            jurisdiction = stored_context.jurisdiction_candidate
            jurisdiction_basis = "session_context"
        else:
            jurisdiction, jurisdiction_basis = infer_jurisdiction(
                jurisdiction,
                classification,
                sources,
            )
        missing_source_domains = [
            candidate
            for candidate in retrieval_domains
            if candidate != "legal_general"
            and not any(candidate in source.domains for source in sources)
        ]
        if classification.source_required and not sources:
            risk = RiskLevel.HIGH
            approval_state = ApprovalState.REQUIRES_HUMAN_REVIEW
            for policy in (HUMAN_REVIEW_POLICY, LIMITATION_REPORTING_POLICY, GOVERNANCE_BALANCE_POLICY):
                if policy not in policies:
                    policies.append(policy)
        review_reason = (
            "external_action_requires_explicit_approval"
            if intent in {"external_action_request", "external_action_bypass_attempt"}
            else human_review_reason(classification, risk)
        )
        orientation.jurisdiction = jurisdiction
        orientation.risk_level = risk
        orientation.approval_state = approval_state
        orientation.policies = policies
        orientation.human_review_required = (
            approval_state == ApprovalState.REQUIRES_HUMAN_REVIEW
        )
        behavioral_instructions = instructions_for(orientation, runtime_roles)

        emitted.append(
            self._event(
                request,
                EventType.MESSAGE_RECEIVED,
                route=route,
                policies=[],
                risk=RiskLevel.LOW,
                jurisdiction=jurisdiction,
                payload={"message_length": len(request.message)},
            )
        )
        emitted.append(
            self._event(
                request,
                EventType.USER_MESSAGE_RECEIVED,
                route=route,
                policies=[],
                risk=RiskLevel.LOW,
                jurisdiction=jurisdiction,
                payload={"message_length": len(request.message)},
            )
        )
        if normalization_changes:
            emitted.append(
                self._event(
                    request,
                    EventType.TERM_NORMALIZED,
                    route="Orientation Layer",
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    approval_state=approval_state,
                    payload={
                        "original_text": orientation_text,
                        "normalized_text": normalized_text,
                        "normalizations": normalization_changes,
                    },
                )
            )
        if reused_context:
            emitted.append(
                self._event(
                    request,
                    EventType.CONTEXT_REUSED,
                    route="Orientation Layer",
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    approval_state=approval_state,
                    payload={
                        "context_source": "previous_user_message",
                        "previous_topic": previous_topic,
                        "follow_up": message_value,
                    },
                )
            )
            emitted.append(
                self._event(
                    request,
                    EventType.FOLLOW_UP_RESOLVED,
                    route="Orientation Layer",
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    approval_state=approval_state,
                    payload={
                        "follow_up": message_value,
                        "resolved_topic": normalized_text,
                        "domain": domain,
                        "intent": intent,
                    },
                )
            )
        emitted.append(
            self._event(
                request,
                EventType.LANGUAGE_DETECTED,
                route=route,
                policies=[],
                risk=risk,
                jurisdiction=jurisdiction,
                payload={"language": language},
            )
        )
        emitted.append(
            self._event(
                request,
                EventType.INTENT_DETECTED,
                route="Orientation Layer",
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                approval_state=approval_state,
                payload={
                    "intent": intent,
                    "strategy": answer_strategy,
                    "domains": orientation.domain_graph,
                    "sources_required": classification.source_required,
                },
            )
        )
        emitted.append(
            self._event(
                request,
                EventType.DOMAIN_GRAPH_CREATED,
                route="Orientation Layer",
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                approval_state=approval_state,
                payload={
                    "primary_domain": domain,
                    "domains": orientation.domain_graph,
                },
            )
        )
        emitted.append(
            self._event(
                request,
                EventType.SITUATION_MODEL_CREATED,
                route="Orientation Layer",
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                approval_state=approval_state,
                payload=(
                    orientation.situation.model_dump(mode="json")
                    if orientation.situation
                    else {}
                ),
            )
        )
        emitted.append(
            self._event(
                request,
                EventType.MODE_SELECTED,
                route="Orientation Layer",
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                approval_state=approval_state,
                payload={"mode": orientation.mode, "route_key": orientation.route_key},
            )
        )
        emitted.append(
            self._event(
                request,
                EventType.ROLE_ASSIGNMENT_SELECTED,
                route="Orientation Layer",
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                approval_state=approval_state,
                payload={
                    "primary_role": runtime_roles.primary_role,
                    "active_roles": runtime_roles.active_roles,
                    "reason": runtime_roles.reason,
                },
            )
        )
        emitted.append(
            self._event(
                request,
                EventType.BEHAVIORAL_INSTRUCTIONS_APPLIED,
                route="Orientation Layer",
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                approval_state=approval_state,
                payload={
                    "system_instruction": behavioral_instructions.system_instruction,
                    "role_instructions": behavioral_instructions.role_instructions,
                    "skill_instructions": behavioral_instructions.skill_instructions,
                    "policy_instructions": behavioral_instructions.policy_instructions,
                },
            )
        )
        emitted.append(
            self._event(
                request,
                EventType.JURISDICTION_DETECTED,
                route=route,
                policies=[],
                risk=risk,
                jurisdiction=jurisdiction,
                payload={
                    "jurisdiction": jurisdiction,
                    "jurisdiction_basis": jurisdiction_basis,
                },
            )
        )
        if jurisdiction_basis != "explicit_user_context" and jurisdiction != "unknown":
            emitted.append(
                self._event(
                    request,
                    EventType.JURISDICTION_INFERRED,
                    route="Orientation Layer",
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    approval_state=approval_state,
                    payload={
                        "jurisdiction": jurisdiction,
                        "basis": jurisdiction_basis,
                        "domain": domain,
                    },
                )
            )
        emitted.append(
            self._event(
                request,
                EventType.LEGAL_CLASSIFIED,
                route=route,
                policies=[],
                risk=risk,
                jurisdiction=jurisdiction,
                payload={
                    "domain": domain,
                    "domain_candidates": classification.domain_candidates,
                    "confidence": classification.confidence,
                    "classification_mode": classification.classification_mode,
                    "regulated_domain_guard": classification.regulated_domain_guard,
                    "source_required": classification.source_required,
                },
            )
        )
        if classification.uncertain:
            emitted.append(
                self._event(
                    request,
                    EventType.CLASSIFICATION_UNCERTAIN,
                    route="Orientation Layer",
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    approval_state=approval_state,
                    payload={
                        "domain_candidates": classification.domain_candidates,
                        "confidence": classification.confidence,
                        "classification_mode": classification.classification_mode,
                        "human_review_reason": review_reason,
                    },
                )
            )
        emitted.append(
            self._event(
                request,
                EventType.RISK_FLAGGED,
                route=route,
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                approval_state=approval_state,
                payload={"risk_level": risk},
            )
        )
        if pii_detected:
            emitted.append(
                self._event(
                    request,
                    EventType.PII_DETECTED,
                    route="Local preprocessing",
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    approval_state=approval_state,
                    payload={"handling": "mask_before_external_route"},
                )
            )

        if domain != "general":
            emitted.append(
                self._event(
                    request,
                    EventType.SOURCE_REQUIRED,
                    route="Legal Retrieval",
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    approval_state=approval_state,
                    payload={
                        "domain": domain,
                        "domain_candidates": classification.domain_candidates,
                        "confidence": classification.confidence,
                        "sources_required": True,
                    },
                )
            )
            emitted.append(
                self._event(
                    request,
                    EventType.LEGAL_RETRIEVAL_COMPLETED,
                    route="Legal Retrieval",
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    source_refs=[source.id for source in sources],
                    approval_state=approval_state,
                    payload={
                        "source_count": len(sources),
                        "covered_domains": [
                            candidate for candidate in retrieval_domains
                            if any(candidate in source.domains for source in sources)
                        ],
                        "missing_source_domains": missing_source_domains,
                    },
                )
            )

        route = self._select_route(domain, answer_strategy, risk, bool(sources), pii_detected)
        retained_messages = list(stored_context.last_user_messages) if stored_context else []
        retained_messages.extend(request.conversation_history)
        retained_messages.append(message_value)
        deduplicated_messages: list[str] = []
        for retained_message in retained_messages:
            if not deduplicated_messages or deduplicated_messages[-1] != retained_message:
                deduplicated_messages.append(retained_message)
        stateful_intents = {
            "letter_draft",
            "document_review",
            "action_plan",
            "business_orientation",
            "regulated_business_creation",
            "legal_orientation",
            "external_action_request",
            "external_action_bypass_attempt",
        }
        preserve_current_task = domain != "general" or intent in stateful_intents
        self.session_context.put(request.user_session, SessionContext(
            last_user_messages=deduplicated_messages[-5:],
            active_topic=normalized_text if preserve_current_task else (
                stored_context.active_topic if stored_context else ""
            ),
            domain=domain if preserve_current_task else (
                stored_context.domain if stored_context else "general"
            ),
            jurisdiction_candidate=jurisdiction,
            intent=intent if preserve_current_task else (
                stored_context.intent if stored_context else intent
            ),
            active_task=intent if preserve_current_task else (
                stored_context.active_task if stored_context else intent
            ),
            domain_graph=orientation.domain_graph if preserve_current_task else (
                stored_context.domain_graph if stored_context else []
            ),
            mode=orientation.mode if preserve_current_task else (
                stored_context.mode if stored_context else orientation.mode
            ),
            uploaded_documents=(request.attachment_names or (
                stored_context.uploaded_documents if stored_context else []
            )),
            governance_state=policies,
            unresolved=preserve_current_task or approval_state == ApprovalState.REQUIRES_HUMAN_REVIEW,
            route=route,
        ))
        emitted.append(
            self._event(
                request,
                EventType.ROUTE_SELECTED,
                route=route,
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                source_refs=[source.id for source in sources],
                approval_state=approval_state,
                payload={"route_key": orientation.route_key, "mode": orientation.mode},
            )
        )
        emitted.append(
            self._event(
                request,
                EventType.ROUTING_SELECTED,
                route=route,
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                source_refs=[source.id for source in sources],
                approval_state=approval_state,
            )
        )

        final_response = self.answer_composer.compose(
            AnswerContext(
                language=language,
                message=normalized_text,
                domain=domain,
                domain_candidates=classification.domain_candidates,
                intent=answer_strategy,
                jurisdiction=jurisdiction,
                risk=risk,
                sources=sources,
                approval_state=approval_state,
                document_text=document_text,
                attachment_names=request.attachment_names,
                document_processing=document_processing,
            )
        )
        if classification.uncertain and missing_source_domains:
            final_response = self._uncertainty_notice(language, missing_source_domains) + final_response
        emitted.append(
            self._event(
                request,
                EventType.ANSWER_STRATEGY_SELECTED,
                route=route,
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                source_refs=[source.id for source in sources],
                approval_state=approval_state,
                payload={"strategy": answer_strategy, "mode": orientation.mode},
            )
        )
        if ACTIVE_TASK_EXECUTION_POLICY in policies:
            readable_text_available = document_processing.extraction_status == "readable_text_received"
            result = "output_produced"
            operation = {
                "draft_letter": "draft_generation",
                "review_document": "document_analysis",
                "build_action_plan": "action_plan_generation",
                "assess_situation": "situation_analysis",
            }.get(answer_strategy, "governed_orientation")
            if answer_strategy == "review_document" and not readable_text_available:
                result = "limited_no_readable_text"
            emitted.append(
                self._event(
                    request,
                    EventType.ACTIVE_TASK_EXECUTION_ATTEMPTED,
                    route=route,
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    source_refs=[source.id for source in sources],
                    approval_state=approval_state,
                    payload={
                        "policy": ACTIVE_TASK_EXECUTION_POLICY,
                        "operation": operation,
                        "result": result,
                        "mode": orientation.mode,
                    },
                )
            )
        if answer_strategy == "review_document" and ACTIVE_TASK_EXECUTION_POLICY in policies:
            emitted.append(
                self._event(
                    request,
                    EventType.DOCUMENT_EXTRACTION_ATTEMPTED,
                    route=route,
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    approval_state=approval_state,
                    payload={
                        "extracted_text_available": bool(document_processing.extracted_text),
                        "extraction_status": document_processing.extraction_status,
                        "method": document_processing.method,
                        "confidence": document_processing.confidence,
                        "pages_seen": document_processing.pages_seen,
                        "limitation_reason": document_processing.limitation_reason,
                        "provenance": document_processing.provenance,
                    },
                )
            )
            if document_processing.ocr_required:
                emitted.append(
                    self._event(
                        request,
                        EventType.OCR_REQUIRED,
                        route=route,
                        policies=policies,
                        risk=risk,
                        jurisdiction=jurisdiction,
                        approval_state=approval_state,
                        payload={
                            "reason": document_processing.limitation_reason,
                            "provenance": document_processing.provenance,
                        },
                    )
                )
            emitted.append(
                self._event(
                    request,
                    EventType.ACTIVE_TASK_ANALYSIS_ATTEMPTED,
                    route=route,
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    source_refs=[source.id for source in sources],
                    approval_state=approval_state,
                    payload={
                        "policy": ACTIVE_TASK_EXECUTION_POLICY,
                        "attachments": request.attachment_names,
                        "readable_text_available": readable_text_available,
                        "mode": orientation.mode,
                    },
                )
            )
        if LIMITATION_REPORTING_POLICY in policies:
            emitted.append(
                self._event(
                    request,
                    EventType.LIMITATION_REPORTED,
                    route=route,
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    source_refs=[source.id for source in sources],
                    approval_state=approval_state,
                    payload={
                        "policy": LIMITATION_REPORTING_POLICY,
                        "reason": (
                            "no_readable_document_text"
                            if answer_strategy == "review_document"
                            else "required_official_source_not_available"
                        ),
                        "mode": orientation.mode,
                    },
                )
            )
        emitted.append(
            self._event(
                request,
                EventType.ANSWER_GENERATED,
                route=route,
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                source_refs=[source.id for source in sources],
                approval_state=approval_state,
                payload={"source_bound": bool(sources), "domain": domain},
            )
        )
        emitted.append(
            self._event(
                request,
                EventType.DISCLAIMER_ATTACHED,
                route=route,
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                source_refs=[source.id for source in sources],
                approval_state=approval_state,
            )
        )
        if approval_state == ApprovalState.REQUIRES_HUMAN_REVIEW:
            emitted.append(
                self._event(
                    request,
                    EventType.HUMAN_REVIEW_REQUIRED,
                    route=route,
                    policies=policies,
                    risk=risk,
                    jurisdiction=jurisdiction,
                    source_refs=[source.id for source in sources],
                    approval_state=approval_state,
                    payload={
                        "human_review_reason": review_reason,
                        "domains": classification.domain_candidates,
                        "sources_required": classification.source_required,
                    },
                )
            )
        emitted.append(
            self._event(
                request,
                EventType.MEMORY_UPDATED,
                route=route,
                policies=policies,
                risk=risk,
                jurisdiction=jurisdiction,
                source_refs=[source.id for source in sources],
                approval_state=approval_state,
                payload={
                    "memory_scope": "orientation_metadata_local_durable_store",
                    "persistent": True,
                    "active_task": intent,
                    "mode": orientation.mode,
                    "pii_storage": "explicit_email_phone_bsn_patterns_redacted",
                },
            )
        )

        return RuntimeResponse(
            user_session=request.user_session,
            role=request.role,
            route=route,
            risk_level=risk,
            jurisdiction=jurisdiction,
            approval_state=approval_state,
            policies=policies,
            sources=sources,
            classification=classification,
            orientation=orientation,
            runtime_roles=runtime_roles,
            behavioral_instructions=behavioral_instructions,
            document_extraction=(
                document_processing
                if answer_strategy == "review_document" or request.attachment_names
                else None
            ),
            final_response=final_response,
            events=emitted,
        )

    def _select_route(
        self,
        domain: str,
        intent: str,
        risk: RiskLevel,
        has_sources: bool,
        has_pii: bool,
    ) -> str:
        if intent == "request_external_action":
            return "ASTI -> Pending Approval"
        if intent == "request_unapproved_external_execution":
            return "ASTI -> Approval Bypass Blocked"
        if intent == "draft_letter":
            return "LetterBox -> Draft Generation"
        if intent == "review_document":
            return "DocumentBox -> Analysis Attempt"
        if domain == "event_collaboration":
            return "Orientation -> Coordination Planning"
        if intent in {"build_action_plan", "assess_situation"}:
            return "Orientation -> Active Analysis"
        if domain == "general":
            return "Local AI"
        prefix = "Local preprocessing -> " if has_pii else ""
        legal = "Legal Retrieval" if has_sources else "Source Clarification"
        if risk == RiskLevel.HIGH:
            return f"{prefix}{legal} -> Governed Draft -> Human Review"
        return f"{prefix}{legal} -> Governed Draft"

    def _uncertainty_notice(self, language: str, missing_domains: list[str]) -> str:
        missing = ", ".join(missing_domains)
        if language == "ru":
            return (
                "Внимание: запрос затрагивает несколько регулируемых областей, "
                f"а текущий реестр источников не полностью покрывает: {missing}. "
                "Ответ требует проверки человеком.\n\n"
            )
        if language == "nl":
            return (
                "Let op: deze vraag raakt meerdere gereguleerde gebieden en het "
                f"huidige bronnenregister dekt nog niet volledig: {missing}. "
                "Menselijke controle is vereist.\n\n"
            )
        return (
            "Notice: this request touches multiple regulated domains and the "
            f"current source registry does not fully cover: {missing}. "
            "Human review is required.\n\n"
        )

    def _answer(
        self,
        *,
        language: str,
        message: str,
        domain: str,
        domain_candidates: list[str],
        intent: str,
        jurisdiction: str,
        risk: RiskLevel,
        sources: list,
        approval_state: ApprovalState,
    ) -> str:
        risk_label = {
            "ru": {
                "low": "низкий",
                "medium": "средний",
                "high": "высокий",
                "emergency": "критический",
            },
            "nl": {
                "low": "laag",
                "medium": "middel",
                "high": "hoog",
                "emergency": "kritiek",
            },
            "en": {
                "low": "low",
                "medium": "medium",
                "high": "high",
                "emergency": "critical",
            },
        }.get(language, {}).get(risk.value, risk.value)
        approval_label = {
            "ru": {
                "AUTO": "автоматическая обработка",
                "SUGGESTED_REVIEW": "рекомендуется проверка человеком",
                "REQUIRES_HUMAN_REVIEW": "требуется проверка человеком",
                "DENIED": "отклонено",
            },
            "nl": {
                "AUTO": "automatische verwerking",
                "SUGGESTED_REVIEW": "menselijke controle aanbevolen",
                "REQUIRES_HUMAN_REVIEW": "menselijke controle vereist",
                "DENIED": "afgewezen",
            },
            "en": {
                "AUTO": "automatic processing",
                "SUGGESTED_REVIEW": "human review recommended",
                "REQUIRES_HUMAN_REVIEW": "human review required",
                "DENIED": "denied",
            },
        }.get(language, {}).get(approval_state.value, approval_state.value)
        if domain != "general" and not sources:
            if language == "ru":
                return (
                    "Я распознал юридический вопрос, но не нашел подключенных "
                    "официальных источников по этой теме. Поэтому я не буду "
                    "формулировать правовой вывод без подтверждения. Уточните "
                    "страну и область права или приложите официальный документ. "
                    "Реестр источников требует расширения, а запрос направлен на "
                    "проверку человеком."
                )
            if language == "nl":
                return (
                    "Ik herken een juridische vraag, maar heb geen gekoppelde "
                    "officiele bron voor dit onderwerp gevonden. Daarom geef ik "
                    "geen juridische conclusie zonder onderbouwing. Verduidelijk "
                    "land en rechtsgebied of voeg een officieel document toe. "
                    "Het bronnenregister moet worden uitgebreid en menselijke "
                    "controle is vereist."
                )
            return (
                "LegalBox cannot provide legal orientation without connected "
                "official sources. Clarify jurisdiction/domain or attach a source. "
                "The source registry must be expanded and human review is required."
            )

        if domain == "liability" and language == "ru":
            source_lines = "\n\n".join(
                f"{idx}. {source.title}\n{source.url}\n{source.summary}"
                for idx, source in enumerate(sources, start=1)
            )
            return (
                "1. Краткий ответ\n\n"
                "Если ДТП произошло в Нидерландах и участвовали автомобиль и "
                "велосипедист, требование о компенсации не является автоматически "
                "незаконным только потому, что велосипедист врезался сам. По "
                "статье 185 Wegenverkeerswet 1994 владелец или держатель "
                "моторного транспортного средства может отвечать за вред, если "
                "не доказан overmacht/форс-мажор.\n\n"
                f"2. Источники\n\n{source_lines}\n\n"
                "3. Следующие шаги\n\n"
                "1. Не признавайте вину и не платите напрямую до проверки.\n"
                "2. Передайте требование в свою WA/автостраховку.\n"
                "3. Соберите фото, видео, схему, свидетелей, accident form и "
                "переписку.\n"
                "4. Попросите письменное обоснование суммы и основания требования.\n\n"
                f"4. Уровень контроля\n\nРиск: {risk_label}. Решение: {approval_label}.\n\n"
                "Disclaimer: это информационная правовая ориентация, не точный "
                "юридический совет и не решение по делу."
            )

        if domain == "liability" and language == "nl":
            source_lines = "\n\n".join(
                f"{idx}. {source.title}\n{source.url}\n{source.summary}"
                for idx, source in enumerate(sources, start=1)
            )
            return (
                "1. Kort antwoord\n\n"
                "Als het ongeval in Nederland plaatsvond met een auto en een "
                "fietser, is de schadeclaim niet automatisch onrechtmatig omdat "
                "de fietser tegen de auto aanreed. Artikel 185 Wegenverkeerswet "
                "1994 kan de eigenaar of houder van het motorrijtuig aansprakelijk "
                "maken, tenzij overmacht aannemelijk is.\n\n"
                f"2. Bronnen\n\n{source_lines}\n\n"
                "3. Volgende stappen\n\n"
                "1. Erken geen aansprakelijkheid en betaal niet rechtstreeks zonder controle.\n"
                "2. Meld de claim bij uw WA/autoverzekeraar.\n"
                "3. Verzamel foto's, video, situatieschets, getuigen en het schadeformulier.\n"
                "4. Vraag om schriftelijke onderbouwing van de claim.\n\n"
                "Disclaimer: dit is informatieve juridische orientatie, geen "
                "definitief juridisch advies en geen besluit in uw zaak."
            )

        if "battery_manufacturing" in domain_candidates:
            if language == "ru":
                source_notes = {
                    "businessgov-choose-legal-structure": (
                        "Официальный портал для предпринимателей Нидерландов объясняет, "
                        "что правовая форма влияет на ответственность и налогообложение; "
                        "для производственной компании обычно нужно сравнить BV и другие формы."
                    ),
                    "businessgov-private-limited-bv": (
                        "Business.gov.nl описывает BV как отдельное юридическое лицо, "
                        "подходящее для владения активами, заключения договоров и привлечения инвесторов."
                    ),
                    "eurlex-batteries-regulation-2023-1542": (
                        "Регламент ЕС 2023/1542 распространяется на батареи, включая "
                        "промышленные батареи для хранения энергии, и устанавливает "
                        "обязанности производителя по соответствию, документации, маркировке и CE."
                    ),
                    "businessgov-battery-producer-responsibility": (
                        "При выводе батарей или аккумуляторов на рынок Нидерландов "
                        "производитель или импортёр несёт расширенную ответственность "
                        "за управление отходами батарей (UPV)."
                    ),
                    "businessgov-environment-harmful-activities-permit": (
                        "Для производственной площадки деятельность с воздействием на "
                        "окружающую среду может потребовать omgevingsvergunning, "
                        "уведомления или представления информации."
                    ),
                }
                source_lines = "\n\n".join(
                    f"{idx}. {source.title}\n{source.url}\n"
                    f"{source_notes.get(source.id, source.summary)}"
                    for idx, source in enumerate(sources, start=1)
                )
                return (
                    "1. Краткий вывод\n\n"
                    "Если вы планируете в Нидерландах или для рынка ЕС открыть компанию "
                    "по производству накопителей энергии, вопрос относится одновременно "
                    "к созданию бизнеса и регулируемому производству батарей. Для проекта "
                    "с оборудованием, ответственностью за продукт, инвестициями и интеллектуальной "
                    "собственностью разумно в первую очередь изучать BV, но форму нельзя "
                    "выбирать отдельно от требований к самому продукту и производственной площадке.\n\n"
                    "2. Что нужно уточнить\n\n"
                    "- В какой стране будет зарегистрирована компания и где находится производство?\n"
                    "- Это аккумуляторные модули/батареи, стационарные системы хранения или другая технология?\n"
                    "- Продукт будет продаваться в ЕС, устанавливаться у клиентов или использоваться только внутри предприятия?\n"
                    "- Планируются ли химические вещества, переработка, хранение опасных материалов или импорт компонентов?\n\n"
                    "3. Какие блоки проверки обязательны для Нидерландов/ЕС\n\n"
                    "1. Правовая форма и ответственность: сравнение BV с альтернативами, "
                    "владение технологией и договорами.\n"
                    "2. Требования к батарее: техническая документация, оценка соответствия, "
                    "маркировка и CE в случаях, предусмотренных Регламентом ЕС о батареях.\n"
                    "3. Ответственность производителя: организация сбора и обработки отходов "
                    "батарей при выводе продукции на рынок Нидерландов.\n"
                    "4. Производственная площадка: предварительная проверка экологических "
                    "разрешений, уведомлений и требований по месту размещения.\n\n"
                    f"4. Официальные источники\n\n{source_lines}\n\n"
                    "5. Следующий шаг\n\n"
                    "Сначала зафиксируйте страну, тип накопителя, предполагаемые объёмы "
                    "производства и рынок продаж. После этого можно подготовить карту: "
                    "регистрация BV, IP, разрешения площадки, product compliance, UPV "
                    "и необходимые специалисты (нотариус, экологический консультант, "
                    "специалист по сертификации батарей).\n\n"
                    "Уровень контроля: высокий, потому что речь идёт о производстве "
                    "регулируемого изделия и потенциальных экологических и продуктовых рисках. "
                    "Перед запуском требуется проверка специалистом.\n\n"
                    "Дисклеймер: это информационная ориентация по официальным источникам "
                    "Нидерландов и ЕС, а не персональная юридическая, техническая или "
                    "экологическая консультация."
                )
            if language == "nl":
                return (
                    "Deze vraag gaat niet alleen over het oprichten van een onderneming, "
                    "maar ook over gereguleerde productie van batterijen/energieopslag. "
                    "Voor Nederland en de EU moet u naast de rechtsvorm ook de EU "
                    "Batterijenverordening, producentenverantwoordelijkheid en mogelijke "
                    "milieuvergunningen voor de locatie beoordelen.\n\n"
                    "Disclaimer: informatieve orientatie; laat dit toetsen door bevoegde specialisten."
                )
            return (
                "This question concerns both business formation and regulated battery or "
                "energy-storage manufacturing. For the Netherlands/EU, review the legal "
                "entity alongside the EU Batteries Regulation, producer responsibility "
                "and possible environmental permits for the manufacturing site.\n\n"
                "Disclaimer: informational orientation; obtain specialist review before launch."
            )

        if domain == "social_housing":
            if language == "ru":
                return (
                    "1. Краткий ответ\n\n"
                    "Если вы спрашиваете о Нидерландах, право получить социальную "
                    "арендную квартиру через woningcorporatie зависит прежде всего от "
                    "вашего дохода, состава домохозяйства, регистрации в жилищной "
                    "организации и местных правил муниципалитета. Поскольку страну и "
                    "муниципалитет вы пока не указали, Нидерланды определены как "
                    "предполагаемая юрисдикция, а не подтверждённый факт.\n\n"
                    "2. Основные условия в Нидерландах на 2026 год\n\n"
                    "- Необходимо зарегистрироваться в woningcorporatie или иной "
                    "организации, распределяющей социальные квартиры.\n"
                    "- В некоторых муниципалитетах требуется huisvestingsvergunning "
                    "(разрешение на заселение).\n"
                    "- Woningcorporatie проверяет доход и размер домохозяйства.\n"
                    "- Не менее 85% освобождающихся социальных квартир корпорации "
                    "должны распределять домохозяйствам с доходом до €51 537 в год "
                    "для одного человека или до €56 910 для нескольких человек.\n"
                    "- Для социальной аренды базовая месячная арендная плата в 2026 "
                    "году составляет не более €932,93.\n\n"
                    "3. Что мне нужно от вас для точной проверки\n\n"
                    "1. Ваш муниципалитет или город в Нидерландах.\n"
                    "2. Вы один или живёте семьёй/с партнёром и детьми.\n"
                    "3. Ваш приблизительный общий годовой доход домохозяйства.\n"
                    "4. Нужна ли вам обычная очередь или есть срочная причина "
                    "(медицинская ситуация, утрата жилья, снос жилья и т.п.).\n\n"
                    "4. Что делать сейчас\n\n"
                    "Уточните муниципалитет и зарегистрируйтесь в местной системе "
                    "woningcorporatie. Если есть чрезвычайная жилищная ситуация, "
                    "узнайте в муниципалитете о подаче на urgentieverklaring: "
                    "условия приоритета различаются по муниципалитетам.\n\n"
                    "5. Официальные источники\n\n"
                    "1. Rijksoverheid - Kom ik in aanmerking voor een sociale huurwoning?\n"
                    "https://www.rijksoverheid.nl/onderwerpen/huurwoning-zoeken/"
                    "vraag-en-antwoord/wanneer-kom-ik-in-aanmerking-voor-een-sociale-huurwoning\n"
                    "Условия социальной аренды, регистрация, доходные границы и "
                    "максимальная базовая аренда на 2026 год.\n\n"
                    "2. Rijksoverheid - Krijg ik een urgentieverklaring voor een sociale huurwoning?\n"
                    "https://www.rijksoverheid.nl/onderwerpen/huurwoning-zoeken/"
                    "vraag-en-antwoord/wanneer-krijg-ik-een-urgentieverklaring-voor-een-huurwoning\n"
                    "Приоритетная очередь возможна в отдельных обстоятельствах; "
                    "правила определяются муниципалитетом.\n\n"
                    "Дисклеймер: это информационная ориентация по официальным "
                    "источникам Нидерландов. Окончательное решение о допуске и "
                    "распределении жилья принимает woningcorporatie или муниципалитет."
                )
            if language == "nl":
                return (
                    "Als u Nederland bedoelt, hangt toegang tot een sociale huurwoning "
                    "af van inkomen, huishoudgrootte, inschrijving bij een "
                    "woningcorporatie en gemeentelijke regels. Geef uw gemeente, "
                    "huishoudgrootte en gezamenlijk jaarinkomen op voor een gerichtere "
                    "controle. Bij spoed kunt u bij uw gemeente informeren naar een "
                    "urgentieverklaring.\n\n"
                    "Disclaimer: informatieve orientatie op basis van Rijksoverheid; "
                    "de woningcorporatie of gemeente beslist."
                )
            return (
                "If you mean the Netherlands, social housing eligibility depends on "
                "income, household size, registration with a housing corporation and "
                "municipal rules. Provide your municipality, household size and "
                "approximate annual household income for a more specific check. In an "
                "urgent housing situation, ask the municipality about an urgency declaration.\n\n"
                "Disclaimer: informational orientation based on Rijksoverheid; the "
                "housing corporation or municipality makes the decision."
            )

        if domain == "employment_contract":
            if language == "ru":
                return (
                    "1. Что это значит\n\n"
                    "Если речь идёт о Нидерландах, под «нулевым контрактом» обычно "
                    "понимают `nulurencontract`: трудовой договор по вызову, в котором "
                    "заранее не установлено фиксированное количество рабочих часов. "
                    "Вы работаете, когда работодатель вызывает вас, а оплата обычно "
                    "начисляется за фактически отработанные часы.\n\n"
                    "2. Что важно знать до подписания\n\n"
                    "- Вы остаётесь работником и имеете трудовые права, а не просто "
                    "исполнителем без гарантий.\n"
                    "- Вызов на работу обычно должен поступить минимум за 4 дня; "
                    "если работодатель отменяет или меняет вызов позднее, может "
                    "сохраняться право на оплату вызванных часов.\n"
                    "- В предусмотренных случаях один вызов оплачивается минимум "
                    "за 3 часа, даже если работы было меньше.\n"
                    "- После 12 месяцев работы работодатель должен предложить "
                    "фиксированное количество часов, основанное на среднем объёме работы.\n"
                    "- Вам положены отпускные часы и как минимум 8% vakantiegeld "
                    "от заработанного брутто-дохода.\n\n"
                    "3. Что проверить в самом договоре\n\n"
                    "1. Страну работы и применимую CAO (коллективное соглашение).\n"
                    "2. Ставку оплаты, порядок вызова и отмены смен.\n"
                    "3. Правила оплаты при болезни и при отсутствии вызовов.\n"
                    "4. Срок договора, испытательный срок и порядок прекращения.\n"
                    "5. Есть ли письменное указание, что это `oproepovereenkomst` "
                    "или `nulurencontract`.\n\n"
                    "4. Важное изменение правил\n\n"
                    "Официальный портал Business.gov.nl указывает, что запрет "
                    "нулевых контрактов объявлен с предполагаемой датой вступления "
                    "в силу 1 января 2027 года; до подписания следует проверить, "
                    "вступило ли изменение в силу и применяется ли исключение к вашей ситуации.\n\n"
                    "5. Официальные источники\n\n"
                    "1. Rijksoverheid - Welke contracten zijn er voor oproepkrachten?\n"
                    "https://www.rijksoverheid.nl/vraag-en-antwoord/"
                    "arbeidsovereenkomst-en-cao/welke-contracten-zijn-er-voor-oproepkrachten\n\n"
                    "2. Rijksoverheid - Nulurencontract, vakantiedagen en vakantiegeld\n"
                    "https://www.rijksoverheid.nl/onderwerpen/arbeidsovereenkomst-en-cao/"
                    "vraag-en-antwoord/nulurencontract-en-vakantiedagen-en-vakantiegeld\n\n"
                    "3. Business.gov.nl - Hiring on-call employees with a zero-hours contract\n"
                    "https://business.gov.nl/staff/employing-staff/"
                    "hiring-on-call-employees-with-a-zero-hours-contract/\n\n"
                    "Дисклеймер: это информационная ориентация по официальным "
                    "источникам Нидерландов. Перед подписанием договора можно "
                    "показать его Juridisch Loket, профсоюзу или юристу по трудовому праву."
                )
            if language == "nl":
                return (
                    "Een nulurencontract is een oproepovereenkomst zonder vast "
                    "aantal uren. U werkt wanneer u wordt opgeroepen, maar houdt "
                    "arbeidsrechten, waaronder vakantie en vakantiegeld. Controleer "
                    "oproeptermijn, loon, cao en regels na 12 maanden voordat u tekent."
                )
            return (
                "In the Netherlands, a zero-hours contract is an on-call employment "
                "contract without fixed hours. You remain an employee with rights "
                "including holiday entitlement; check call notice, pay, applicable "
                "collective agreement and the fixed-hours offer rule before signing."
            )

        if intent == "explain_cooperative_ua":
            if language == "ru":
                return (
                    "1. Что означает cooperatie UA\n\n"
                    "`Cooperatie UA` в Нидерландах означает кооператив с исключённой "
                    "ответственностью участников: `Uitgesloten van Aansprakelijkheid`. "
                    "Кооператив является отдельным юридическим лицом, а его участники "
                    "по выбранной форме UA не отвечают по долгам кооператива, включая "
                    "ситуацию банкротства. Этот выбор закрепляется в уставе при создании.\n\n"
                    "2. Чем UA отличается от других вариантов\n\n"
                    "- `UA` - ответственность участников исключена.\n"
                    "- `BA` - ответственность участников ограничена суммой, указанной в уставе.\n"
                    "- `WA` - участники несут установленную законом ответственность и "
                    "могут совместно отвечать по долгам кооператива.\n\n"
                    "3. Что UA не отменяет\n\n"
                    "UA защищает участников именно от долгов кооператива в качестве "
                    "членов. Она не означает, что руководитель никогда не несёт "
                    "ответственности: директор может отвечать лично, например при "
                    "ненадлежащем управлении, небрежности или проблемах с регистрацией. "
                    "Кроме того, личные гарантии по кредитам или собственные нарушения "
                    "нужно оценивать отдельно.\n\n"
                    "4. Когда такая форма может подходить\n\n"
                    "Cooperatie UA может быть логичной, если несколько самостоятельных "
                    "специалистов или компаний хотят совместно получать проекты, "
                    "продавать услуги или пользоваться общей инфраструктурой, сохраняя "
                    "возможность входа и выхода участников. Если же вы создаёте один "
                    "продукт с единым IP, долями основателей и инвестициями, её всё равно "
                    "нужно сравнить с BV.\n\n"
                    "5. Что нужно оформить\n\n"
                    "Для учреждения cooperatie нужен нотариус. В уставе важно определить "
                    "форму `UA`, цели кооператива, правила членства, голоса, распределение "
                    "доходов, выход участника и владение интеллектуальной собственностью. "
                    "Нотариус обычно регистрирует кооператив и директоров в KVK, а также "
                    "UBO, если применимо.\n\n"
                    "6. Официальный источник\n\n"
                    "Business.gov.nl - Setting up a cooperative in the Netherlands\n"
                    "https://business.gov.nl/running-your-business/legal-forms-and-governance/cooperative/\n\n"
                    "Источник указывает три формы ответственности участников: UA, BA и "
                    "WA; для UA участники не отвечают по долгам кооператива, включая "
                    "банкротство, при этом ответственность директора может сохраняться "
                    "в исключительных случаях.\n\n"
                    "Следующий шаг: если вы рассматриваете cooperatie UA для вашего "
                    "проекта, опишите участников, IP, инвестиции и способ получения "
                    "дохода; тогда её можно предметно сравнить с BV.\n\n"
                    "Дисклеймер: это информационная ориентация по официальному источнику "
                    "Нидерландов, а не персональная юридическая или налоговая консультация."
                )
            if language == "nl":
                return (
                    "Een cooperatie UA is een cooperatie met uitgesloten "
                    "aansprakelijkheid: leden zijn niet aansprakelijk voor schulden "
                    "van de cooperatie, ook niet na faillissement. Dit moet in de "
                    "statuten worden vastgelegd. Bestuurdersaansprakelijkheid kan in "
                    "uitzonderlijke gevallen wel blijven bestaan.\n\n"
                    "Bron: https://business.gov.nl/running-your-business/legal-forms-and-governance/cooperative/"
                )
            return (
                "A Dutch cooperatie UA is a cooperative with excluded member "
                "liability: members are not liable for the cooperative's debts, "
                "including after bankruptcy, when this is established in the "
                "articles of association. Exceptional director liability may still "
                "apply.\n\n"
                "Source: https://business.gov.nl/running-your-business/legal-forms-and-governance/cooperative/"
            )

        if domain == "business_formation":
            source_lines = "\n\n".join(
                f"{idx}. {source.title}\n{source.url}\n{source.summary}"
                for idx, source in enumerate(sources, start=1)
            )
            if language == "ru":
                return (
                    "1. Краткий вывод\n\n"
                    "Если речь о компании в Нидерландах для группы специалистов, "
                    "которая создаёт программное обеспечение и затем продаёт или "
                    "лицензирует продукты, базовым кандидатом обычно является BV "
                    "(besloten vennootschap). Она лучше подходит, когда нужны "
                    "единая компания-владелец IP, доли участников, инвестиции, "
                    "контракты с клиентами и ограничение личной ответственности.\n\n"
                    "Кооператив (cooperatie) может быть сильным вариантом, если "
                    "участники остаются самостоятельными предпринимателями, "
                    "совместно получают проекты или делят инфраструктуру, а состав "
                    "участников должен гибко меняться. Для одного продуктового "
                    "стартапа с общим кодом и инвестиционной перспективой он часто "
                    "сложнее, чем BV.\n\n"
                    "2. Как выбирать\n\n"
                    "- BV: один продукт, единый IP, доли основателей, будущие инвесторы, найм персонала.\n"
                    "- Cooperatie: сеть независимых специалистов, совместные заказы, членство может меняться.\n"
                    "- VOF: проще начать вместе, но участники лично отвечают по долгам; для продуктового ПО с рисками обычно требует особой осторожности.\n\n"
                    "3. Что нужно оформить независимо от формы\n\n"
                    "- кому принадлежит исходный код, бренд, модели и данные;\n"
                    "- доли, голосование, распределение прибыли и выход участника;\n"
                    "- IP assignment и лицензии на сторонние компоненты;\n"
                    "- ответственность за ошибки продукта, privacy/GDPR и безопасность;\n"
                    "- порядок принятия новых участников и разрешения конфликтов.\n\n"
                    f"4. Официальные источники\n\n{source_lines}\n\n"
                    "5. Практический следующий шаг\n\n"
                    "Составьте таблицу: кто владеет продуктом, нужны ли инвестиции, "
                    "будут ли участники сотрудниками или независимыми членами, как "
                    "делятся прибыль и ответственность. После этого обсудите BV "
                    "против cooperatie UA с нидерландским нотариусом и налоговым "
                    "консультантом до регистрации и передачи IP.\n\n"
                    "Дисклеймер: это информационная ориентация по официальным "
                    "источникам Нидерландов, а не персональная юридическая или "
                    "налоговая рекомендация."
                )
            if language == "nl":
                return (
                    "1. Korte conclusie\n\n"
                    "Voor een groep specialisten in Nederland die software en "
                    "product-IP gezamenlijk ontwikkelt en verkoopt of licentieert, "
                    "is een BV vaak de eerste structuur om serieus te onderzoeken: "
                    "een centrale eigenaar van IP, aandelen, investeerders, "
                    "klantcontracten en in beginsel beperkte prive-aansprakelijkheid.\n\n"
                    "Een cooperatie kan beter passen wanneer leden zelfstandige "
                    "ondernemers blijven, gezamenlijk opdrachten uitvoeren of "
                    "voorzieningen delen, en flexibel moeten kunnen toe- en uittreden.\n\n"
                    f"2. Officiele bronnen\n\n{source_lines}\n\n"
                    "3. Volgende stap\n\n"
                    "Leg eerst IP-eigendom, zeggenschap, winstverdeling, toetreding "
                    "en uittreding vast. Bespreek daarna BV versus cooperatie UA "
                    "met een Nederlandse notaris en fiscalist.\n\n"
                    "Disclaimer: informatieve orientatie, geen persoonlijk juridisch "
                    "of fiscaal advies."
                )
            return (
                "1. Short conclusion\n\n"
                "For a Netherlands-based group building software products and "
                "shared IP, a BV is often the first structure to examine when you "
                "need central IP ownership, founder shares, investor access and "
                "limited personal liability. A cooperative can fit better when "
                "members remain independent entrepreneurs and need flexible "
                "membership around shared assignments or services.\n\n"
                f"2. Official sources\n\n{source_lines}\n\n"
                "3. Next step\n\n"
                "Define IP ownership, governance, profit distribution, member exit "
                "and investment plans, then review BV versus cooperative UA with a "
                "Dutch civil-law notary and tax adviser.\n\n"
                "Disclaimer: informational orientation, not personalised legal or tax advice."
            )

        if domain == "employment":
            if language == "ru":
                source_notes = {
                    "rijksoverheid-wage-payment-delay": (
                        "Rijksoverheid указывает: если работодатель не платит зарплату, "
                        "работник может письменно потребовать выплату задолженности; "
                        "при отсутствии реакции возможно предъявление требования о зарплате "
                        "с юридической помощью, например через Juridisch Loket."
                    ),
                    "government-minimum-wage-less-than": (
                        "Government.nl описывает отдельную ситуацию, когда выплата ниже "
                        "установленного минимума: тогда может применяться обращение в "
                        "Nederlandse Arbeidsinspectie."
                    ),
                }
                source_lines = "\n\n".join(
                    f"{idx}. {source.title}\n{source.url}\n"
                    f"{source_notes.get(source.id, source.summary)}"
                    for idx, source in enumerate(sources, start=1)
                )
                jurisdiction_note = (
                    "Поскольку страна не указана, ниже применим путь для Нидерландов. "
                    "Если работа была в другой стране, укажите её: порядок взыскания изменится."
                    if jurisdiction == "unknown"
                    else "Запрос относится к трудовым отношениям в Нидерландах."
                )
                return (
                    "1. Краткий ответ\n\n"
                    f"{jurisdiction_note}\n\n"
                    "Если заработная плата в Нидерландах не выплачена в установленный срок, "
                    "работник может письменно потребовать выплату задолженности. Если "
                    "работодатель не реагирует, требование о выплате зарплаты можно "
                    "предъявлять с юридической помощью, например через Juridisch Loket. "
                    "При просрочке также может возникнуть право требовать установленную "
                    "законом надбавку за задержку; её размер в споре определяет суд.\n\n"
                    "2. Что нужно уточнить\n\n"
                    "- В какой стране вы работаете и где зарегистрирован работодатель?\n"
                    "- Есть ли трудовой договор, расчётные листки и дата, когда зарплата должна была поступить?\n"
                    "- Не выплачена вся зарплата или выплачено меньше установленной суммы?\n\n"
                    "3. Практические шаги для Нидерландов\n\n"
                    "1. Сохраните договор, loonstrook/расчётный листок, банковскую выписку и переписку.\n"
                    "2. Направьте работодателю письменное требование о выплате задолженности с указанием срока.\n"
                    "3. Если выплаты нет, обратитесь в Juridisch Loket, профсоюз или к юристу для loonvordering.\n"
                    "4. Если выплата ниже минимальной ставки, отдельно применим маршрут Nederlandse Arbeidsinspectie.\n\n"
                    f"4. Официальные источники\n\n{source_lines}\n\n"
                    "Уровень контроля: средний риск, рекомендуется проверка человеком перед "
                    "направлением официальной претензии.\n\n"
                    "Дисклеймер: это информационная правовая ориентация по официальным "
                    "источникам Нидерландов, а не персональная юридическая консультация."
                )
            if language == "nl":
                source_lines = "\n\n".join(
                    f"{idx}. {source.title}\n{source.url}\n{source.summary}"
                    for idx, source in enumerate(sources, start=1)
                )
                jurisdiction_note = (
                    "Omdat het land niet is vermeld, beschrijft dit antwoord de route voor Nederland. "
                    "Noem het werkland als dit anders is."
                    if jurisdiction == "unknown"
                    else "De vraag betreft een arbeidsrelatie in Nederland."
                )
                return (
                    "1. Kort antwoord\n\n"
                    f"{jurisdiction_note}\n\n"
                    "Als loon in Nederland niet op tijd wordt betaald, kunt u uw werkgever "
                    "schriftelijk verzoeken het achterstallige loon te betalen. Reageert "
                    "de werkgever niet, dan kunt u met juridische hulp een loonvordering "
                    "instellen. Bij te late betaling kan ook een wettelijke verhoging spelen.\n\n"
                    "2. Volgende stappen\n\n"
                    "Bewaar arbeidsovereenkomst, loonstroken, bankafschriften en berichten. "
                    "Stuur een schriftelijke loonvordering en vraag hulp van het Juridisch "
                    "Loket, een vakbond of jurist als betaling uitblijft. Gaat het om loon "
                    "onder het minimumloon, dan kan ook de Nederlandse Arbeidsinspectie relevant zijn.\n\n"
                    f"3. Officiele bronnen\n\n{source_lines}\n\n"
                    "Disclaimer: informatieve juridische orientatie op basis van Nederlandse "
                    "officiele bronnen, geen persoonlijk juridisch advies."
                )
            source_lines = "\n\n".join(
                f"{idx}. {source.title}\n{source.url}\n{source.summary}"
                for idx, source in enumerate(sources, start=1)
            )
            jurisdiction_note = (
                "Because no country was specified, this answer describes the Netherlands route. "
                "Provide the work country if it is different."
                if jurisdiction == "unknown"
                else "This request concerns an employment relationship in the Netherlands."
            )
            return (
                "1. Short answer\n\n"
                f"{jurisdiction_note}\n\n"
                "If salary in the Netherlands is not paid on time, an employee can make "
                "a written demand for the outstanding wages. If the employer does not "
                "respond, a wage claim can be pursued with legal support. Late payment "
                "may also lead to a statutory increase, subject to court assessment.\n\n"
                "2. Next steps\n\n"
                "Keep your employment contract, payslips, bank statement and correspondence. "
                "Send a written payment demand and seek support from Juridisch Loket, a "
                "union or a lawyer if payment is not made. If payment is below minimum wage, "
                "the Netherlands Labour Authority route may also apply.\n\n"
                f"3. Official sources\n\n{source_lines}\n\n"
                "Disclaimer: informational legal orientation based on Dutch official sources, "
                "not personalised legal advice."
            )

        source_lines = "\n\n".join(
            f"{idx}. {source.title}\n{source.url}\n{source.summary}"
            for idx, source in enumerate(sources, start=1)
        )
        if domain != "general":
            if language == "ru":
                return (
                    "1. Правовая ориентация по источникам\n\n"
                    f"Область: {domain}. Юрисдикция: {jurisdiction}. Риск: {risk_label}.\n\n"
                    f"2. Источники\n\n{source_lines}\n\n"
                    "3. Следующие шаги\n\n"
                    "Сверьте факты с указанными источниками, соберите документы, "
                    "не передавайте необработанные персональные данные и получите "
                    "проверку человеком для решения с высоким риском.\n\n"
                    "Дисклеймер: это информационная правовая ориентация, а не "
                    "юридический совет."
                )
            if language == "nl":
                return (
                    "1. Juridische orientatie op basis van bronnen\n\n"
                    f"Rechtsgebied: {domain}. Jurisdictie: {jurisdiction}. Risico: {risk_label}.\n\n"
                    f"2. Bronnen\n\n{source_lines}\n\n"
                    "3. Volgende stappen\n\n"
                    "Vergelijk de feiten met de bronnen, verzamel documenten, deel "
                    "geen onbewerkte persoonsgegevens en vraag menselijke controle "
                    "bij beslissingen met hoog risico.\n\n"
                    "Disclaimer: dit is informatieve juridische orientatie en geen juridisch advies."
                )
            return (
                "1. Source-bound legal orientation\n\n"
                f"Domain: {domain}. Jurisdiction: {jurisdiction}. Risk: {risk_label}.\n\n"
                f"2. Sources\n\n{source_lines}\n\n"
                "3. Next steps\n\n"
                "Check facts against the sources, collect documents, avoid sharing "
                "raw sensitive data, and request human/legal review for high-risk "
                "decisions.\n\n"
                f"Review status: {approval_label}.\n\n"
                "Disclaimer: informational orientation only, not legal advice."
            )

        if language == "ru":
            return (
                "Я получил ваш запрос. Напишите, какой результат вам нужен: "
                "объяснение, план действий, проверка документа, подготовка письма "
                "или разбор ситуации.\n\n"
                "Если вопрос связан с законом, деньгами, статусом пребывания, "
                "работой, ДТП или компенсацией, укажите страну и основные факты. "
                "Тогда я проверю тему по доступным официальным источникам и "
                "покажу безопасный следующий шаг."
            )
        if language == "nl":
            return (
                "Ik heb uw verzoek ontvangen. Beschrijf welk resultaat u nodig "
                "hebt: uitleg, actieplan, documentcontrole, brief of analyse van "
                "de situatie.\n\n"
                "Als de vraag gaat over recht, geld, verblijf, werk, een ongeval "
                "of compensatie, vermeld land en kernfeiten. Dan controleer ik "
                "de beschikbare officiele bronnen en geef ik een veilige volgende stap."
            )
        return (
            "I received your request. Tell me what outcome you need: explanation, "
            "action plan, document review, letter preparation, or situation "
            "analysis. If it concerns law, money, immigration, work, an accident, "
            "or compensation, include the jurisdiction and key facts so I can "
            "check available official sources."
        )
