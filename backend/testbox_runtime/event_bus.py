from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path

from .audit_store import JsonlAuditStore
from .models import RuntimeEvent


class RuntimeEventBus:
    def __init__(self, audit_path: Path, max_events_per_session: int = 300) -> None:
        self.audit = JsonlAuditStore(audit_path)
        self.max_events_per_session = max_events_per_session
        self._events: dict[str, deque[RuntimeEvent]] = defaultdict(
            lambda: deque(maxlen=max_events_per_session)
        )

    def publish(self, event: RuntimeEvent) -> RuntimeEvent:
        self._events[event.user_session].append(event)
        self.audit.append(event)
        return event

    def list(self, user_session: str | None = None, limit: int = 100) -> list[RuntimeEvent]:
        if user_session:
            memory_events = list(self._events[user_session])[-limit:]
            if memory_events:
                return memory_events
        return self.audit.list(user_session=user_session, limit=limit)
