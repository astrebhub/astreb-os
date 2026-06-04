from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from .event_bus import RuntimeEventBus
from .models import ApprovalState, EventType, RiskLevel, RuntimeEvent


META_QMS_LAYERS = [
    "Orientation Layer",
    "Governance Layer",
    "Policy Layer",
    "Runtime Execution Layer",
    "Audit Layer",
    "Memory Layer",
    "Learning Layer",
    "Evolution Layer",
]

META_QMS_CYCLE = [
    "Event",
    "Context Analysis",
    "Risk Evaluation",
    "Policy Matching",
    "Routing",
    "AI/Human Decision",
    "Execution",
    "Audit",
    "Reflection",
    "Learning",
    "Evolution Proposal",
]

META_QMS_PRINCIPLES = [
    "Continuous improvement",
    "Quality at runtime",
    "Governance before action",
    "Human sovereignty",
    "Full auditability",
    "Learning from deviations",
    "Orientation over automation",
]

_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _redact(value: str) -> str:
    return _PHONE.sub("[PHONE_OR_IDENTIFIER]", _EMAIL.sub("[EMAIL]", value))


class QualityAssessmentRequest(BaseModel):
    user_session: str = "local"
    role: str = "Governance Officer"
    trigger: str = "operator_review"
    observation: str = Field(min_length=3, max_length=2000)
    deviation_category: str = "quality_gap"
    affected_layers: list[str] = Field(default_factory=lambda: ["Learning Layer", "Evolution Layer"])
    risk_level: RiskLevel = RiskLevel.MEDIUM
    evidence: list[str] = Field(default_factory=list)
    proposed_improvement: str = Field(min_length=3, max_length=2000)
    acceptance_condition: str = Field(min_length=3, max_length=2000)


class EvolutionDecisionRequest(BaseModel):
    user_session: str = "local"
    role: str = "Governance Officer"
    decision: Literal["approve", "reject"]
    reason: str = Field(min_length=3, max_length=1000)


class EvolutionProposal(BaseModel):
    id: str = Field(default_factory=lambda: f"evo-{uuid4().hex[:12]}")
    created_at: str = Field(default_factory=_utc_now)
    updated_at: str = Field(default_factory=_utc_now)
    user_session: str
    trigger: str
    deviation_category: str
    affected_layers: list[str]
    risk_level: RiskLevel
    observation: str
    evidence: list[str]
    quality_gaps: list[str]
    proposed_improvement: str
    acceptance_condition: str
    status: Literal["review_required", "approved_for_implementation", "rejected"] = "review_required"
    approval_required: bool = True
    human_decision: dict[str, str] | None = None
    automatic_execution: bool = False


class EvolutionProposalStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _read(self) -> list[EvolutionProposal]:
        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return [EvolutionProposal.model_validate(row) for row in payload if isinstance(row, dict)]

    def _write(self, proposals: list[EvolutionProposal]) -> None:
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        payload = [proposal.model_dump(mode="json") for proposal in proposals]
        temporary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary_path.replace(self.path)

    def add(self, proposal: EvolutionProposal) -> EvolutionProposal:
        with self._lock:
            proposals = self._read()
            proposals.append(proposal)
            self._write(proposals)
        return proposal

    def list(self) -> list[EvolutionProposal]:
        with self._lock:
            return self._read()

    def update(self, proposal: EvolutionProposal) -> EvolutionProposal:
        with self._lock:
            proposals = self._read()
            for index, existing in enumerate(proposals):
                if existing.id == proposal.id:
                    proposals[index] = proposal
                    self._write(proposals)
                    return proposal
        raise KeyError(proposal.id)


