import time
import uuid
from typing import Any, Dict

from .database import Database


class ApprovalCenter:
    def __init__(self, database: Database):
        self.database = database

    def request(self, target_type: str, target_id: str, requested_by: str, reason: str, metadata: Dict[str, Any]) -> str:
        return self.database.insert_approval(
            {
                "id": str(uuid.uuid4()),
                "created_at": int(time.time()),
                "target_type": target_type,
                "target_id": target_id,
                "requested_by": requested_by,
                "status": "pending",
                "reason": reason,
                "metadata": metadata,
            }
        )
