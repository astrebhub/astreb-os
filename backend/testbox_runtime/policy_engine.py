from __future__ import annotations

import re

from .models import ApprovalState, RiskLevel


LEGAL_SOURCE_POLICY = "legal_answers_require_sources"
# Stable runtime policy alias: the public concept is source governance.
SOURCE_GOVERNANCE_POLICY = LEGAL_SOURCE_POLICY
PII_POLICY = "pii_must_be_masked_before_cloud"
HUMAN_REVIEW_POLICY = "high_risk_requires_approval"
ACTIVE_TASK_EXECUTION_POLICY = "active_task_execution_policy"
LIMITATION_REPORTING_POLICY = "limitation_reporting_policy"
GOVERNANCE_BALANCE_POLICY = "governance_balance_policy"
CONTEXT_CONTINUITY_POLICY = "context_continuity_policy"
MISSION_FACT_INTEGRITY_POLICY = "mission_fact_integrity_policy"
ASTI_EXECUTION_POLICY = "governed_external_execution_policy"
NON_REGULATED_ORIENTATION_DOMAINS = {"event_collaboration"}

HIGH_RISK_DOMAINS = {
    "immigration",
    "tax",
    "employment_termination",
    "fraud",
    "liability",
    "contracts",
    "litigation",
    "benefits_sanctions",
    "regulated_domain_candidate",
    "battery_manufacturing",
    "employment_contract",
}


def detect_pii(text: str) -> bool:
    return bool(
        re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", text, re.I)
        or re.search(r"\+?\d[\d\s-]{7,}\d", text)
        or re.search(r"\b\d{9}\b", text)
    )


def needs_legal_sources(domain: str) -> bool:
    return domain != "general" and domain not in NON_REGULATED_ORIENTATION_DOMAINS


def classify_risk(domain: str, text: str) -> RiskLevel:
    value = text.casefold()
    if any(token in value for token in ["112", "emergency", "urgent", "violence", "threat"]):
        return RiskLevel.EMERGENCY
    if domain in HIGH_RISK_DOMAINS:
        return RiskLevel.HIGH
    if domain in NON_REGULATED_ORIENTATION_DOMAINS:
        return RiskLevel.LOW
    if domain != "general":
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def approval_for(risk: RiskLevel) -> ApprovalState:
    if risk in {RiskLevel.HIGH, RiskLevel.EMERGENCY}:
        return ApprovalState.REQUIRES_HUMAN_REVIEW
    if risk == RiskLevel.MEDIUM:
        return ApprovalState.SUGGESTED_REVIEW
    return ApprovalState.AUTO


def evaluate_policies(domain: str, risk: RiskLevel, text: str) -> list[str]:
    policies: list[str] = []
    if detect_pii(text):
        policies.append(PII_POLICY)
    if needs_legal_sources(domain):
        policies.append(LEGAL_SOURCE_POLICY)
    if approval_for(risk) == ApprovalState.REQUIRES_HUMAN_REVIEW:
        policies.append(HUMAN_REVIEW_POLICY)
    return policies