class MetaQmsError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class MetaQmsService:
    def __init__(self, store: EvolutionProposalStore, events: RuntimeEventBus) -> None:
        self.store = store
        self.events = events

    def overview(self) -> dict:
        proposals = self.store.list()
        pending = [proposal for proposal in proposals if proposal.status == "review_required"]
        return {
            "mode": "ASTREB META-QMS Living Evolution",
            "authority_boundary": "Proposals require human review; no automatic system change is executed.",
            "principles": META_QMS_PRINCIPLES,
            "layers": META_QMS_LAYERS,
            "runtime_cycle": META_QMS_CYCLE,
            "metrics": {
                "proposals_total": len(proposals),
                "review_required": len(pending),
                "approved_for_implementation": sum(
                    proposal.status == "approved_for_implementation" for proposal in proposals
                ),
                "rejected": sum(proposal.status == "rejected" for proposal in proposals),
            },
            "proposals": list(reversed(proposals[-20:])),
        }

    def assess(self, request: QualityAssessmentRequest) -> EvolutionProposal:
        invalid_layers = [layer for layer in request.affected_layers if layer not in META_QMS_LAYERS]
        if invalid_layers:
            raise MetaQmsError("unknown_meta_qms_layer", 422)
        evidence = [_redact(item) for item in request.evidence if item.strip()]
        quality_gaps: list[str] = []
        if not evidence:
            quality_gaps.append("Evidence is missing; validate before implementation.")
        if "Audit Layer" not in request.affected_layers:
            quality_gaps.append("Audit impact must be reviewed for every evolution proposal.")
        if request.risk_level in {RiskLevel.HIGH, RiskLevel.EMERGENCY}:
            quality_gaps.append("Elevated risk requires explicit human governance decision.")
        proposal = EvolutionProposal(
            user_session=request.user_session,
            trigger=_redact(request.trigger),
            deviation_category=_redact(request.deviation_category),
            affected_layers=request.affected_layers,
            risk_level=request.risk_level,
            observation=_redact(request.observation),
            evidence=evidence,
            quality_gaps=quality_gaps,
            proposed_improvement=_redact(request.proposed_improvement),
            acceptance_condition=_redact(request.acceptance_condition),
        )
        self.store.add(proposal)
        event_payload = {
            "proposal_id": proposal.id,
            "deviation_category": proposal.deviation_category,
            "affected_layers": proposal.affected_layers,
            "quality_gaps": proposal.quality_gaps,
            "automatic_execution": False,
        }
        self.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route="Meta-QMS -> Assessment",
                action=EventType.QUALITY_ASSESSED,
                risk_level=request.risk_level,
                approval_state=ApprovalState.REQUIRES_HUMAN_REVIEW,
                payload=event_payload,
            )
        )
        self.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route="Meta-QMS -> Deviation",
                action=EventType.DEVIATION_RECORDED,
                risk_level=request.risk_level,
                approval_state=ApprovalState.REQUIRES_HUMAN_REVIEW,
                payload=event_payload,
            )
        )
        self.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route="Meta-QMS -> Human Review",
                action=EventType.EVOLUTION_PROPOSED,
                risk_level=request.risk_level,
                approval_state=ApprovalState.REQUIRES_HUMAN_REVIEW,
                payload=event_payload,
            )
        )
        return proposal

    def decide(self, proposal_id: str, request: EvolutionDecisionRequest) -> EvolutionProposal:
        proposal = next((item for item in self.store.list() if item.id == proposal_id), None)
        if proposal is None:
            raise MetaQmsError("evolution_proposal_not_found", 404)
        if proposal.status != "review_required":
            raise MetaQmsError("evolution_proposal_already_decided", 409)
        proposal.status = (
            "approved_for_implementation" if request.decision == "approve" else "rejected"
        )
        proposal.updated_at = _utc_now()
        proposal.human_decision = {
            "role": request.role,
            "decision": request.decision,
            "reason": _redact(request.reason),
            "timestamp": proposal.updated_at,
        }
        self.store.update(proposal)
        self.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route="Meta-QMS -> Human Decision",
                action=(
                    EventType.EVOLUTION_APPROVED
                    if request.decision == "approve"
                    else EventType.EVOLUTION_REJECTED
                ),
                risk_level=proposal.risk_level,
                approval_state=(
                    ApprovalState.APPROVED if request.decision == "approve" else ApprovalState.DENIED
                ),
                payload={
                    "proposal_id": proposal.id,
                    "status": proposal.status,
                    "automatic_execution": False,
                },
            )
        )
        return proposal
