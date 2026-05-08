import json
import time
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .database import Database


DomainName = Literal[
    "business",
    "legal",
    "investment",
    "security",
    "software",
    "partnership",
    "personal",
    "recruitment",
    "AI-governance",
]
StrengthName = Literal["weak", "medium", "strong"]
ConfidenceName = Literal["low", "medium", "high"]
ImpactName = Literal["low", "medium", "high", "critical"]
DetectabilityName = Literal["easy", "medium", "hard"]
RiskCategory = Literal["legal", "human", "technical"]
OutcomeName = Literal["yes", "no"]


STRENGTH_WEIGHTS = {"weak": 5.0, "medium": 10.0, "strong": 20.0}
IMPACT_WEIGHTS = {"low": 1.0, "medium": 2.0, "high": 3.0, "critical": 4.0}
DETECTABILITY_WEIGHTS = {"easy": 1.0, "medium": 1.25, "hard": 1.5}


class FormalEvent(BaseModel):
    event_statement: str
    deadline: str
    success_condition: str
    failure_condition: str = ""
    verification_method: str = ""


class ForecastFactor(BaseModel):
    name: str
    direction: Literal["up", "down"]
    strength: StrengthName = "medium"
    confidence: ConfidenceName = "medium"
    weight: Optional[float] = None


class RiskItem(BaseModel):
    name: str
    category: RiskCategory
    probability: float = Field(ge=0, le=100)
    impact: ImpactName = "medium"
    detectability: DetectabilityName = "medium"
    early_warning_signals: List[str] = Field(default_factory=list)
    mitigation_actions: List[str] = Field(default_factory=list)
    residual_risk_after_mitigation: float = Field(default=0, ge=0, le=100)


class ScenarioInput(BaseModel):
    probability: float = Field(ge=0, le=100)
    description: str
    trigger: str = ""
    expected_outcome: str = ""
    main_risk: str = ""
    recommended_action: str = ""


class ForecastCreateRequest(BaseModel):
    raw_question: str = Field(..., min_length=1)
    decision_context: str = ""
    domain: DomainName = "business"
    deadline: str
    success_condition: str
    user_initial_probability: float = Field(ge=1, le=99)
    available_evidence: List[str] = Field(default_factory=list)
    legal_context: str = ""
    human_context: str = ""
    technical_context: str = ""
    created_by: str = "local_user"
    base_rate: Optional[float] = Field(default=None, ge=1, le=99)
    formal_event: Optional[FormalEvent] = None
    factors: List[ForecastFactor] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    scenarios: Optional[List[ScenarioInput]] = None
    decision_after_loss: bool = False


class ForecastOutcomeRequest(BaseModel):
    outcome: OutcomeName
    lessons_learned: str = ""


