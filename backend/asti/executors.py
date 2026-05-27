from __future__ import annotations

import os
from typing import Protocol

import httpx

from .models import Action, utc_now


class Executor(Protocol):
    def execute(self, action: Action) -> dict:
        ...


class TelegramExecutor:
    def __init__(self, token: str | None = None, owner_chat_id: str | None = None) -> None:
        self.token = token if token is not None else os.getenv("TELEGRAM_BOT_TOKEN")
        self.owner_chat_id = (
            owner_chat_id if owner_chat_id is not None else os.getenv("TELEGRAM_OWNER_CHAT_ID")
        )

    def execute(self, action: Action) -> dict:
        if not self.token or not self.owner_chat_id:
            raise RuntimeError("telegram_not_configured")
        response = httpx.post(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            json={"chat_id": self.owner_chat_id, "text": action.payload["text"]},
            timeout=10.0,
        )
        if not response.is_success:
            raise RuntimeError("telegram_request_failed")
        payload = response.json()
        if not payload.get("ok"):
            raise RuntimeError("telegram_request_failed")
        result = payload.get("result") or {}
        return {
            "executor": "telegram",
            "method": "sendMessage",
            "chat_id": self.owner_chat_id,
            "message_id": result.get("message_id"),
            "telegram_message_id": result.get("message_id"),
            "telegram_ok": bool(payload.get("ok")),
            "executed_at": utc_now(),
        }


class LocalReportExecutor:
    def execute(self, action: Action) -> dict:
        return {
            "executor": "local_report",
            "delivery": "local_only",
            "text_length": len(action.payload["text"]),
            "executed_at": utc_now(),
        }


class NoOpExecutor:
    def execute(self, action: Action) -> dict:
        return {
            "executor": "no_op",
            "delivery": "none",
            "text_length": len(action.payload["text"]),
            "executed_at": utc_now(),
        }
