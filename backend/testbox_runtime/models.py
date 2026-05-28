from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class EventType(str, Enum):
    MESSAGE_RECEIVED = "MESSAGE_RECEIVED"
    USER_MESSAGE_RECEIVED = "USER_MESSAGE_RECEIVED"
    LANGUAGE_DETECTED = "LANGUAGE_DETECTED"
    CONTEXT_REUSED = "CONTEXT_REUSED"
    TERM_NORMALIZED = "TERM_NORMALIZED"
    FOLLOW_UP_RESOLVED = "FOLLOW_UP_RESOLVED"
    JURISDICTION_INFERRED = "JURISDICTION_INFERRED"
    INTENT_DETECTED = "INTENT_DETECTED"
    SITUATION_MODEL_CREATED = "SITUATION_MODEL_CREATED"
    DOMAIN_GRAPH_CREATED = "DOMAIN_GRAPH_CREATED"
    MODE_SELECTED = "MODE_SELECTED"
    LEGAL_CLASSIFIED = "LEGAL_CLASSIFIED"
    CLASSIFICATION_UNCERTAIN = "CLASSIFICATION_UNCERTAIN"
    JURISDICTION_DETECTED = "JURISDICTION_DETECTED"
    RISK_FLAGGED = "RISK_FLAGGED"
    PII_DETECTED = "PII_DETECTED"
    SOURCE_REQUIRED = "SOURCE_REQUIRED"
    LEGAL_RETRIEVAL_COMPLETED = "LEGAL_RETRIEVAL_COMPLETED"
    ROUTING_SELECTED = "ROUTING_SELECTED"
    ROUTE_SELECTED = "ROUTE_SELECTED"
    ANSWER_STRATEGY_SELECTED = "ANSWER_STRATEGY_SELECTED"
    ACTIVE_TASK_EXECUTION_ATTEMPTED = "ACTIVE_TASK_EXECUTION_ATTEMPTED"
    ACTIVE_TASK_ANALYSIS_ATTEMPTED = "ACTIVE_TASK_ANALYSIS_ATTEMPTED"
    DOCUMENT_EXTRACTION_ATTEMPTED = "DOCUMENT_EXTRACTION_ATTEMPTED"
    OCR_REQUIRED = "OCR_REQUIRED"
    LIMITATION_REPORTED = "LIMITATION_REPORTED"
    ROLE_ASSIGNMENT_SELECTED = "ROLE_ASSIGNMENT_SELECTED"
    BEHAVIORAL_INSTRUCTIONS_APPLIED = "BEHAVIORAL_INSTRUCTIONS_APPLIED"
    GOVERNED_ACTION_QUEUED = "GOVERNED_ACTION_QUEUED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    EXECUTION_BLOCKED = "EXECUTION_BLOCKED"
    EXECUTION_STARTED = "EXECUTION_STARTED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    ANSWER_GENERATED = "ANSWER_GENERATED"
    DISCLAIMER_ATTACHED = "DISCLAIMER_ATTACHED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    AUDIT_EVENT_CREATED = "AUDIT_EVENT_CREATED"
    MEMORY_UPDATED = "MEMORY_UPDATED"
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    APPROVAL_DENIED = "APPROVAL_DENIED"
    QUALITY_ASSESSED = "QUALITY_ASSESSED"
    DEVIATION_RECORDED = "DEVIATION_RECORDED"
    EVOLUTION_PROPOSED = "EVOLUTION_PROPOSED"
    EVOLUTION_APPROVED = "EVOLUTION_APPROVED"
    EVOLUTION_REJECTED = "EVOLUTION_REJECTED"
    QUALITY_SKILLS_LOADED = "QUALITY_SKILLS_LOADED"
    QUALITY_EVALUATED = "QUALITY_EVALUATED"
    QUALITY_INTERVENTION_APPLIED = "QUALITY_INTERVENTION_APPLIED"
    LEARNING_CAPTURED = "LEARNING_CAPTURED"
    SKILL_EVOLUTION_PROPOSED = "SKILL_EVOLUTION_PROPOSED"
    SKILL_EVOLUTION_APPROVED = "SKILL_EVOLUTION_APPROVED"
    SKILL_EVOLUTION_REJECTED = "SKILL_EVOLUTION_REJECTED"


class ApprovalState(str, Enum):
    AUTO = "AUTO"
    SUGGESTED_REVIEW = "SUGGESTED_REVIEW"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"
    APPROVED = "APPROVED"
    DENIED = "DENIED"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"


class LegalSource(BaseModel):
    id: str
    title: str
    url: str
    jurisdiction: str
    domains: list[str]
    keywords: list[str]
    summary: str


class RuntimeEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    user_session: str = "local"
    role: str = "Operator"
    route: str = "unselected"
    policy: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    jurisdiction: str = "unknown"
    source_refs: list[str] = Field(default_factory=list)
    action: EventType
    approval_state: ApprovalState = ApprovalState.AUTO
    payload: dict[str, Any] = Field(default_factory=dict)


