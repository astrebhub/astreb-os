from __future__ import annotations

import os
from collections.abc import Mapping
from threading import Lock
from uuid import uuid4

from .executors import Executor, LocalReportExecutor, NoOpExecutor, TelegramExecutor
from .models import (
    Action,
    ActionStatus,
    AuditEvent,
    AuditEventType,
    ExecutorType,
    TaskRequest,
    utc_now,
)
from .store import ActionQueue, AstiAuditLog


class AstiError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


ALLOWED_EXECUTORS = {"telegram", "local_report", "no_op"}


def real_external_execution_enabled() -> bool:
    return os.getenv("ASTI_EXTERNAL_EXECUTION_ENABLED", "").casefold() in {
        "1",
        "true",
        "yes",
        "on",
    }


class AstiService:
    def __init__(
        self,
        queue: ActionQueue,
        audit: AstiAuditLog,
        executors: Mapping[ExecutorType, Executor] | None = None,
    ) -> None:
        self.queue = queue
        self.audit = audit
        self._transition_lock = Lock()
        self.executors = executors or {
            ExecutorType.TELEGRAM: TelegramExecutor(),
            ExecutorType.LOCAL_REPORT: LocalReportExecutor(),
            ExecutorType.NO_OP: NoOpExecutor(),
        }

    def create_task(self, request: TaskRequest, origin: str = "api") -> Action:
        text = request.content()
        if not text:
            raise AstiError("task_text_required", 422)
        if request.executor.value not in ALLOWED_EXECUTORS:
            raise AstiError("executor_not_allowed", 422)
        action = Action(executor=request.executor, payload={"text": text}, origin=origin)
        self._audit(action, AuditEventType.CREATED, origin, {"executor": action.executor.value})
        self.queue.add(action)
        return action

    def inbox(self) -> list[Action]:
        return self.queue.list()

    def get(self, action_id: str) -> Action:
        action = self.queue.get(action_id)
        if action is None:
            raise AstiError("action_not_found", 404)
        return action

    def approve(self, action_id: str, actor: str = "owner", reason: str | None = None) -> Action:
        with self._transition_lock:
            action = self.get(action_id)
            if action.status != ActionStatus.PENDING:
                raise AstiError("only_pending_actions_can_be_approved", 409)
            action.status = ActionStatus.APPROVED
            action.updated_at = utc_now()
            action.approval = {"actor": actor, "reason": reason, "timestamp": action.updated_at}
            self._audit(action, AuditEventType.APPROVED, actor, {"reason": reason})
            self.queue.update(action)
            return action

    def reject(self, action_id: str, actor: str = "owner", reason: str | None = None) -> Action:
        with self._transition_lock:
            action = self.get(action_id)
            if action.status != ActionStatus.PENDING:
                raise AstiError("only_pending_actions_can_be_rejected", 409)
            action.status = ActionStatus.REJECTED
            action.updated_at = utc_now()
            action.rejection = {"actor": actor, "reason": reason, "timestamp": action.updated_at}
            self._audit(action, AuditEventType.REJECTED, actor, {"reason": reason})
            self.queue.update(action)
            return action

    def execute(self, action_id: str, actor: str = "owner") -> Action:
        with self._transition_lock:
            action = self.get(action_id)
            if action.status != ActionStatus.APPROVED:
                if action.status in {ActionStatus.EXECUTED, ActionStatus.EXECUTION_IN_PROGRESS}:
                    self._audit(
                        action,
                        AuditEventType.DUPLICATE_EXECUTE_ATTEMPT,
                        actor,
                        {"status": action.status.value},
                    )
                self._audit(
                    action,
                    AuditEventType.EXECUTION_BLOCKED,
                    actor,
                    {"status": action.status.value, "reason": "approval_required"},
                )
                raise AstiError("approval_required_before_execution", 409)
            if action.executor == ExecutorType.TELEGRAM and not real_external_execution_enabled():
                self._audit(
                    action,
                    AuditEventType.EXECUTION_BLOCKED,
                    actor,
                    {"status": action.status.value, "reason": "external_execution_frozen"},
                )
                raise AstiError("external_execution_frozen", 503)
            action.status = ActionStatus.EXECUTION_IN_PROGRESS
            action.updated_at = utc_now()
            action.execution_started_at = action.updated_at
            action.execution_attempt_id = str(uuid4())
            self._audit(
                action,
                AuditEventType.EXECUTION_STARTED,
                actor,
                {
                    "executor": action.executor.value,
                    "execution_attempt_id": action.execution_attempt_id,
                },
            )
            self.queue.update(action)
            try:
                executor = self.executors[action.executor]
                metadata = executor.execute(action)
            except Exception as exc:
                self._audit(
                    action,
                    AuditEventType.EXECUTION_FAILED,
                    actor,
                    {"executor": action.executor.value, "error": str(exc)},
                )
                raise AstiError(f"execution_failed: {exc}", 502) from exc
            if not isinstance(metadata, dict):
                self._audit(
                    action,
                    AuditEventType.EXECUTION_FAILED,
                    actor,
                    {"executor": action.executor.value, "error": "executor_metadata_required"},
                )
                raise AstiError("execution_failed: executor_metadata_required", 502)
            metadata = {
                **metadata,
                "executor": action.executor.value,
                "executed_at": metadata.get("executed_at") or utc_now(),
                "execution_attempt_id": action.execution_attempt_id,
            }
            action.status = ActionStatus.EXECUTED
            action.updated_at = utc_now()
            action.execution_metadata = metadata
            self._audit(action, AuditEventType.EXECUTED, actor, metadata)
            self.queue.update(action)
            return action

    def record_boundary_event(
        self,
        event: AuditEventType,
        actor: str,
        metadata: dict | None = None,
        action_id: str | None = None,
    ) -> AuditEvent:
        return self.audit.append(
            AuditEvent(
                action_id=action_id,
                event=event,
                actor=actor,
                metadata=metadata or {},
            )
        )

    def _audit(
        self, action: Action, event: AuditEventType, actor: str, metadata: dict | None = None
    ) -> AuditEvent:
        return self.audit.append(
            AuditEvent(
                action_id=action.id,
                event=event,
                actor=actor,
                metadata=metadata or {},
            )
        )
