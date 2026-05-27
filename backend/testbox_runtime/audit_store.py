from __future__ import annotations

import json
from pathlib import Path

from .models import RuntimeEvent


class JsonlAuditStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: RuntimeEvent) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            if hasattr(event, "model_dump_json"):
                handle.write(event.model_dump_json() + "\n")
            else:
                handle.write(event.json() + "\n")

    def list(self, user_session: str | None = None, limit: int = 100) -> list[RuntimeEvent]:
        if not self.path.exists():
            return []
        rows: list[RuntimeEvent] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                    event = (
                        RuntimeEvent.model_validate(payload)
                        if hasattr(RuntimeEvent, "model_validate")
                        else RuntimeEvent.parse_obj(payload)
                    )
                except (json.JSONDecodeError, ValueError):
                    continue
                if user_session and event.user_session != user_session:
                    continue
                rows.append(event)
        return rows[-limit:]
