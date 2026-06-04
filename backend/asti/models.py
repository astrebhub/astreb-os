from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ActionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTION_IN_PROGRESS = "execution_in_progress"
    EXECUTED = "executed"


class ExecutorType(str, Enum):
    TELEGRAM = "telegram"
    LOCAL_REPORT = "local_report"
    NO_OP = "no_op"


class AuditEventType(str, Enum):
    CREATED = "created"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTION_BLOCKED = "execution_blocked"
    EXECUTION_STARTED = "execution_started"
    EXECUTED = "executed"
    EXECUTION_FAILED = "execution_failed"
    DUPLICATE_EXECUTE_ATTEMPT = "duplicate_execute_attempt"
    DUPLICATE_WEBHOOK_UPDATE = "duplicate_webhook_update"
    INVALID_WEBHOOK_SECRET = "invalid_webhook_secret"


class TaskRequest(BaseModel):
    text: str | None = None
    task: str | None = None
    executor: ExecutorType = ExecutorType.TELEGRAM

    def content(self) -> str:
        return (self.text or self.task or "").strip()


class DecisionRequest(BaseModel):
    actor: str = "owner"
    reason: str | None = None


class Action(BaseModel):
    id: str = Field(default_factory=lambda: f"asti-{uuid4().hex[:12]}")
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)
    status: ActionStatus = ActionStatus.PENDING
    executor: ExecutorType
    payload: dict[str, Any]
    origin: str = "api"
    approval: dict[str, Any] | None = None
    rejection: dict[str, Any] | None = None
    execution_started_at: str | None = None
    execution_attempt_id: str | None = None
    execution_metadata: dict[str, Any] | None = None


class AuditEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=utc_now)
    action_id: str | None = None
    event: AuditEventType
    actor: str
    metadata: dict[str, Any] = Field(default_factory=dict)
