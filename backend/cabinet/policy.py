from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class PolicyDecision:
    name: str
    mask: bool
    allow_cloud: bool
    require_approval: bool
    local_only: bool
    blocked: bool
    reason: str


class PolicyEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def evaluate(
        self,
        classification: Dict[str, str],
        has_pii: bool,
        access_level: int,
        local_only: bool,
    ) -> PolicyDecision:
        rules = self.config.get("rules", {})
        data_class = classification["data_class"]
        risk_level = classification["risk_level"]
        rule = rules.get(data_class, rules.get("default", {}))

        mask = bool(rule.get("mask", has_pii))
        allow_cloud = bool(rule.get("allow_cloud", True))
        require_approval = bool(rule.get("require_approval", risk_level != "low"))
        forced_local_only = bool(rule.get("local_only", False)) or local_only

        blocked = access_level < 2 and classification["task_type"].endswith("_draft")
        reason = "access_level_too_low" if blocked else rule.get("name", f"{data_class}_policy")

        if access_level <= 3 and classification["task_type"].endswith("_draft"):
            require_approval = True

        return PolicyDecision(
            name=reason,
            mask=mask,
            allow_cloud=allow_cloud and not forced_local_only,
            require_approval=require_approval,
            local_only=forced_local_only,
            blocked=blocked,
            reason=reason,
        )
