from typing import Any, Dict

from .database import Database


ROLE_ACCESS = {
    "owner": 5,
    "admin": 4,
    "operator": 3,
    "agent": 2,
    "guest": 1,
    "client": 1,
}


class IdentityAccessLayer:
    def __init__(self, database: Database):
        self.database = database

    def ensure_user(self, user_id: str, requested_access: int) -> Dict[str, Any]:
        user = self.database.get_user(user_id)
        if not user:
            role = "owner" if user_id == "local_user" else "guest"
            self.database.upsert_user(
                {
                    "id": user_id,
                    "role": role,
                    "permissions": ["submit", "view_control_center"],
                    "metadata": {"created_by": "identity_access_layer"},
                }
            )
            user = self.database.get_user(user_id)

        role = user.get("role", "guest")
        max_access = ROLE_ACCESS.get(role, 1)
        return {
            "user_id": user_id,
            "role": role,
            "allowed": requested_access <= max_access,
            "max_access_level": max_access,
            "requested_access_level": requested_access,
        }
