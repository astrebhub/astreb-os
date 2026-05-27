from __future__ import annotations

import os
import secrets
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException

from runtime_auth import require_admin_token, validate_privileged_runtime_configuration

from .models import AuditEventType, DecisionRequest, ExecutorType, TaskRequest
from .service import AstiError, AstiService
from .store import ActionQueue, AstiAuditLog, ProcessedTelegramUpdates


def create_asti_router(
    base_dir: Path,
    service: AstiService | None = None,
    processed_updates: ProcessedTelegramUpdates | None = None,
) -> APIRouter:
    validate_privileged_runtime_configuration()
    router = APIRouter(tags=["asti"])
    runtime = service or AstiService(
        ActionQueue(base_dir / "action_queue" / "asti_actions.json"),
        AstiAuditLog(base_dir / "audit" / "asti_events.jsonl"),
    )
    telegram_updates = processed_updates or ProcessedTelegramUpdates(
        base_dir / "action_queue" / "telegram_processed_updates.json"
    )

    def result(operation):
        try:
            return operation()
        except AstiError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    @router.post("/asti/task")
    async def create_task(
        request: TaskRequest, x_ai_cabinet_admin_token: str | None = Header(default=None)
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        return {"action": result(lambda: runtime.create_task(request))}

    @router.get("/asti/inbox")
    async def inbox(x_ai_cabinet_admin_token: str | None = Header(default=None)):
        require_admin_token(x_ai_cabinet_admin_token)
        actions = runtime.inbox()
        return {"actions": actions, "count": len(actions)}

    @router.post("/asti/actions/{action_id}/approve")
    async def approve(
        action_id: str,
        request: DecisionRequest | None = None,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        request = request or DecisionRequest()
        return {
            "action": result(lambda: runtime.approve(action_id, request.actor, request.reason))
        }

    @router.post("/asti/actions/{action_id}/reject")
    async def reject(
        action_id: str,
        request: DecisionRequest | None = None,
        x_ai_cabinet_admin_token: str | None = Header(default=None),
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        request = request or DecisionRequest()
        return {
            "action": result(lambda: runtime.reject(action_id, request.actor, request.reason))
        }

    @router.post("/asti/actions/{action_id}/execute")
    async def execute(
        action_id: str, x_ai_cabinet_admin_token: str | None = Header(default=None)
    ):
        require_admin_token(x_ai_cabinet_admin_token)
        return {"action": result(lambda: runtime.execute(action_id))}

    @router.post("/webhooks/telegram")
    async def telegram_webhook(
        update: dict,
        x_telegram_bot_api_secret_token: str | None = Header(default=None),
    ):
        expected_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
        if (
            not expected_secret
            or x_telegram_bot_api_secret_token is None
            or not secrets.compare_digest(x_telegram_bot_api_secret_token, expected_secret)
        ):
            runtime.record_boundary_event(
                AuditEventType.INVALID_WEBHOOK_SECRET,
                "telegram_webhook",
                {"reason": "invalid_or_missing_secret"},
            )
            raise HTTPException(status_code=403, detail="invalid_telegram_webhook_secret")
        configured_chat_id = os.getenv("TELEGRAM_OWNER_CHAT_ID")
        if not configured_chat_id:
            raise HTTPException(status_code=503, detail="telegram_owner_chat_not_configured")
        message = update.get("message") or {}
        chat_id = str((message.get("chat") or {}).get("id", ""))
        if chat_id != configured_chat_id:
            raise HTTPException(status_code=403, detail="unknown_telegram_chat")
        text = str(message.get("text") or "").strip()
        command, _, argument = text.partition(" ")
        actor = f"telegram:{chat_id}"
        update_id = update.get("update_id")
        if update_id is None:
            raise HTTPException(status_code=400, detail="telegram_update_id_required")
        if not telegram_updates.claim(update_id):
            action_id = argument if command in {"/approve", "/reject", "/execute"} else None
            runtime.record_boundary_event(
                AuditEventType.DUPLICATE_WEBHOOK_UPDATE,
                actor,
                {"update_id": str(update_id), "command": command},
                action_id=action_id,
            )
            return {"status": "ignored", "reason": "duplicate_webhook_update"}

        if command == "/task":
            action = result(
                lambda: runtime.create_task(
                    TaskRequest(text=argument, executor=ExecutorType.TELEGRAM),
                    origin=actor,
                )
            )
            return {"command": "task", "action": action}
        if command == "/actions":
            actions = [
                action
                for action in runtime.inbox()
                if action.status.value in {"pending", "approved", "execution_in_progress"}
            ]
            return {"command": "actions", "actions": actions, "count": len(actions)}
        if command == "/approve":
            return {"command": "approve", "action": result(lambda: runtime.approve(argument, actor))}
        if command == "/reject":
            return {"command": "reject", "action": result(lambda: runtime.reject(argument, actor))}
        if command == "/execute":
            return {"command": "execute", "action": result(lambda: runtime.execute(argument, actor))}
        if command == "/status":
            actions = runtime.inbox()
            counts = {
                state: sum(action.status.value == state for action in actions)
                for state in (
                    "pending",
                    "approved",
                    "rejected",
                    "execution_in_progress",
                    "executed",
                )
            }
            return {"command": "status", "counts": counts, "telegram_configured": True}
        raise HTTPException(status_code=400, detail="unknown_telegram_command")

    return router