class ForecastingEngine:
    def __init__(self, database: Database):
        self.database = database

    def create_forecast(self, req: ForecastCreateRequest) -> Dict[str, Any]:
        formal_event = req.formal_event or self._formalize(req)
        factors = [self._factor_payload(item) for item in req.factors]
        factors_up = [item for item in factors if item["direction"] == "up"]
        factors_down = [item for item in factors if item["direction"] == "down"]

        base_rate = req.base_rate if req.base_rate is not None else self._conservative_prior(req.domain)
        adjusted_probability = self._clamp(
            base_rate
            + sum(item["weight"] for item in factors_up)
            - sum(item["weight"] for item in factors_down)
        )

        risks = [self._risk_payload(item) for item in req.risks]
        legal_risks = [item for item in risks if item["category"] == "legal"]
        human_risks = [item for item in risks if item["category"] == "human"]
        technical_risks = [item for item in risks if item["category"] == "technical"]
        risk_penalty = self._risk_penalty(risks)
        probability_after_risk = self._clamp(adjusted_probability - risk_penalty)

        bias = self._bias_check(req, base_rate, risk_penalty)
        bias_correction = bias["correction"]
        final_probability = self._clamp(
            (base_rate * 0.40)
            + (adjusted_probability * 0.30)
            + (probability_after_risk * 0.20)
            + (req.user_initial_probability * 0.10)
            - bias_correction
        )

        confidence_level = self._confidence(req, risks, base_rate)
        scenario_distribution = self._scenarios(req.scenarios, final_probability)
        early_warning_signals = self._signals(risks, positive=False)
        positive_signals = self._signals(risks, positive=True)
        update_triggers = self._update_triggers(formal_event, factors_down, risks)
        mitigation_actions = self._mitigations(risks)
        created_at = int(time.time())
        forecast_id = f"forecast_{uuid4().hex[:12]}"

        record = {
            "forecast_id": forecast_id,
            "created_at": created_at,
            "created_by": req.created_by,
            "domain": req.domain,
            "raw_question": req.raw_question,
            "decision_context": req.decision_context,
            "event_statement": formal_event.event_statement,
            "deadline": formal_event.deadline,
            "success_condition": formal_event.success_condition,
            "failure_condition": formal_event.failure_condition,
            "verification_method": formal_event.verification_method,
            "user_initial_probability": round(req.user_initial_probability, 2),
            "base_rate": round(base_rate, 2),
            "adjusted_probability": round(adjusted_probability, 2),
            "probability_after_risk": round(probability_after_risk, 2),
            "bias_correction": round(bias_correction, 2),
            "final_probability": round(final_probability, 2),
            "confidence_level": confidence_level,
            "factors_up": factors_up,
            "factors_down": factors_down,
            "legal_risks": legal_risks,
            "human_risks": human_risks,
            "technical_risks": technical_risks,
            "risk_summary": self._risk_summary(legal_risks, human_risks, technical_risks),
            "bias_check": bias,
            "scenario_distribution": scenario_distribution,
            "positive_signals": positive_signals,
            "early_warning_signals": early_warning_signals,
            "update_triggers": update_triggers,
            "mitigation_actions": mitigation_actions,
            "review_date": formal_event.deadline,
            "status": "open",
            "outcome": None,
            "brier_score": None,
            "lessons_learned": "",
            "report": self._report(
                formal_event,
                base_rate,
                req.user_initial_probability,
                factors_up,
                factors_down,
                legal_risks,
                human_risks,
                technical_risks,
                bias,
                final_probability,
                confidence_level,
                scenario_distribution,
                early_warning_signals,
                update_triggers,
                mitigation_actions,
                forecast_id,
            ),
        }
        self.database.insert_forecast(record)
        return record

    def list_forecasts(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [self._decode(row) for row in self.database.list_rows("forecast_records", limit)]

    def resolve_forecast(self, forecast_id: str, req: ForecastOutcomeRequest) -> Optional[Dict[str, Any]]:
        row = self.database.get_forecast(forecast_id)
        if not row:
            return None
        record = self._decode(row)
        outcome = 1 if req.outcome == "yes" else 0
        probability = float(record["final_probability"]) / 100.0
        brier_score = (probability - outcome) ** 2
        record.update(
            {
                "status": "resolved",
                "outcome": outcome,
                "brier_score": round(brier_score, 4),
                "lessons_learned": req.lessons_learned,
                "resolved_at": int(time.time()),
            }
        )
        self.database.update_forecast_record(forecast_id, record)
        return record

    def calibration_profile(self) -> Dict[str, Any]:
        records = self.list_forecasts(500)
        resolved = [item for item in records if item.get("status") == "resolved" and item.get("brier_score") is not None]
        by_domain: Dict[str, List[float]] = {}
        overconfidence = 0
        base_rate_neglect = 0
        recurring_biases: Dict[str, int] = {}
        for item in resolved:
            by_domain.setdefault(item["domain"], []).append(float(item["brier_score"]))
            if item.get("outcome") == 0 and item.get("final_probability", 0) >= 70:
                overconfidence += 1
            if abs(float(item.get("user_initial_probability", 0)) - float(item.get("base_rate", 0))) >= 30:
                base_rate_neglect += 1
            for bias in item.get("bias_check", {}).get("detected_biases", []):
                recurring_biases[bias] = recurring_biases.get(bias, 0) + 1

        averages = {domain: round(sum(scores) / len(scores), 4) for domain, scores in by_domain.items()}
        best_domain = min(averages, key=averages.get) if averages else ""
        weakest_domain = max(averages, key=averages.get) if averages else ""
        average_brier = round(sum(float(item["brier_score"]) for item in resolved) / len(resolved), 4) if resolved else 0
        total = len(resolved) or 1
        return {
            "total_forecasts": len(records),
            "resolved_forecasts": len(resolved),
            "average_brier_score": average_brier,
            "business_accuracy": averages.get("business", 0),
            "legal_accuracy": averages.get("legal", 0),
            "human_risk_accuracy": 0,
            "technical_risk_accuracy": averages.get("software", 0) or averages.get("security", 0),
            "overconfidence_index": round(overconfidence / total, 3),
            "base_rate_neglect_index": round(base_rate_neglect / total, 3),
            "loss_domain_index": 0,
            "best_domain": best_domain,
            "weakest_domain": weakest_domain,
            "calibration_by_domain": averages,
            "recurring_biases": sorted(recurring_biases, key=recurring_biases.get, reverse=True),
            "recommendations": self._profile_recommendations(average_brier, overconfidence, base_rate_neglect),
        }

    def _formalize(self, req: ForecastCreateRequest) -> FormalEvent:
        return FormalEvent(
            event_statement=f"By {req.deadline}, {req.raw_question.strip()} will meet: {req.success_condition.strip()}",
            deadline=req.deadline,
            success_condition=req.success_condition,
            failure_condition=f"The success condition is not verified by {req.deadline}.",
            verification_method="Manual review of evidence, logs, documents, or agreed KPI records.",
        )

    def _conservative_prior(self, domain: str) -> float:
        return {
            "investment": 35.0,
            "partnership": 35.0,
            "recruitment": 40.0,
            "software": 45.0,
            "security": 30.0,
            "legal": 40.0,
            "AI-governance": 45.0,
        }.get(domain, 40.0)

    def _factor_payload(self, factor: ForecastFactor) -> Dict[str, Any]:
        return {
            "name": factor.name,
            "direction": factor.direction,
            "strength": factor.strength,
            "confidence": factor.confidence,
            "weight": factor.weight if factor.weight is not None else STRENGTH_WEIGHTS[factor.strength],
        }

    def _risk_payload(self, risk: RiskItem) -> Dict[str, Any]:
        risk_score = (risk.probability / 100.0) * IMPACT_WEIGHTS[risk.impact] * DETECTABILITY_WEIGHTS[risk.detectability]
        return {
            **risk.model_dump(),
            "risk_score": round(risk_score, 3),
        }

    def _risk_penalty(self, risks: List[Dict[str, Any]]) -> float:
        total = sum(item["risk_score"] for item in risks)
        if total >= 3.0:
            return 28.0
        if total >= 2.0:
            return 15.0
        if total >= 1.0:
            return 8.0
        if total > 0:
            return 4.0
        return 0.0

    def _bias_check(self, req: ForecastCreateRequest, base_rate: float, risk_penalty: float) -> Dict[str, Any]:
        detected = []
        reasons_required: List[str] = []
        if req.user_initial_probability > 80:
            detected.append("overconfidence")
            reasons_required = [
                "base rate may be lower than the internal estimate",
                "human or execution risk may dominate the apparent opportunity",
                "missing negative evidence can hide failure modes",
            ]
        if req.decision_after_loss:
            detected.append("loss domain risk")
        if req.available_evidence and not any("risk" in item.lower() or "fail" in item.lower() for item in req.available_evidence):
            detected.append("confirmation bias")
        if abs(req.user_initial_probability - base_rate) >= 25:
            detected.append("base rate neglect")
        if req.user_initial_probability >= 70 and risk_penalty >= 8:
            detected.append("optimism bias")
        correction = 0.0
        if len(detected) >= 3:
            correction = 12.0
        elif len(detected) == 2:
            correction = 7.0
        elif len(detected) == 1:
            correction = 4.0
        return {
            "detected_biases": detected,
            "correction": correction,
            "reasons_why_forecast_may_be_wrong": reasons_required,
        }

    def _confidence(self, req: ForecastCreateRequest, risks: List[Dict[str, Any]], base_rate: float) -> str:
        high_risk = any(item["impact"] in {"high", "critical"} and item["probability"] >= 35 for item in risks)
        if not req.available_evidence or req.base_rate is None or high_risk:
            return "low"
        if len(req.available_evidence) >= 2 and base_rate and not high_risk:
            return "medium"
        return "low"

    def _scenarios(self, scenarios: Optional[List[ScenarioInput]], final_probability: float) -> List[Dict[str, Any]]:
        if scenarios and round(sum(item.probability for item in scenarios), 2) == 100:
            return [item.model_dump() for item in scenarios]
        optimistic = min(35.0, max(15.0, final_probability * 0.45))
        negative = min(45.0, max(20.0, 100.0 - final_probability))
        realistic = max(0.0, 100.0 - optimistic - negative)
        return [
            {
                "name": "optimistic",
                "probability": round(optimistic, 2),
                "description": "The event succeeds with controllable execution risk.",
                "trigger": "early positive signals appear before the review date",
                "expected_outcome": "success condition is met or exceeded",
                "main_risk": "execution discipline weakens after initial momentum",
                "recommended_action": "lock KPIs, owners, and review cadence",
            },
            {
                "name": "realistic",
                "probability": round(realistic, 2),
                "description": "Mixed progress; outcome depends on whether risks are actively managed.",
                "trigger": "some milestones are met, but warning signals remain",
                "expected_outcome": "partial progress or narrow success/failure",
                "main_risk": "human or process uncertainty",
                "recommended_action": "recalculate after update triggers",
            },
            {
                "name": "negative",
                "probability": round(negative, 2),
                "description": "The event fails because key assumptions do not hold.",
                "trigger": "negative warning signals appear or mitigation is ignored",
                "expected_outcome": "failure condition is met",
                "main_risk": "uncontrolled legal, human, or technical exposure",
                "recommended_action": "reduce exposure and prepare fallback",
            },
        ]

    def _signals(self, risks: List[Dict[str, Any]], positive: bool) -> List[str]:
        if positive:
            return [
                "written scope, KPI, or owner is confirmed",
                "evidence quality improves before the review date",
                "high-risk dependencies show reliable behavior",
            ]
        signals = []
        for risk in risks:
            signals.extend(risk.get("early_warning_signals", []))
        return signals[:8] or [
            "no measurable progress before the midpoint",
            "key stakeholder stops responding",
            "new legal, security, or operational constraint appears",
        ]

    def _update_triggers(
        self,
        formal_event: FormalEvent,
        factors_down: List[Dict[str, Any]],
        risks: List[Dict[str, Any]],
    ) -> List[str]:
        triggers = [
            f"if verification evidence for '{formal_event.success_condition}' appears -> increase probability",
            "if deadline, KPI, or owner changes -> recalculate",
        ]
        if factors_down:
            triggers.append(f"if '{factors_down[0]['name']}' worsens -> decrease probability")
        if risks:
            triggers.append(f"if '{risks[0]['name']}' materializes -> decrease probability")
        return triggers

    def _mitigations(self, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        actions = []
        for risk in risks:
            for action in risk.get("mitigation_actions", []):
                actions.append(
                    {
                        "action": action,
                        "target_risk": risk["name"],
                        "expected_risk_reduction": max(0, round(risk["probability"] - risk["residual_risk_after_mitigation"], 2)),
                        "priority": "high" if risk["impact"] in {"high", "critical"} else "medium",
                        "owner": "user",
                        "deadline": "before review date",
                    }
                )
        return actions[:10] or [
            {
                "action": "define measurable KPI, owner, deadline, and evidence source",
                "target_risk": "forecast ambiguity",
                "expected_risk_reduction": 10,
                "priority": "high",
                "owner": "user",
                "deadline": "before execution",
            }
        ]

    def _risk_summary(
        self,
        legal: List[Dict[str, Any]],
        human: List[Dict[str, Any]],
        technical: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "legal_risk_score": round(sum(item["risk_score"] for item in legal), 3),
            "human_risk_score": round(sum(item["risk_score"] for item in human), 3),
            "technical_risk_score": round(sum(item["risk_score"] for item in technical), 3),
            "total_risk_score": round(sum(item["risk_score"] for item in legal + human + technical), 3),
        }

    def _report(
        self,
        formal_event: FormalEvent,
        base_rate: float,
        user_probability: float,
        factors_up: List[Dict[str, Any]],
        factors_down: List[Dict[str, Any]],
        legal_risks: List[Dict[str, Any]],
        human_risks: List[Dict[str, Any]],
        technical_risks: List[Dict[str, Any]],
        bias: Dict[str, Any],
        final_probability: float,
        confidence: str,
        scenarios: List[Dict[str, Any]],
        signals: List[str],
        triggers: List[str],
        mitigations: List[Dict[str, Any]],
        forecast_id: str,
    ) -> str:
        def factor_lines(items: List[Dict[str, Any]]) -> str:
            return "\n".join(f"- {item['name']} / {item['weight']}% / {item['confidence']}" for item in items) or "- none"

        def risk_line(items: List[Dict[str, Any]]) -> str:
            item = items[0] if items else {}
            return "\n".join(
                [
                    f"- probability: {item.get('probability', 0)}%",
                    f"- impact: {item.get('impact', 'low')}",
                    f"- detectability: {item.get('detectability', 'easy')}",
                    f"- key issue: {item.get('name', 'not specified')}",
                    f"- mitigation: {', '.join(item.get('mitigation_actions', [])) or 'define controls'}",
                ]
            )

        scenario_lines = "\n".join(f"- {item.get('name', 'scenario')}: {item['probability']}%" for item in scenarios)
        return "\n".join(
            [
                "FORECAST REPORT",
                "",
                f"1. Formal Event:\n{formal_event.event_statement}",
                f"\n2. Deadline:\n{formal_event.deadline}",
                f"\n3. Success Condition:\n{formal_event.success_condition}",
                f"\n4. Base Rate:\n{round(base_rate, 2)}%",
                f"\n5. User Initial Probability:\n{round(user_probability, 2)}%",
                f"\n6. Factors Increasing Probability:\n{factor_lines(factors_up)}",
                f"\n7. Factors Decreasing Probability:\n{factor_lines(factors_down)}",
                f"\n8. Risk Map:\n\nA. Legal / Objective Risk:\n{risk_line(legal_risks)}\n\nB. Human / Behavioral Risk:\n{risk_line(human_risks)}\n\nC. Technical / Security / Software Risk:\n{risk_line(technical_risks)}",
                f"\n9. Bias Check:\n- detected_biases: {', '.join(bias['detected_biases']) or 'none'}\n- correction: -{bias['correction']}%",
                f"\n10. Final Forecast:\n{round(final_probability, 2)}%",
                f"\n11. Confidence Level:\n{confidence}",
                f"\n12. Scenario Distribution:\n{scenario_lines}",
                f"\n13. Early Warning Signals:\n" + "\n".join(f"- {item}" for item in signals[:5]),
                f"\n14. Update Triggers:\n" + "\n".join(f"- {item}" for item in triggers[:5]),
                f"\n15. Recommended Actions:\n" + "\n".join(f"- {item['action']}" for item in mitigations[:5]),
                f"\n16. Save:\nforecast_id: {forecast_id}\nreview_date: {formal_event.deadline}",
            ]
        )

    def _profile_recommendations(self, average_brier: float, overconfidence: int, base_rate_neglect: int) -> List[str]:
        recommendations = []
        if average_brier >= 0.25:
            recommendations.append("Use wider uncertainty ranges and make more conservative forecasts until calibration improves.")
        if overconfidence:
            recommendations.append("Before assigning 70%+, write three reasons the forecast can fail.")
        if base_rate_neglect:
            recommendations.append("Start every forecast from base rate before adding case-specific evidence.")
        return recommendations or ["Keep resolving forecasts; calibration signal improves with more outcomes."]

    def _decode(self, row: Dict[str, Any]) -> Dict[str, Any]:
        record = json.loads(row["record"])
        record["forecast_id"] = row["id"]
        record["created_at"] = row["created_at"]
        record["status"] = row["status"]
        record["deadline"] = row["deadline"]
        return record

    def _clamp(self, probability: float) -> float:
        return max(1.0, min(99.0, probability))
