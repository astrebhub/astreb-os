import time
import uuid
from dataclasses import dataclass

from . import config
from .database import Database


@dataclass
class BudgetDecision:
    allowed: bool
    reason: str
    alert: str


class BudgetGovernor:
    def __init__(self, database: Database):
        self.database = database

    def evaluate(self, user_id: str, agent_id: str, session_id: str, estimated_cost: float) -> BudgetDecision:
        if config.EMERGENCY_STOP:
            return BudgetDecision(False, "emergency_stop_enabled", "Runtime kill switch is active.")

        start_day = int(time.time()) - 86400
        usage = self.database.daily_usage(user_id, start_day)
        if usage["cost"] + estimated_cost > config.DAILY_COST_LIMIT:
            return BudgetDecision(False, "daily_cost_limit_exceeded", "Daily cost limit reached.")

        start_month = int(time.time()) - 30 * 86400
        monthly_usage = self.database.daily_usage(user_id, start_month)
        if monthly_usage["cost"] + estimated_cost > config.MONTHLY_COST_LIMIT:
            return BudgetDecision(False, "monthly_cost_limit_exceeded", "Monthly cost limit reached.")

        if estimated_cost > config.SESSION_COST_LIMIT:
            return BudgetDecision(False, "session_cost_limit_exceeded", "Session request is too expensive.")

        alert = ""
        if usage["cost"] + estimated_cost > config.DAILY_COST_LIMIT * 0.8:
            alert = "daily_budget_warning_80_percent"
        return BudgetDecision(True, "ok", alert)

    def record(
        self,
        user_id: str,
        agent_id: str,
        session_id: str,
        tokens_estimated: int,
        tokens_used: int,
        cost_estimated: float,
        cost_real: float,
        provider: str,
        model: str,
        status: str,
    ) -> None:
        self.database.insert_budget_event(
            {
                "id": str(uuid.uuid4()),
                "created_at": int(time.time()),
                "user_id": user_id,
                "agent_id": agent_id,
                "session_id": session_id,
                "tokens_estimated": tokens_estimated,
                "tokens_used": tokens_used,
                "cost_estimated": cost_estimated,
                "cost_real": cost_real,
                "provider": provider,
                "model": model,
                "status": status,
            }
        )
