from __future__ import annotations

from pathlib import Path

from asti.models import ActionStatus, ExecutorType, TaskRequest
from asti.service import AstiService

from .legalbox import LegalBoxRuntime
from .models import EventType, GovernedActionRequest, RuntimeEvent, RuntimeResponse, UserMessageRequest


class TestboxOrchestrator:
    """Central governed runtime that dispatches orientation decisions to bounded tools."""

    def __init__(self, audit_path: Path, asti_service: AstiService) -> None:
        self.orientation_runtime = LegalBoxRuntime(audit_path)
        self.asti_service = asti_service
        self.events = self.orientation_runtime.events

    def process_message(self, request: UserMessageRequest) -> RuntimeResponse:
        response = self.orientation_runtime.process_message(request)
        orientation = response.orientation
        if orientation is None:
            return response
        if orientation.route_key == "asti_approval_block":
            response.events.append(
                self.events.publish(
                    RuntimeEvent(
                        user_session=request.user_session,
                        role=request.role,
                        route=response.route,
                        policy=response.policies,
                        risk_level=response.risk_level,
                        jurisdiction=response.jurisdiction,
                        action=EventType.APPROVAL_REQUIRED,
                        approval_state=response.approval_state,
                        payload={"reason": "approval_bypass_prohibited"},
                    )
                )
            )
            response.events.append(
                self.events.publish(
                    RuntimeEvent(
                        user_session=request.user_session,
                        role=request.role,
                        route=response.route,
                        policy=response.policies,
                        risk_level=response.risk_level,
                        jurisdiction=response.jurisdiction,
                        action=EventType.EXECUTION_BLOCKED,
                        approval_state=response.approval_state,
                        payload={
                            "reason": "approval_bypass_prohibited",
                            "execution_performed": False,
                        },
                    )
                )
            )
            return response
        if orientation.route_key != "asti_action_queue":
            return response

        action = self.asti_service.create_task(
            TaskRequest(text=request.message, executor=ExecutorType.TELEGRAM),
            origin=f"testbox:{request.user_session}",
        )
        response.governed_action = action.model_dump(mode="json")
        response.events.append(
            self.events.publish(
                RuntimeEvent(
                    user_session=request.user_session,
                    role=request.role,
                    route=response.route,
                    policy=response.policies,
                    risk_level=response.risk_level,
                    jurisdiction=response.jurisdiction,
                    action=EventType.GOVERNED_ACTION_QUEUED,
                    approval_state=response.approval_state,
                    payload={
                        "action_id": action.id,
                        "status": action.status.value,
                        "executor": action.executor.value,
                        "source": "explicit_user_request",
                    },
                )
            )
        )
        response.events.append(
            self.events.publish(
                RuntimeEvent(
                    user_session=request.user_session,
                    role=request.role,
                    route=response.route,
                    policy=response.policies,
                    risk_level=response.risk_level,
                    jurisdiction=response.jurisdiction,
                    action=EventType.APPROVAL_REQUIRED,
                    approval_state=response.approval_state,
                    payload={
                        "action_id": action.id,
                        "reason": "external_action_requires_explicit_approval",
                    },
                )
            )
        )
        if orientation.language == "ru":
            response.final_response += (
                f"\n\nЗапрос зарегистрирован в управляемой очереди ASTI: `{action.id}` "
                "(статус: pending). Отправка возможна только после явного approve "
                "и отдельного execute."
            )
        elif orientation.language == "nl":
            response.final_response += (
                f"\n\nDe aanvraag staat in de bestuurde ASTI-wachtrij: `{action.id}` "
                "(status: pending). Verzending vereist expliciete approve en daarna execute."
            )
        else:
            response.final_response += (
                f"\n\nThe request is now in the governed ASTI queue: `{action.id}` "
                "(status: pending). Delivery requires explicit approve followed by execute."
            )
        return response

    def approve_action(self, action_id: str, request: GovernedActionRequest):
        action = self.asti_service.approve(action_id, request.role, request.reason)
        self.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route="ASTI -> Approved, Awaiting Execute",
                action=EventType.APPROVED,
                approval_state="APPROVED",
                payload={"action_id": action.id, "status": action.status.value},
            )
        )
        self.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route="ASTI -> Approved, Awaiting Execute",
                action=EventType.APPROVAL_GRANTED,
                approval_state="APPROVED",
                payload={
                    "action_id": action.id,
                    "status": action.status.value,
                    "compatibility_event_for": EventType.APPROVED.value,
                },
            )
        )
        return action

    def reject_action(self, action_id: str, request: GovernedActionRequest):
        action = self.asti_service.reject(action_id, request.role, request.reason)
        self.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route="ASTI -> Rejected",
                action=EventType.REJECTED,
                approval_state="DENIED",
                payload={"action_id": action.id, "status": action.status.value},
            )
        )
        return action

    def execute_action(self, action_id: str, request: GovernedActionRequest):
        existing = self.asti_service.get(action_id)
        if existing.status == ActionStatus.APPROVED:
            self.events.publish(
                RuntimeEvent(
                    user_session=request.user_session,
                    role=request.role,
                    route="ASTI -> Governed Execution",
                    action=EventType.EXECUTION_STARTED,
                    approval_state="APPROVED",
                    payload={"action_id": action_id, "executor": existing.executor.value},
                )
            )
        action = self.asti_service.execute(action_id, request.role)
        self.events.publish(
            RuntimeEvent(
                user_session=request.user_session,
                role=request.role,
                route="ASTI -> Executed",
                action=EventType.EXECUTED,
                approval_state="APPROVED",
                payload={"action_id": action.id, "status": action.status.value},
            )
        )
        return action
