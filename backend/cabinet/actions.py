import time
import uuid
from typing import Dict, Optional

from .database import Database
from .policy import PolicyDecision
from .schemas import SubmitRequest


ACTION_INTENTS = {
    "paperclip_task": ("paperclip_plugin", "create_task_draft"),
    "telegram_draft": ("telegram_plugin", "draft_message"),
    "email_draft": ("email_plugin", "draft_email"),
}


class ActionQueue:
    def __init__(self, database: Database):
        self.database = database

    def maybe_enqueue(
        self,
        request_id: str,
        req: SubmitRequest,
        risk_level: str,
        policy: PolicyDecision,
        output: str,
    ) -> Optional[Dict[str, str]]:
        intent = ACTION_INTENTS.get(req.mode)
        if not intent:
            return None

        plugin, action = intent
        status = "pending_approval" if policy.require_approval else "draft"
        action_id = str(uuid.uuid4())
        payload = self._payload(req.mode, req.task, output)
        self.database.create_action(
            {
                "id": action_id,
                "created_at": int(time.time()),
                "request_id": request_id,
                "user_id": req.user_id,
                "plugin": plugin,
                "action": action,
                "access_level": req.access_level,
                "risk_level": risk_level,
                "status": status,
                "payload": payload,
                "policy_decision": policy.name,
                "approval_note": "Queued by AI Cabinet v0.2; no direct external execution.",
            }
        )
        return {"action_id": action_id, "action_status": status}

    def approve(self, action_id: str) -> Optional[Dict[str, str]]:
        row = self.database.update_action_status(
            action_id,
            "approved",
            "Approved by owner. Execution is still disabled in Level 2-3 MVP.",
        )
        if not row:
            return None
        return {"id": action_id, "status": "approved"}

    def reject(self, action_id: str) -> Optional[Dict[str, str]]:
        row = self.database.update_action_status(action_id, "rejected", "Rejected by owner.")
        if not row:
            return None
        return {"id": action_id, "status": "rejected"}

    def execute_noop(self, action_id: str) -> Optional[Dict[str, str]]:
        row = self.database.update_action_status(
            action_id,
            "executed",
            "No-op execution recorded. Real connector execution remains disabled until signed connector approval.",
        )
        if not row:
            return None
        return {"id": action_id, "status": "executed", "execution": "noop"}

    def rollback(self, action_id: str) -> Optional[Dict[str, str]]:
        row = self.database.update_action_status(
            action_id,
            "rollback",
            "Rollback state recorded. No external side effects existed in MVP runtime.",
        )
        if not row:
            return None
        return {"id": action_id, "status": "rollback"}

    def expire(self, action_id: str) -> Optional[Dict[str, str]]:
        row = self.database.update_action_status(action_id, "expired", "Action expired before approval/execution.")
        if not row:
            return None
        return {"id": action_id, "status": "expired"}

    def _payload(self, mode: str, task: str, output: str) -> Dict[str, str]:
        if mode == "paperclip_task":
            return {"title": task[:120], "description": output}
        if mode == "telegram_draft":
            return {"channel": "manual_target", "message_draft": output}
        if mode == "email_draft":
            return {"to": "manual_recipient", "subject": task[:80], "body_draft": output}
        return {"draft": output}
