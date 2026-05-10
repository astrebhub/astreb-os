from typing import Any, Dict

from .database import Database


class AgentRegistry:
    def __init__(self, database: Database):
        self.database = database

    def ensure_defaults(self) -> list[str]:
        return [
            self.ensure_default(),
            self.ensure_cabinet_operator(),
            self.ensure_cabinet_guide(),
            self.ensure_governance_architect(),
            self.ensure_github_manager(),
            self.ensure_computer_control_agent(),
            self.ensure_microsoft_365_agent(),
            self.ensure_editorial_agent(),
            self.ensure_research_agent(),
            self.ensure_risk_sentinel(),
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

    def ensure_cabinet_operator(self) -> str:
        return self.register(
            {
                "id": "cabinet_operator",
                "role": "runtime_operator",
                "instructions": (
                    "Operate AI Cabinet as a controlled runtime. Prefer short status-oriented answers, "
                    "diagnose runtime health, explain configuration, and propose safe operational steps. "
                    "Never execute external actions or change durable settings without approval."
                ),
                "permissions": ["analyze_runtime", "draft_operations_plan", "read_runtime_status"],
                "budget": {"daily_cost": 1.0, "max_cost_per_request": 0.1},
                "tools": ["model_router", "audit_log", "observability"],
                "memory_scope": "operational",
                "risk_level": "medium",
                "status": "active",
            }
        )

    def ensure_cabinet_guide(self) -> str:
        return self.register(
            {
                "id": "cabinet_guide_agent",
                "role": "runtime_navigation_and_configuration_guide",
                "instructions": (
                    "Live inside AI Cabinet as the navigation guide. Explain the runtime, buttons, "
                    "pipeline, models, policies, ASTI connectors, agents, approvals, audit, memory, "
                    "and safe test scenarios. Help the owner choose settings and propose governed "
                    "actions without bypassing policy or executing external side effects."
                ),
                "permissions": [
                    "explain_runtime",
                    "recommend_ui_panel",
                    "draft_safe_test",
                    "explain_policy",
                    "explain_connectors",
                    "explain_model_routing",
                ],
                "budget": {"daily_cost": 0.5, "max_cost_per_request": 0.02},
                "tools": ["runtime_status", "connector_registry", "policy_config", "local_runtime_status"],
                "memory_scope": "operational",
                "risk_level": "low",
                "status": "active",
            }
        )

    def ensure_computer_control_agent(self) -> str:
        return self.register(
            {
                "id": "computer_control_agent",
                "role": "local_computer_control_planner",
                "instructions": (
                    "Prepare safe local computer operations behind AI Cabinet governance. "
                    "You may diagnose, draft command plans, explain expected effects, and create approved "
                    "local report artifacts. Never run shell commands, delete files, install software, stop "
                    "services, access credentials, change startup items, modify registry, or perform network "
                    "actions unless a signed executor and explicit owner approval are present."
                ),
                "permissions": [
                    "diagnose_local_runtime",
                    "draft_command_plan",
                    "prepare_computer_action",
                    "write_local_report_artifact",
                    "recommend_manual_steps",
                ],
                "budget": {"daily_cost": 1.0, "max_cost_per_request": 0.1},
                "tools": ["policy_engine", "action_queue", "approval_center", "audit_log", "local_report_executor"],
                "memory_scope": "operational",
                "risk_level": "high",
                "status": "active",
            }
        )

    def ensure_microsoft_365_agent(self) -> str:
        return self.register(
            {
                "id": "microsoft_365_agent",
                "role": "microsoft_365_control_agent",
                "instructions": (
                    "Prepare governed Microsoft 365 work behind AI Cabinet. You may summarize, draft, "
                    "plan Outlook email actions, calendar actions, Teams replies, OneDrive/SharePoint file "
                    "workflows, and Planner tasks. Never send email, post Teams messages, create meetings, "
                    "share files, change permissions, delete files, access credentials, or call Microsoft Graph "
                    "unless a signed connector and explicit approval record are present."
                ),
                "permissions": [
                    "draft_outlook_email",
                    "draft_calendar_event",
                    "draft_teams_reply",
                    "draft_planner_task",
                    "prepare_onedrive_file_workflow",
                    "prepare_sharepoint_workflow",
                    "write_local_report_artifact",
                ],
                "budget": {"daily_cost": 1.5, "max_cost_per_request": 0.15},
                "tools": ["policy_engine", "action_queue", "approval_center", "audit_log", "local_report_executor"],
                "memory_scope": "operational",
                "risk_level": "high",
                "status": "active",
            }
        )

    def ensure_governance_architect(self) -> str:
        return self.register(
            {
                "id": "governance_architect",
                "role": "ai_governance_architect",
                "instructions": (
                    "Design governed AI workflows, policy gates, approval paths, audit controls, "
                    "risk scoring, and enterprise-grade operating models. Be strict about control before autonomy."
                ),
                "permissions": ["draft_policy", "analyze_governance", "propose_architecture"],
                "budget": {"daily_cost": 2.0, "max_cost_per_request": 0.2},
                "tools": ["policy_engine", "audit_log", "memory_proposals", "evidence_layer"],
                "memory_scope": "project",
                "risk_level": "high",
                "status": "active",
            }
        )

    def ensure_editorial_agent(self) -> str:
        return self.register(
            {
                "id": "editorial_agent",
                "role": "editorial_quality_agent",
                "instructions": (
                    "Improve editorial clarity, structure, tone, and source discipline for Jazekker.nl. "
                    "Separate fact, interpretation, and speculation. Never invent sources or publish directly."
                ),
                "permissions": ["draft_article", "edit_content", "critique_claims", "propose_headlines"],
                "budget": {"daily_cost": 1.0, "max_cost_per_request": 0.1},
                "tools": ["evidence_layer", "memory_read", "draft_create"],
                "memory_scope": "project",
                "risk_level": "medium",
                "status": "active",
            }
        )

    def ensure_research_agent(self) -> str:
        return self.register(
            {
                "id": "research_agent",
                "role": "evidence_research_agent",
                "instructions": (
                    "Build evidence packs, flag unsupported claims, estimate source confidence, "
                    "and identify what must be verified before publication or strategic use."
                ),
                "permissions": ["structure_sources", "draft_research_notes", "flag_uncertainty"],
                "budget": {"daily_cost": 1.0, "max_cost_per_request": 0.1},
                "tools": ["evidence_layer", "audit_log"],
                "memory_scope": "project",
                "risk_level": "medium",
                "status": "active",
            }
        )

    def ensure_risk_sentinel(self) -> str:
        return self.register(
            {
                "id": "risk_sentinel",
                "role": "risk_and_policy_sentinel",
                "instructions": (
                    "Detect privacy, legal, reputational, operational, and quality risks. "
                    "Recommend blocks, approvals, rollback, or safer rewrites when needed."
                ),
                "permissions": ["score_risk", "flag_pii", "recommend_approval", "draft_safe_rewrite"],
                "budget": {"daily_cost": 1.5, "max_cost_per_request": 0.15},
                "tools": ["policy_engine", "output_guard", "audit_log", "approval_center"],
                "memory_scope": "audit",
                "risk_level": "high",
                "status": "active",
            }
        )

    def register(self, record: Dict[str, Any]) -> str:
        return self.database.upsert_agent(record)
