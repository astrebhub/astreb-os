from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

from .models import Action, AuditEvent, utc_now


def _json_dict(model: object) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return json.loads(model.json())


class ActionQueue:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _read(self) -> list[Action]:
        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return [
            Action.model_validate(row) if hasattr(Action, "model_validate") else Action.parse_obj(row)
            for row in payload
        ]

    def _write(self, actions: list[Action]) -> None:
        payload = [_json_dict(action) for action in actions]
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary_path.replace(self.path)

    def add(self, action: Action) -> Action:
        with self._lock:
            actions = self._read()
            actions.append(action)
            self._write(actions)
        return action

    def list(self) -> list[Action]:
        with self._lock:
            return self._read()

    def get(self, action_id: str) -> Action | None:
        with self._lock:
            return next((action for action in self._read() if action.id == action_id), None)

    def update(self, changed: Action) -> Action:
        with self._lock:
            actions = self._read()
            for index, action in enumerate(actions):
                if action.id == changed.id:
                    actions[index] = changed
                    self._write(actions)
                    return changed
        raise KeyError(changed.id)


class AstiAuditLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def append(self, event: AuditEvent) -> AuditEvent:
        with self._lock, self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(_json_dict(event)) + "\n")
        return event

    def list(self, action_id: str | None = None) -> list[AuditEvent]:
        if not self.path.exists():
            return []
        events: list[AuditEvent] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    payload = json.loads(line)
                    event = (
                        AuditEvent.model_validate(payload)
                        if hasattr(AuditEvent, "model_validate")
                        else AuditEvent.parse_obj(payload)
                    )
                except (json.JSONDecodeError, ValueError):
                    continue
                if action_id is None or event.action_id == action_id:
                    events.append(event)
        return events


class ProcessedTelegramUpdates:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _read(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def claim(self, update_id: int | str) -> bool:
        key = str(update_id)
        with self._lock:
            updates = self._read()
            if key in updates:
                return False
            updates[key] = utc_now()
            temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
            temporary_path.write_text(json.dumps(updates, indent=2), encoding="utf-8")
            temporary_path.replace(self.path)
            return True
