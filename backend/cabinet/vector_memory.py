import math
import time
import uuid
from typing import Any, Dict, List, Optional

from .database import Database


class LocalEmbeddingEngine:
    def embed(self, text: str, dimensions: int = 64) -> List[float]:
        vector = [0.0] * dimensions
        for index, char in enumerate(text.lower()):
            slot = (ord(char) + index) % dimensions
            vector[slot] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [round(value / norm, 6) for value in vector]


class VectorMemory:
    def __init__(self, database: Database, embeddings: LocalEmbeddingEngine):
        self.database = database
        self.embeddings = embeddings

    def add(self, namespace: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        record = {
            "id": str(uuid.uuid4()),
            "created_at": int(time.time()),
            "namespace": namespace,
            "content": content,
            "embedding": self.embeddings.embed(content),
            "metadata": metadata or {"provider": "local_deterministic_embedding"},
        }
        self.database.insert_vector_memory(record)
        return {"id": record["id"], "namespace": namespace, "status": "stored"}

    def search(self, namespace: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_vector = self.embeddings.embed(query)
        scored = []
        for item in self.database.all_vector_memory(namespace):
            score = self._cosine(query_vector, item["embedding"])
            scored.append({"score": round(score, 6), "content": item["content"], "metadata": item["metadata"]})
        scored.sort(key=lambda row: row["score"], reverse=True)
        return scored[:limit]

    def _cosine(self, left: List[float], right: List[float]) -> float:
        return sum(a * b for a, b in zip(left, right))
