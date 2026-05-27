from __future__ import annotations

from .models import OrientationClassification, SituationModel


SITUATION_PROFILES = {
    "event_collaboration": {
        "type": "pre_hackathon_team_orientation",
        "concerns": ["challenge fit", "team discovery", "useful introduction"],
        "risks": ["joining without matching skills or expected contribution"],
        "missing": ["participant skills", "preferred challenge", "event registration details"],
    },
    "employment_contract": {
        "type": "variable_hours_employment_offer",
        "concerns": ["schedule certainty", "income stability", "employment rights"],
        "risks": ["variable income", "call-and-pay conditions"],
        "missing": ["offered contract text", "start date", "collective agreement if applicable"],
    },
    "employment": {
        "type": "employment_payment_issue",
        "concerns": ["unpaid wages", "evidence of work and agreed pay"],
        "risks": ["income loss", "statutory deadline or claim handling"],
        "missing": ["contract", "payslips", "payment due date"],
    },
    "social_housing": {
        "type": "housing_eligibility_orientation",
        "concerns": ["eligibility", "registration and allocation route"],
        "risks": ["wrong eligibility assumption"],
        "missing": ["household income", "household composition", "municipality"],
    },
    "business_formation": {
        "type": "business_structure_decision",
        "concerns": ["liability", "tax and governance", "cooperation terms"],
        "risks": ["inappropriate legal structure"],
        "missing": ["participants", "investment plan", "liability preference"],
    },
    "consulting_services": {
        "type": "professional_services_launch",
        "concerns": ["registration", "VAT", "professional liability"],
        "risks": ["uninsured professional claim", "incorrect registration or tax handling"],
        "missing": ["service scope", "client type", "regulated profession status"],
    },
    "battery_manufacturing": {
        "type": "regulated_energy_storage_manufacturing_launch",
        "concerns": ["market access", "environmental permits", "producer responsibility"],
        "risks": ["product compliance failure", "environmental non-compliance"],
        "missing": ["battery chemistry", "facility location", "market and scale"],
    },
    "liability": {
        "type": "traffic_liability_claim",
        "concerns": ["facts of collision", "insurance handling", "damage evidence"],
        "risks": ["premature admission of liability"],
        "missing": ["vehicle involvement", "damage and injury evidence", "incident record"],
    },
}

SITUATION_PROFILE_PRIORITY = (
    "event_collaboration",
    "battery_manufacturing",
    "consulting_services",
    "employment_contract",
    "employment",
    "social_housing",
    "liability",
    "business_formation",
)


def build_situation_model(
    text: str,
    intent: str,
    classification: OrientationClassification,
    domain_graph: list[str],
    attachment_names: list[str],
) -> SituationModel:
    profile_domain = next(
        (domain for domain in SITUATION_PROFILE_PRIORITY if domain in domain_graph),
        classification.primary_domain,
    )
    profile = SITUATION_PROFILES.get(profile_domain)
    if intent == "document_review":
        return SituationModel(
            situation_type="document_under_review",
            user_goal="understand document content and material risks",
            operational_concerns=["text extraction", "terms, dates and amounts"],
            implied_risks=["analysis limited by unreadable or incomplete text"],
            available_evidence=attachment_names or ["message requesting document review"],
            missing_critical_facts=["readable document text"] if not attachment_names else [],
        )
    if intent == "letter_draft":
        return SituationModel(
            situation_type="controlled_correspondence_draft",
            user_goal="prepare a usable first letter draft",
            operational_concerns=["accurate facts", "safe wording"],
            implied_risks=["draft sent without verifying details"],
            available_evidence=["stated purpose of the letter"],
            missing_critical_facts=["recipient", "key dates and amounts"],
        )
    if intent in {"external_action_request", "external_action_bypass_attempt"}:
        return SituationModel(
            situation_type="governed_external_action_request",
            user_goal="send or perform an external action",
            operational_concerns=["approval", "recipient and payload verification"],
            implied_risks=["unauthorised external execution"],
            available_evidence=["explicit action instruction"],
            missing_critical_facts=["approved final payload"],
        )
    if profile:
        return SituationModel(
            situation_type=profile["type"],
            user_goal="receive practical governed orientation",
            operational_concerns=profile["concerns"],
            implied_risks=profile["risks"],
            available_evidence=["user description"],
            missing_critical_facts=profile["missing"],
        )
    return SituationModel(
        situation_type="general_orientation_request",
        user_goal="understand the question and identify a useful next action",
        operational_concerns=["intent clarification only if task cannot be attempted"],
        available_evidence=["user message"] if text else [],
    )
