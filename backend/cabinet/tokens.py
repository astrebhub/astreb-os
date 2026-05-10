import time
from dataclasses import dataclass

from . import config
from .database import Database


@dataclass
class TokenEstimate:
    tokens_estimated: int
    cost_estimated: float
    blocked: bool
    reason: str


class TokenCostEstimator:
    model_prices = {
        "gpt-4.1-mini": 0.0000004,
        "gemini-2.0-flash": 0.0000002,
        "openrouter/free": 0.0,
        "local-safe-fallback": 0.0,
    }

    def __init__(self, database: Database):
        self.database = database

    def estimate_tokens(self, text: str) -> int:
        return max(1, int(len(text) / 4) + 64)

    def estimate_cost(self, tokens: int, model: str) -> float:
        return round(tokens * self.model_prices.get(model, 0.0000005), 6)

    def evaluate(self, user_id: str, text: str, model_hint: str) -> TokenEstimate:
        tokens = self.estimate_tokens(text)
        cost = self.estimate_cost(tokens, model_hint)

        if tokens > config.TOKEN_LIMIT_PER_REQUEST:
            return TokenEstimate(tokens, cost, True, "token_limit_per_request_exceeded")

        start_of_day = int(time.time()) - 86400
        usage = self.database.daily_usage(user_id, start_of_day)
        if usage["tokens"] + tokens > config.DAILY_TOKEN_LIMIT_PER_USER:
            return TokenEstimate(tokens, cost, True, "daily_token_limit_exceeded")
        if usage["cost"] + cost > config.DAILY_COST_LIMIT:
            return TokenEstimate(tokens, cost, True, "daily_cost_limit_exceeded")

        return TokenEstimate(tokens, cost, False, "ok")
