import time
import uuid
from pathlib import Path
from typing import Dict, Optional

from .database import Database
from .policy import PolicyDecision
from .schemas import SubmitRequest


ACTION_INTENTS = {
    "paperclip_task": ("paperclip_plugin", "create_task_draft"),
    "telegram_draft": ("telegram_plugin", "draft_message"),
    "email_draft": ("email_plugin", "draft_email"),
    "calendar_action": ("calendar_plugin", "prepare_calendar_action"),
    "browser_action": ("browser_plugin", "prepare_browser_action"),
    "github_ops": ("github_connector", "prepare_github_action"),
    "computer_ops": ("computer_control_plugin", "prepare_computer_action"),
    "microsoft_ops": ("microsoft_365_connector", "prepare_microsoft_action"),
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
        action = self.database.get_action(action_id)
        if not action:
            return None

        report_plugins = [
            "paperclip_plugin",
            "telegram_plugin",
            "email_plugin",
            "calendar_plugin",
            "browser_plugin",
            "github_connector",
            "computer_control_plugin",
            "microsoft_365_connector",
        ]
        if action["plugin"] in report_plugins:
            return self.execute_local_report(action_id, action)

        self.database.update_action_status(
            action_id,
            "executed",
            "No-op execution recorded. Real connector execution remains disabled until signed connector approval.",
        )
        return {"id": action_id, "status": "executed", "execution": "noop"}

    def execute_local_report(self, action_id: str, action: Dict[str, str]) -> Dict[str, str]:
        reports_dir = Path(__file__).resolve().parents[2] / "runtime" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        prefix_map = {
            "paperclip_plugin": "paperclip-action",
            "telegram_plugin": "telegram-action",
            "email_plugin": "email-action",
            "calendar_plugin": "calendar-action",
            "browser_plugin": "browser-action",
            "computer_control_plugin": "computer-action",
            "microsoft_365_connector": "microsoft-action",
        }
        prefix = prefix_map.get(action.get("plugin"), "github-action")
        report_path = reports_dir / f"{prefix}-{action_id}.md"
        payload = action.get("payload", {})
        report = (
            "# AI Cabinet Executed Agent Action Report\n\n"
            f"- Action ID: {action_id}\n"
            f"- Request ID: {action.get('request_id', '')}\n"
            f"- User ID: {action.get('user_id', '')}\n"
            f"- Plugin: {action.get('plugin', '')}\n"
            f"- Action: {action.get('action', '')}\n"
            f"- Risk level: {action.get('risk_level', '')}\n"
            f"- Policy: {action.get('policy_decision', '')}\n"
            "- Execution type: local sandbox file write\n"
            "- External side effects: none\n"
            "- Connector scope: report artifact only, no external connector call\n\n"
            "## Task\n\n"
            f"{payload.get('task', '')}\n\n"
            "## Agent Operations Brief\n\n"
            f"{payload.get('operations_brief', '')}\n\n"
            "## Governance Result\n\n"
            "The agent action was approved and executed as a local report artifact only. "
            "No shell command, file deletion, application install, email send, Teams post, "
            "calendar event creation, browser form submission, file sharing, GitHub push, merge, "
            "release, repository setting change, or network connector call was performed.\n"
        )
        report_path.write_text(report, encoding="utf-8")
        self.database.update_action_status(
            action_id,
            "executed",
            f"Executed local sandbox report artifact: {report_path}",
        )
        return {
            "id": action_id,
            "status": "executed",
            "execution": "local_report",
            "artifact_path": str(report_path),
        }

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
        if mode == "calendar_action":
            return {"target": "manual_calendar", "task": task, "operations_brief": output}
        if mode == "browser_action":
            return {"target": "manual_browser", "task": task, "operations_brief": output}
        if mode == "github_ops":
            return {"target": "manual_repository", "task": task, "operations_brief": output}
        if mode == "computer_ops":
            return {"target": "local_computer", "task": task, "operations_brief": output}
        if mode == "microsoft_ops":
            return {"target": "microsoft_365_manual_connector", "task": task, "operations_brief": output}
        return {"draft": output}
