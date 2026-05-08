from typing import Any, Dict

from .database import Database


class AgentRegistry:
    def __init__(self, database: Database):
        self.database = database

    def ensure_default(self) -> str:
        return self.register(
            {
                "id": "default_agent",
                "role": "controlled_runtime_agent",
                "instructions": "Follow AI Cabinet governance. Do not self-authorize actions.",
                "permissions": ["draft", "propose_memory_update"],
                "budget": {"daily_cost": 1.0},
                "tools": ["model_router", "action_queue"],
                "memory_scope": "operational",
                "risk_level": "medium",
                "status": "active",
            }
        )

    def register(self, record: Dict[str, Any]) -> str:
        return self.database.upsert_agent(record)
