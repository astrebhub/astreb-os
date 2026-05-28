from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Request

from asti.service import AstiError, AstiService
from runtime_auth import require_admin_token, validate_privileged_runtime_configuration

from .clipboard_bridge import ClipboardBridgeError, read_local_clipboard_text
from .constitution import constitution_registry
from .legal_sources import SOURCES
from .meta_qms import (
    EvolutionDecisionRequest,
    EvolutionProposalStore,
    MetaQmsError,
    MetaQmsService,
    QualityAssessmentRequest,
)
from .models import (
    ApprovalRequest,
    ApprovalState,
    EventType,
    GovernedActionRequest,
    RuntimeEvent,
    UserMessageRequest,
)
from .orchestration import TestboxOrchestrator
from .quality_layer import SkillEvolutionDecisionRequest, SkillEvolutionRequest
from .roles import CORE_ROLES


def create_testbox_router(base_dir: Path, asti_service: AstiService) -> APIRouter:
    validate_privileged_runtime_configuration()
    router = APIRouter(prefix="/api/testbox", tags=["testbox-runtime"])
    runtime = TestboxOrchestrator(
        base_dir / "audit" / "testbox_runtime_events.jsonl",
        asti_service,
        base_dir / "audit" / "qms_learning_records.jsonl",
    )
    meta_qms = MetaQmsService(
        EvolutionProposalStore(base_dir / "audit" / "meta_qms_evolution_proposals.json"),
        runtime.events,
    )

    @router.post("/runtime/message")
    async def process_message(
        request: UserMessageRequest,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        return runtime.process_message(request)

    @router.get("/runtime/events")
    async def list_events(
        user_session: str | None = None,
        limit: int = 100,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        return {"events": runtime.events.list(user_session=user_session, limit=limit)}

    @router.get("/runtime/sources")
    async def list_sources(x_ai_cabinet_admin_token: str | None = Header(default=None)):
        require_admin_token(x_ai_cabinet_admin_token)
        return {"sources": SOURCES}

    @router.get("/runtime/roles")
    async def list_roles(x_ai_cabinet_admin_token: str | None = Header(default=None)):
        require_admin_token(x_ai_cabinet_admin_token)
        return {"roles": CORE_ROLES}

    @router.get("/runtime/constitution")
    async def list_constitution(x_ai_cabinet_admin_token: str | None = Header(default=None)):
        require_admin_token(x_ai_cabinet_admin_token)
        return {"instructions": constitution_registry()}

    @router.get("/runtime/qms/skills")
    async def qms_skill_library(x_ai_cabinet_admin_token: str | None = Header(default=None)):
        require_admin_token(x_ai_cabinet_admin_token)
        return runtime.quality_layer.skill_library()

    @router.get("/runtime/qms/scenarios")
    async def qms_scenarios(x_ai_cabinet_admin_token: str | None = Header(default=None)):
        require_admin_token(x_ai_cabinet_admin_token)
        return runtime.quality_layer.scenario_catalog()

    @router.get("/runtime/qms/learning")
    async def qms_learning_repository(x_ai_cabinet_admin_token: str | None = Header(default=None)):
        require_admin_token(x_ai_cabinet_admin_token)
        return runtime.quality_layer.observation()

    @router.get("/runtime/qms/meta")
    async def qms_meta_recommendations(x_ai_cabinet_admin_token: str | None = Header(default=None)):
        require_admin_token(x_ai_cabinet_admin_token)
        return runtime.quality_layer.meta_qms_recommendations()

    @router.post("/runtime/qms/skills/{skill_id}/evolution")
    async def propose_skill_evolution(
        skill_id: str,
        request: SkillEvolutionRequest,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        try:
            proposal = runtime.quality_layer.propose_skill_evolution(skill_id, request)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="skill_not_found") from exc
        event = runtime.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route="QMS -> Skill Evolution",
                action=EventType.SKILL_EVOLUTION_PROPOSED,
                approval_state=ApprovalState.REQUIRES_HUMAN_REVIEW,
                payload={
                    "proposal_id": proposal.id,
                    "skill_id": proposal.skill_id,
                    "current_version": proposal.current_version,
                    "proposed_version": proposal.proposed_version,
                    "automatic_execution": False,
                },
            )
        )
        return {"proposal": proposal, "event": event, "skills": runtime.quality_layer.skill_library()}

    @router.post("/runtime/qms/skills/evolution/{proposal_id}/decision")
    async def decide_skill_evolution(
        proposal_id: str,
        request: SkillEvolutionDecisionRequest,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        try:
            proposal = runtime.quality_layer.decide_skill_evolution(proposal_id, request)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="skill_evolution_proposal_not_found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        event = runtime.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route="QMS -> Skill Evolution Decision",
                action=(
                    EventType.SKILL_EVOLUTION_APPROVED
                    if request.decision == "approve"
                    else EventType.SKILL_EVOLUTION_REJECTED
                ),
                approval_state=(
                    ApprovalState.APPROVED if request.decision == "approve" else ApprovalState.DENIED
                ),
                payload={
                    "proposal_id": proposal.id,
                    "skill_id": proposal.skill_id,
                    "status": proposal.status,
                    "automatic_execution": False,
                },
            )
        )
        return {"proposal": proposal, "event": event, "skills": runtime.quality_layer.skill_library()}

    @router.get("/runtime/meta-qms")
    async def meta_qms_overview(x_ai_cabinet_admin_token: str | None = Header(default=None)):
        require_admin_token(x_ai_cabinet_admin_token)
        return meta_qms.overview()

    @router.post("/runtime/meta-qms/assess")
    async def assess_quality(
        request: QualityAssessmentRequest,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        try:
            return {"proposal": meta_qms.assess(request), "overview": meta_qms.overview()}
        except MetaQmsError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    @router.post("/runtime/meta-qms/proposals/{proposal_id}/decision")
    async def decide_evolution_proposal(
        proposal_id: str,
        request: EvolutionDecisionRequest,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        try:
            return {"proposal": meta_qms.decide(proposal_id, request), "overview": meta_qms.overview()}
        except MetaQmsError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    @router.post("/runtime/clipboard/read")
    async def read_clipboard_for_explicit_paste(
        request: Request,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        client_host = request.client.host if request.client else ""
        if client_host not in {"127.0.0.1", "::1", "localhost", "testclient"}:
            raise HTTPException(status_code=403, detail="clipboard_local_access_only")
        try:
            text = read_local_clipboard_text()
        except ClipboardBridgeError as exc:
            raise HTTPException(status_code=503, detail="clipboard_unavailable") from exc
        return {"text": text, "storage": "not_persisted"}

    @router.post("/runtime/approval")
    async def record_approval(
        request: ApprovalRequest,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        event = runtime.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route="Human Approval",
                action=(
                    EventType.APPROVAL_GRANTED
                    if request.decision == ApprovalState.APPROVED
                    else EventType.APPROVAL_DENIED
                ),
                approval_state=request.decision,
                payload={"reason": request.reason},
            )
        )
        return {"event": event}

    def governed_action_result(operation):
        try:
            return operation()
        except AstiError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    @router.post("/runtime/actions/{action_id}/approve")
    async def approve_governed_action(
        action_id: str,
        request: GovernedActionRequest,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        return {"action": governed_action_result(lambda: runtime.approve_action(action_id, request))}

    @router.post("/runtime/actions/{action_id}/reject")
    async def reject_governed_action(
        action_id: str,
        request: GovernedActionRequest,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        return {"action": governed_action_result(lambda: runtime.reject_action(action_id, request))}

    @router.post("/runtime/actions/{action_id}/execute")
    async def execute_governed_action(
        action_id: str,
        request: GovernedActionRequest,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        return {"action": governed_action_result(lambda: runtime.execute_action(action_id, request))}

    return router
