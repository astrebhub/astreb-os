import time
import uuid
from typing import Any, Dict, List

from .database import Database


class EvidenceLayer:
    def __init__(self, database: Database):
        self.database = database

    def record_sources(self, request_id: str, sources: List[Dict[str, Any]]) -> int:
        count = 0
        for source in sources:
            self.database.insert_evidence(
                {
                    "id": str(uuid.uuid4()),
                    "created_at": int(time.time()),
                    "request_id": request_id,
                    "source": source.get("source", source.get("title", "")),
                    "url": source.get("url", ""),
                    "confidence": float(source.get("confidence", 0.0)),
                    "verification_status": source.get("verification_status", "unverified"),
                    "citation": source.get("citation", ""),
                    "metadata": source,
                }
            )
            count += 1
        return count