class DocumentPageExtraction(BaseModel):
    page_number: int
    text: str = ""
    confidence: float | None = None
    method: str = "provided_text"


class DocumentExtractionInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    filename: str | None = None
    extracted_text: str | None = None
    extraction_status: str = Field(
        default="provided",
        validation_alias=AliasChoices("extraction_status", "status"),
    )
    method: str = "browser_extraction"
    confidence: float | None = None
    pages_seen: int | None = Field(
        default=None,
        validation_alias=AliasChoices("pages_seen", "page_count"),
    )
    limitation_reason: str | None = None
    pages: list[DocumentPageExtraction] = Field(default_factory=list)


class DocumentProcessingState(BaseModel):
    extracted_text: str | None = None
    extraction_status: str
    confidence: float | None = None
    pages_seen: int | None = None
    limitation_reason: str | None = None
    method: str
    provenance: list[dict[str, Any]] = Field(default_factory=list)
    ocr_required: bool = False


class UserMessageRequest(BaseModel):
    message: str
    user_session: str = "local"
    role: str = "Operator"
    language: str | None = None
    document_text: str | None = None
    attachment_names: list[str] = Field(default_factory=list)
    document_extraction: DocumentExtractionInput | None = None
    conversation_history: list[str] = Field(default_factory=list)


class OrientationClassification(BaseModel):
    primary_domain: str
    domain_candidates: list[str] = Field(default_factory=list)
    confidence: float = 1.0
    classification_mode: str = "single_domain"
    regulated_domain_guard: bool = False
    source_required: bool = False
    uncertain: bool = False


class SituationModel(BaseModel):
    situation_type: str
    user_goal: str
    operational_concerns: list[str] = Field(default_factory=list)
    implied_risks: list[str] = Field(default_factory=list)
    available_evidence: list[str] = Field(default_factory=list)
    missing_critical_facts: list[str] = Field(default_factory=list)


class OrientationDecision(BaseModel):
    original_text: str
    normalized_text: str
    combined_text: str
    normalization_changes: list[dict[str, str]] = Field(default_factory=list)
    context_reused: bool = False
    previous_topic: str = ""
    language: str
    intent: str
    answer_strategy: str
    classification: OrientationClassification
    situation: SituationModel | None = None
    domain_graph: list[str] = Field(default_factory=list)
    mode: str
    route_key: str
    risk_level: RiskLevel
    source_required: bool = False
    human_review_required: bool = False
    pii_detected: bool = False
    jurisdiction: str = "unknown"
    policies: list[str] = Field(default_factory=list)
    approval_state: ApprovalState = ApprovalState.AUTO


class OperationalRole(BaseModel):
    id: str
    name: str
    purpose: str
    skills: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class RuntimeRoleAssignment(BaseModel):
    primary_role: str
    active_roles: list[str] = Field(default_factory=list)
    reason: str


class BehavioralInstruction(BaseModel):
    id: str
    level: str
    name: str
    instruction: str


class ActiveInstructionSet(BaseModel):
    system_instruction: str
    role_instructions: list[str] = Field(default_factory=list)
    skill_instructions: list[str] = Field(default_factory=list)
    policy_instructions: list[str] = Field(default_factory=list)


class SessionContext(BaseModel):
    last_user_messages: list[str] = Field(default_factory=list)
    active_topic: str = ""
    domain: str = "general"
    jurisdiction_candidate: str = "unknown"
    intent: str = "general_assistance"
    active_task: str = "general_assistance"
    domain_graph: list[str] = Field(default_factory=list)
    mode: str = "Explain Mode"
    uploaded_documents: list[str] = Field(default_factory=list)
    governance_state: list[str] = Field(default_factory=list)
    unresolved: bool = False
    route: str = "Local AI"


class RuntimeResponse(BaseModel):
    user_session: str
    role: str
    route: str
    risk_level: RiskLevel
    jurisdiction: str
    approval_state: ApprovalState
    policies: list[str]
    sources: list[LegalSource]
    classification: OrientationClassification
    orientation: OrientationDecision | None = None
    runtime_roles: RuntimeRoleAssignment | None = None
    behavioral_instructions: ActiveInstructionSet | None = None
    governed_action: dict[str, Any] | None = None
    document_extraction: DocumentProcessingState | None = None
    quality_assessment: dict[str, Any] | None = None
    final_response: str
    events: list[RuntimeEvent]


class ApprovalRequest(BaseModel):
    user_session: str = "local"
    role: str = "Governance Officer"
    decision: ApprovalState
    reason: str | None = None


class GovernedActionRequest(BaseModel):
    user_session: str = "local"
    role: str = "Governance Officer"
    reason: str | None = None
