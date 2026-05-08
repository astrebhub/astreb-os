from typing import Any, Dict, List, Optional

from .database import Database


RUNTIME_STATES = [
    "received",
    "normalized",
    "classified",
    "masked",
    "policy_checked",
    "budget_checked",
    "routed",
    "executed",
    "scanned",
    "queued",
    "approved",
    "audited",
    "memory_proposed",
    "completed",
    "failed",
    "rollback_requested",
]


class StateEngine:
    def __init__(self, database: Database):
        self.database = database

    def transition(self, request_id: str, state: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        if state not in RUNTIME_STATES:
            state = "failed"
            metadata = {"error": "invalid_state_transition", "requested_state": state}
        self.database.insert_runtime_state(request_id, state, metadata or {})
        return state

    def states(self) -> List[str]:
        return RUNTIME_STATES
