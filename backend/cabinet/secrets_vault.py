import base64
import os
import uuid
from typing import Optional

from .database import Database


class SecretsVault:
    def __init__(self, database: Database):
        self.database = database

    def put(self, name: str, value: str, provider: str = "") -> str:
        encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
        return self.database.insert_secret(
            {
                "id": str(uuid.uuid4()),
                "name": name,
                "provider": provider,
                "encrypted_value": encoded,
                "metadata": {"encoding": "base64_mvp_placeholder"},
            }
        )

    def get(self, name: str) -> Optional[str]:
        row = self.database.get_secret(name)
        if row:
            return base64.b64decode(row["encrypted_value"]).decode("utf-8")
        return os.getenv(name.upper(), None)

    def metadata(self, name: str) -> dict:
        row = self.database.get_secret(name)
        return {"name": name, "stored": bool(row), "env_fallback": bool(os.getenv(name.upper()))}
