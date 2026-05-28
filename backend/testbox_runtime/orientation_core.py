from __future__ import annotations

from .jurisdiction_resolver import detect_jurisdiction
from .models import ApprovalState, OrientationDecision, RiskLevel, SessionContext
from .orientation_registry import (
    DOCUMENT_REVIEW_FOLLOW_UP_SIGNALS,
    classify_orientation,
    identify_intent,
    is_follow_up,
    normalize_terms,
)
from .policy_engine import (
    ACTIVE_TASK_EXECUTION_POLICY,
    ASTI_EXECUTION_POLICY,
    CONTEXT_CONTINUITY_POLICY,
    GOVERNANCE_BALANCE_POLICY,
    LIMITATION_REPORTING_POLICY,
    MISSION_FACT_INTEGRITY_POLICY,
    approval_for,
    classify_risk,
    detect_pii,
    evaluate_policies,
)
from .situation_modeler import build_situation_model


DOMAIN_GRAPH_EXPANSIONS = {
    "testbox_product": [
        "quality_management_runtime",
        "governance_observability",
        "public_sector_ai_readiness",
    ],
    "event_collaboration": [
        "challenge_discovery",
        "team_matching",
        "preparation_brief",
    ],
    "battery_manufacturing": [
        "energy_storage",
        "environmental_permits",
        "producer_responsibility",
        "eu_product_compliance",
    ],
    "zzp_intermediary_contract": [
        "self_employment",
        "intermediary_contract",
        "wet_dba",
        "false_self_employment_risk",
    ],
    "residential_parking": [
        "municipal_procedure",
        "resident_parking_permit",
        "reserved_space_eligibility",
    ],
    "consulting_services": [
        "business_formation",
        "kvk_registration",
        "tax_vat",
        "client_contracts",
        "professional_liability",
        "sector_specific_licensing_check",
    ],
}


