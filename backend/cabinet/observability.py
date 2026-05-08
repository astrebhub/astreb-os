import time
import uuid
from typing import Any, Dict, Optional

from .database import Database


class ObservabilityLayer:
    def __init__(self, database: Database):
        self.database = database

    def event(
        self,
        event_type: str,
        request_id: str = "",
        severity: str = "info",
        payload: Optional[Dict[str, Any]] = None,
        started_at: Optional[float] = None,
    ) -> None:
        latency_ms = int((time.time() - started_at) * 1000) if started_at else 0
        self.database.insert_observability_event(
            {
                "id": str(uuid.uuid4()),
                "created_at": int(time.time()),
                "event_type": event_type,
                "request_id": request_id,
                "latency_ms": latency_ms,
                "severity": severity,
                "payload": payload or {},
            }
        )
