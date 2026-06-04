from __future__ import annotations

import json
import re
from pathlib import Path
from threading import Lock

from .models import SessionContext


_SENSITIVE_PATTERNS = (
    (re.compile(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", re.I), "[EMAIL]"),
    (re.compile(r"\+?\d[\d\s-]{7,}\d"), "[PHONE_OR_IDENTIFIER]"),
    (re.compile(r"\b\d{9}\b"), "[BSN]"),
)


def _redact_text(text: str) -> str:
    redacted = text
    for pattern, placeholder in _SENSITIVE_PATTERNS:
        redacted = pattern.sub(placeholder, redacted)
    return redacted


class JsonSessionContextStore:
    """Durable local orientation state; production can replace this adapter."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _read(self) -> dict[str, dict]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def get(self, user_session: str) -> SessionContext | None:
        with self._lock:
            payload = self._read().get(user_session)
        if not payload:
            return None
        return (
            SessionContext.model_validate(payload)
            if hasattr(SessionContext, "model_validate")
            else SessionContext.parse_obj(payload)
        )

    def put(self, user_session: str, context: SessionContext) -> None:
        if hasattr(context, "model_dump"):
            payload = context.model_dump(mode="json")
        else:
            payload = json.loads(context.json())
        payload["active_topic"] = _redact_text(payload["active_topic"])
        payload["last_user_messages"] = [
            _redact_text(message) for message in payload["last_user_messages"]
        ]
        with self._lock:
            sessions = self._read()
            sessions[user_session] = payload
            temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
            temporary_path.write_text(
                json.dumps(sessions, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            temporary_path.replace(self.path)