class OrientationCore:
    """Central orientation boundary before specialised runtime strategies run."""

    def orient(
        self,
        message: str,
        *,
        language: str,
        document_text: str | None = None,
        attachment_names: list[str] | None = None,
        stored_context: SessionContext | None = None,
        conversation_history: list[str] | None = None,
    ) -> OrientationDecision:
        message_value = message.strip()
        history = conversation_history or []
        previous_topic = (
            history[-1]
            if history
            else stored_context.active_topic if stored_context else ""
        )
        reused_context = bool(
            previous_topic and is_follow_up(message_value)
        )
        orientation_text = (
            f"{previous_topic}\nУточнение пользователя: {message_value}"
            if reused_context
            else message_value
        )
        normalized_text, normalization_changes = normalize_terms(orientation_text)
        combined_text = f"{normalized_text}\n\n{document_text or ''}".strip()
        classification = classify_orientation(combined_text)
        strategy = identify_intent(classification, normalized_text)
        has_active_document = bool(document_text or attachment_names)
        contract_inspection_request = bool(
            classification.primary_domain == "contracts"
            and any(
                signal in message_value.casefold()
                for signal in ("проверь", "проверить", "посмотри", "разбери", "review", "check")
            )
        )
        document_focus_request = bool(
            has_active_document
            and any(
                signal in message_value.casefold()
                for signal in DOCUMENT_REVIEW_FOLLOW_UP_SIGNALS
            )
        )
        document_context_reused = bool(
            document_focus_request
            and stored_context
            and stored_context.intent == "document_review"
        )
        if document_focus_request or contract_inspection_request:
            strategy = "review_document"
        if document_context_reused:
            reused_context = True
            if not previous_topic:
                previous_topic = "active document review"
        intent = self._canonical_intent(strategy, classification, normalized_text)
        domain_graph = self._domain_graph(classification.domain_candidates)
        situation = build_situation_model(
            normalized_text,
            intent,
            classification,
            domain_graph,
            attachment_names or [],
        )
        risk = (
            RiskLevel.HIGH
            if classification.uncertain and classification.regulated_domain_guard
            else classify_risk(classification.primary_domain, combined_text)
        )
        approval_state = approval_for(risk)
        policies = evaluate_policies(classification.primary_domain, risk, combined_text)
        active_task_requested = (
            intent in {
                "document_review",
                "letter_draft",
                "action_plan",
                "business_orientation",
                "regulated_business_creation",
                "legal_orientation",
                "event_preparation",
                "strategic_positioning",
            }
            or (intent == "explanation" and classification.primary_domain != "general")
        )
        if active_task_requested:
            policies.append(ACTIVE_TASK_EXECUTION_POLICY)
        extraction_unavailable = bool(
            document_text
            and any(
                marker in document_text.casefold()
                for marker in ("text was not extractable", "ocr is not active")
            )
        )
        if intent == "document_review" and (not document_text or extraction_unavailable):
            policies.append(LIMITATION_REPORTING_POLICY)
        if intent in {"business_orientation", "regulated_business_creation"}:
            policies.append(MISSION_FACT_INTEGRITY_POLICY)
        if classification.source_required or approval_state == ApprovalState.REQUIRES_HUMAN_REVIEW:
            policies.append(GOVERNANCE_BALANCE_POLICY)
        if reused_context:
            policies.append(CONTEXT_CONTINUITY_POLICY)
        if intent in {"external_action_request", "external_action_bypass_attempt"}:
            approval_state = ApprovalState.REQUIRES_HUMAN_REVIEW
            policies.append(ASTI_EXECUTION_POLICY)
            policies.append(GOVERNANCE_BALANCE_POLICY)
        return OrientationDecision(
            original_text=orientation_text,
            normalized_text=normalized_text,
            combined_text=combined_text,
            normalization_changes=normalization_changes,
            context_reused=reused_context,
            previous_topic=previous_topic,
            language=language,
            intent=intent,
            answer_strategy=strategy,
            classification=classification,
            situation=situation,
            domain_graph=domain_graph,
            mode=self._mode(intent, classification, risk),
            route_key=self._route_key(intent, classification, risk),
            risk_level=risk,
            source_required=classification.source_required,
            human_review_required=approval_state == ApprovalState.REQUIRES_HUMAN_REVIEW,
            pii_detected=detect_pii(combined_text),
            jurisdiction=detect_jurisdiction(combined_text),
            policies=policies,
            approval_state=approval_state,
        )

    def _canonical_intent(self, strategy: str, classification, text: str) -> str:
        if strategy == "draft_letter":
            return "letter_draft"
        if strategy == "review_document":
            return "document_review"
        if strategy == "build_action_plan":
            return "action_plan"
        if strategy == "forecast_event_challenges":
            return "forecast_event_challenges"
        if strategy == "strategic_positioning":
            return "strategic_positioning"
        if strategy == "prepare_event_participation":
            return "event_preparation"
        if strategy == "request_external_action":
            return "external_action_request"
        if strategy == "request_unapproved_external_execution":
            return "external_action_bypass_attempt"
        if strategy in {"introduce_system", "general_assistance"}:
            return "explanation"
        if strategy == "launch_regulated_energy_storage_manufacturing_business":
            return "regulated_business_creation"
        if strategy == "explain_cooperative_ua":
            return "explanation"
        if classification.primary_domain in {"business_formation", "zzp_intermediary_contract", "consulting_services"}:
            return "business_orientation"
        if classification.primary_domain != "general":
            return "explanation" if "что это значит" in text.casefold() else "legal_orientation"
        return "explanation"

    def _domain_graph(self, candidates: list[str]) -> list[str]:
        graph = list(candidates)
        for domain in candidates:
            for linked in DOMAIN_GRAPH_EXPANSIONS.get(domain, []):
                if linked not in graph:
                    graph.append(linked)
        return graph

    def _mode(self, intent: str, classification, risk: RiskLevel) -> str:
        if intent == "letter_draft":
            return "LetterBox Mode"
        if intent == "document_review":
            return "DocumentBox Mode"
        if intent in {"external_action_request", "external_action_bypass_attempt"}:
            return "ASTI Action Mode"
        if classification.primary_domain == "event_collaboration":
            return "Orientation Planning Mode"
        if classification.primary_domain == "testbox_product":
            return "Strategic Orientation Mode"
        if intent == "regulated_business_creation":
            return "Human Review Mode" if risk == RiskLevel.HIGH else "BusinessBox Mode"
        if classification.primary_domain in {"business_formation", "zzp_intermediary_contract", "consulting_services"}:
            return "BusinessBox Mode"
        if classification.primary_domain != "general":
            return "LegalBox Mode"
        return "Explain Mode"

    def _route_key(self, intent: str, classification, risk: RiskLevel) -> str:
        if intent == "letter_draft":
            return "letter_preparation"
        if intent == "document_review":
            return "document_review"
        if intent == "external_action_request":
            return "asti_action_queue"
        if intent == "external_action_bypass_attempt":
            return "asti_approval_block"
        if intent == "regulated_business_creation":
            return "regulated_manufacturing"
        if classification.primary_domain == "event_collaboration":
            return "coordination_planning"
        if classification.primary_domain == "testbox_product":
            return "strategic_positioning"
        if classification.primary_domain == "employment_contract":
            return "employment_contract"
        if classification.primary_domain in {"business_formation", "zzp_intermediary_contract", "consulting_services"}:
            return "business_orientation"
        if classification.primary_domain == "residential_parking":
            return "municipal_parking_orientation"
        if classification.primary_domain != "general":
            return "legal_retrieval"
        return "general_explanation"
