from typing import Any, Dict, List

from .pii import PiiDetector, PiiResult


class OutputGuard:
    dangerous_patterns = [
        "ignore previous instructions",
        "bypass policy",
        "send without approval",
        "delete without approval",
        "exfiltrate",
        "disable audit",
        "self-authorize",
    ]

    def __init__(self, pii_detector: PiiDetector):
        self.pii_detector = pii_detector

    def scan(self, output: str, input_pii: PiiResult) -> Dict[str, Any]:
        raw_pii = self.pii_detector.contains_raw_pii(output)
        leaks = {}
        for kind, values in input_pii.findings.items():
            leaked = [value for value in values if value and value in output]
            if leaked:
                leaks[kind] = len(leaked)

        lowered = output.lower()
        dangerous = [pattern for pattern in self.dangerous_patterns if pattern in lowered]
        unauthorized_action = any(term in lowered for term in ["i sent", "i deleted", "i executed", "i paid"])

        violations: List[str] = []
        if any(raw_pii.values()) or leaks:
            violations.append("pii_or_secret_leakage")
        if dangerous:
            violations.append("dangerous_instruction")
        if unauthorized_action:
            violations.append("unauthorized_action_claim")

        return {
            "raw_pii_detected": raw_pii,
            "masked_input_leakage": leaks,
            "dangerous_instructions": dangerous,
            "unauthorized_action_claim": unauthorized_action,
            "policy_violations": violations,
            "hallucination_risk": "medium" if "source" in lowered and "http" not in lowered else "low",
            "passed": not violations,
        }
