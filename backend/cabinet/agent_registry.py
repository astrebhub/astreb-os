from typing import Any, Dict

from .database import Database


class AgentRegistry:
    def __init__(self, database: Database):
        self.database = database

    def ensure_defaults(self) -> list[str]:
        return [
            self.ensure_default(),
            self.ensure_github_manager(),
        ]

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

    def ensure_github_manager(self) -> str:
        return self.register(
            {
                "id": "github_manager_agent",
                "role": "github_operations_manager",
                "instructions": (
                    "Coordinate GitHub repository work behind AI Cabinet governance. "
                    "Prepare issues, branches, pull request plans, review summaries, release notes, "
                    "CI diagnostics, and repository maintenance proposals. Never push, merge, delete, "
                    "change repository settings, publish releases, or alter durable policy without an "
                    "approved action record."
                ),
                "permissions": [
                    "analyze_repository",
                    "draft_issue",
                    "draft_pull_request",
                    "draft_release_notes",
                    "review_ci_status",
                    "propose_branch_plan",
                    "propose_repository_policy",
                    "queue_github_action_for_approval",
                ],
                "budget": {"daily_cost": 2.0, "max_cost_per_request": 0.15},
                "tools": [
                    "model_router",
                    "action_queue",
                    "approval_center",
                    "audit_log",
                    "evidence_layer",
                    "github_connector_after_approval",
                ],
                "memory_scope": "operational",
                "risk_level": "medium",
                "status": "active",
            }
        )

    def register(self, record: Dict[str, Any]) -> str:
        return self.database.upsert_agent(record)
