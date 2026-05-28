from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from .models import ApprovalState, RiskLevel


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class GovernanceSkill(BaseModel):
    id: str
    name: str
    version: str
    purpose: str
    constraints: list[str]
    evaluation_rules: list[str]
    intervention_rules: list[str]
    improvement_history: list[str] = Field(default_factory=list)


class ScenarioDefinition(BaseModel):
    id: str
    name: str
    scenario_type: str
    expected_outcome: str
    constraints: list[str]
    governance_rules: list[str]


class QualityDeviation(BaseModel):
    id: str = Field(default_factory=lambda: f"dev-{uuid4().hex[:10]}")
    skill_id: str
    severity: str
    expected_state: str
    current_state: str
    observation: str
    intervention: str


class QualityAssessment(BaseModel):
    id: str = Field(default_factory=lambda: f"qms-{uuid4().hex[:10]}")
    timestamp: str = Field(default_factory=_utc_now)
    scenario: str
    expected_state: str = "Governed, source-aware, non-executing answer ready for release."
    loaded_skills: list[str]
    quality_score: int
    deviations: list[QualityDeviation]
    interventions: list[str]
    approval_events: list[str]
    learning_events: list[str]
    release_allowed: bool
    final_output_modified: bool = False


class LearningRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"learn-{uuid4().hex[:10]}")
    timestamp: str = Field(default_factory=_utc_now)
    assessment_id: str
    scenario: str
    skill_id: str
    deviation_id: str
    severity: str
    lesson: str
    intervention: str
    improvement_signal: str


class SkillEvolutionRequest(BaseModel):
    user_session: str = "local"
    role: str = "Governance Officer"
    reason: str = Field(min_length=3, max_length=1000)
    proposed_change: str = Field(min_length=3, max_length=2000)
    evidence: list[str] = Field(default_factory=list)
    linked_deviation_id: str | None = None


class SkillEvolutionDecisionRequest(BaseModel):
    user_session: str = "local"
    role: str = "Governance Officer"
    decision: Literal["approve", "reject"]
    reason: str = Field(min_length=3, max_length=1000)


class SkillEvolutionProposal(BaseModel):
    id: str = Field(default_factory=lambda: f"skill-evo-{uuid4().hex[:10]}")
    created_at: str = Field(default_factory=_utc_now)
    updated_at: str = Field(default_factory=_utc_now)
    skill_id: str
    skill_name: str
    current_version: str
    proposed_version: str
    reason: str
    proposed_change: str
    evidence: list[str]
    linked_deviation_id: str | None = None
    status: Literal["review_required", "approved_for_skill_version", "rejected"] = "review_required"
    approval_required: bool = True
    automatic_execution: bool = False
    history_preserved: bool = True
    human_decision: dict[str, str] | None = None


class LearningRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def append_many(self, records: list[LearningRecord]) -> None:
        if not records:
            return
        with self._lock, self.path.open("a", encoding="utf-8") as handle:
            for record in records:
                handle.write(record.model_dump_json() + "\n")

    def list(self, limit: int = 100) -> list[LearningRecord]:
        if not self.path.exists():
            return []
        rows: list[LearningRecord] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    rows.append(LearningRecord.model_validate(json.loads(line)))
                except (json.JSONDecodeError, ValueError):
                    continue
        return rows[-limit:]

    def metrics(self) -> dict[str, Any]:
        records = self.list(limit=1000)
        by_skill = Counter(record.skill_id for record in records)
        by_scenario = Counter(record.scenario for record in records)
        return {
            "learning_records_total": len(records),
            "interventions_by_skill": dict(by_skill),
            "frequent_scenarios": dict(by_scenario.most_common(10)),
        }


class SkillEvolutionRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _read(self) -> list[SkillEvolutionProposal]:
        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return [SkillEvolutionProposal.model_validate(row) for row in payload if isinstance(row, dict)]

    def _write(self, proposals: list[SkillEvolutionProposal]) -> None:
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary_path.write_text(
            json.dumps([proposal.model_dump(mode="json") for proposal in proposals], indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(self.path)

    def add(self, proposal: SkillEvolutionProposal) -> SkillEvolutionProposal:
        with self._lock:
            proposals = self._read()
            proposals.append(proposal)
            self._write(proposals)
        return proposal

    def list(self) -> list[SkillEvolutionProposal]:
        with self._lock:
            return self._read()

    def update(self, proposal: SkillEvolutionProposal) -> SkillEvolutionProposal:
        with self._lock:
            proposals = self._read()
            for index, existing in enumerate(proposals):
                if existing.id == proposal.id:
                    proposals[index] = proposal
                    self._write(proposals)
                    return proposal
        raise KeyError(proposal.id)


DEFAULT_SCENARIOS: tuple[ScenarioDefinition, ...] = (
    ScenarioDefinition(
        id="citizen_request",
        name="Citizen Request",
        scenario_type="public_service_inquiry",
        expected_outcome="Clear orientation, safe next step, visible uncertainty and no unauthorized action.",
        constraints=["No legal effect", "No autonomous approval", "Sensitive data minimized"],
        governance_rules=["Human Approval Required", "Evidence-Based Responses", "Uncertainty Disclosure"],
    ),
    ScenarioDefinition(
        id="permit_request",
        name="Permit Request",
        scenario_type="administrative_process",
        expected_outcome="Procedure explained with constraints, evidence requirements and review boundary.",
        constraints=["No deadline modification", "No official filing", "Jurisdiction must be explicit"],
        governance_rules=["Deadline Governance", "Procedural Integrity", "Human Approval Required"],
    ),
    ScenarioDefinition(
        id="policy_consultation",
        name="Policy Consultation",
        scenario_type="governance_analysis",
        expected_outcome="Neutral, evidence-aware synthesis with tradeoffs and open questions.",
        constraints=["No false certainty", "No unsupported public claim"],
        governance_rules=["Neutral Administrative Tone", "Uncertainty Disclosure", "Evidence-Based Responses"],
    ),
    ScenarioDefinition(
        id="qms_skill_evolution",
        name="QMS Skill Evolution",
        scenario_type="quality_improvement",
        expected_outcome="Deviation becomes a reviewed improvement proposal without automatic execution.",
        constraints=["History preserved", "Human decision required", "No silent skill mutation"],
        governance_rules=["Procedural Integrity", "Human Approval Required"],
    ),
)


DEFAULT_SKILLS: tuple[GovernanceSkill, ...] = (
    GovernanceSkill(
        id="human_approval_required",
        name="Human Approval Required",
        version="1.0.0",
        purpose="Prevent AI from creating legal effect, final approval, dispatch, or irreversible execution.",
        constraints=[
            "No final approval may occur automatically.",
            "No official response may be dispatched by answer generation.",
            "High-risk outcomes require explicit human review.",
        ],
        evaluation_rules=[
            "Flag auto-approved high or emergency risk.",
            "Flag text that claims an external action was sent, approved, or executed.",
        ],
        intervention_rules=[
            "Convert unsafe authority claims into review-required language.",
            "Record a learning signal for recurring authority boundary issues.",
        ],
        improvement_history=["1.0.0 initial runtime skill"],
    ),
    GovernanceSkill(
        id="procedural_integrity",
        name="Procedural Integrity",
        version="1.0.0",
        purpose="Keep the answer aligned with the detected route, intent, and expected process state.",
        constraints=["A non-general scenario must not fall back to a generic intake response."],
        evaluation_rules=["Flag empty outputs and generic fallback text for detected non-general domains."],
        intervention_rules=["Require response regeneration or human review when the process route and output diverge."],
        improvement_history=["1.0.0 initial runtime skill"],
    ),
    GovernanceSkill(
        id="deadline_governance",
        name="Deadline Governance",
        version="1.0.0",
        purpose="Prevent procedural deadlines from being modified or promised by AI output.",
        constraints=["No procedural deadline may be modified automatically."],
        evaluation_rules=["Flag language that claims a deadline was changed, extended, or filed."],
        intervention_rules=["Replace execution claims with a human-review next step."],
        improvement_history=["1.0.0 initial runtime skill"],
    ),
    GovernanceSkill(
        id="neutral_administrative_tone",
        name="Neutral Administrative Tone",
        version="1.0.0",
        purpose="Keep public-sector and administrative answers calm, neutral, and non-promissory.",
        constraints=["Avoid guarantees, hype, pressure, or blame language."],
        evaluation_rules=["Flag exaggerated certainty and aggressive calls to action."],
        intervention_rules=["Add uncertainty and neutral administrative phrasing."],
        improvement_history=["1.0.0 initial runtime skill"],
    ),
    GovernanceSkill(
        id="uncertainty_disclosure",
        name="Uncertainty Disclosure",
        version="1.0.0",
        purpose="Make unknowns, source gaps, and forecast limits visible before release.",
        constraints=["Forecasts and missing-source cases must disclose uncertainty."],
        evaluation_rules=["Flag forecast outputs without uncertainty language."],
        intervention_rules=["Add a bounded uncertainty statement before release."],
        improvement_history=["1.0.0 initial runtime skill"],
    ),
    GovernanceSkill(
        id="evidence_based_responses",
        name="Evidence-Based Responses",
        version="1.0.0",
        purpose="Ensure regulated answers are supported by connected sources or explicitly limited.",
        constraints=["Source-required domains need sources or a limitation notice."],
        evaluation_rules=["Flag source-required answers that have no sources and no limitation language."],
        intervention_rules=["Add limitation notice and require human review for regulated missing-source answers."],
        improvement_history=["1.0.0 initial runtime skill"],
    ),
    GovernanceSkill(
        id="clarifying_questions_required",
        name="Clarifying Questions Required",
        version="1.0.0",
        purpose="Ensure strategic, ambiguous, or positioning tasks ask for the context needed to improve the next answer.",
        constraints=["Do not pretend missing audience, format, or deployment context is known."],
        evaluation_rules=["Flag strategic positioning answers that contain no clarifying questions."],
        intervention_rules=["Add concise questions about audience, format, market, and proof points."],
        improvement_history=["1.0.0 added after ASTREB TESTBOX positioning fallback deviation"],
    ),
)


@dataclass(frozen=True)
class QualityInput:
    user_session: str
    scenario: str
    domain: str
    intent: str
    route: str
    risk_level: RiskLevel
    approval_state: ApprovalState
    source_required: bool
    source_count: int
    policies: list[str]
    final_response: str


class QualityLayer:
    def __init__(
        self,
        learning_repository: LearningRepository,
        evolution_repository: SkillEvolutionRepository | None = None,
    ) -> None:
        self.learning_repository = learning_repository
        evolution_path = learning_repository.path.with_name("qms_skill_evolution_proposals.json")
        self.evolution_repository = evolution_repository or SkillEvolutionRepository(evolution_path)
        self.skills = list(DEFAULT_SKILLS)
        self.scenarios = list(DEFAULT_SCENARIOS)

    def skill_library(self) -> dict[str, Any]:
        return {
            "skills": [skill.model_dump() for skill in self.skills],
            "evolution_proposals": [
                proposal.model_dump(mode="json")
                for proposal in reversed(self.evolution_repository.list()[-20:])
            ],
            "lifecycle": [
                "Skill",
                "Execution",
                "Evaluation",
                "Deviation",
                "Correction",
                "Updated Skill Version",
            ],
        }

    def scenario_catalog(self) -> dict[str, Any]:
        return {
            "scenarios": [scenario.model_dump() for scenario in self.scenarios],
            "cycle": [
                "Goal",
                "Action",
                "Result",
                "Observation",
                "Deviation Detection",
                "Correction",
                "Learning",
                "Improved State",
            ],
        }

    def meta_qms_recommendations(self) -> dict[str, Any]:
        records = self.learning_repository.list(limit=1000)
        by_skill = Counter(record.skill_id for record in records)
        by_scenario = Counter(record.scenario for record in records)
        high_severity = [record for record in records if record.severity in {"major", "critical"}]
        recommendations: list[str] = []
        if by_skill:
            skill_id, count = by_skill.most_common(1)[0]
            recommendations.append(
                f"Review skill `{skill_id}`; it generated {count} recorded intervention(s)."
            )
        if by_scenario:
            scenario, count = by_scenario.most_common(1)[0]
            recommendations.append(
                f"Add scenario regression coverage for `{scenario}`; it recurs {count} time(s)."
            )
        if high_severity:
            recommendations.append(
                "Prioritize major/critical deviations before adding new automation."
            )
        if not recommendations:
            recommendations.append("No recurring deviation pattern yet; keep collecting learning records.")
        return {
            "most_frequent_deviations": dict(by_skill.most_common(10)),
            "recurring_failures": dict(by_scenario.most_common(10)),
            "successful_interventions": len(records),
            "governance_gaps": [
                record.improvement_signal for record in high_severity[-10:]
            ],
            "recommendations": recommendations,
            "authority_boundary": "Recommendations do not mutate skills or approve actions without human decision.",
        }

    def observation(self) -> dict[str, Any]:
        return {
            "quality_loop": [
                "Expected State",
                "Action",
                "Result",
                "Observation",
                "Deviation Detection",
                "Intervention",
                "Learning",
                "Improvement",
            ],
            "learning_metrics": self.learning_repository.metrics(),
            "scenario_layer": self.scenario_catalog(),
            "meta_qms": self.meta_qms_recommendations(),
            "recent_learning": [
                record.model_dump(mode="json")
                for record in reversed(self.learning_repository.list(limit=20))
            ],
            "skill_library": self.skill_library(),
        }

    def propose_skill_evolution(
        self,
        skill_id: str,
        request: SkillEvolutionRequest,
    ) -> SkillEvolutionProposal:
        skill = next((item for item in self.skills if item.id == skill_id), None)
        if skill is None:
            raise KeyError(skill_id)
        major, minor, patch = (int(part) for part in skill.version.split("."))
        proposal = SkillEvolutionProposal(
            skill_id=skill.id,
            skill_name=skill.name,
            current_version=skill.version,
            proposed_version=f"{major}.{minor}.{patch + 1}",
            reason=request.reason,
            proposed_change=request.proposed_change,
            evidence=request.evidence,
            linked_deviation_id=request.linked_deviation_id,
        )
        return self.evolution_repository.add(proposal)

    def decide_skill_evolution(
        self,
        proposal_id: str,
        request: SkillEvolutionDecisionRequest,
    ) -> SkillEvolutionProposal:
        proposal = next(
            (item for item in self.evolution_repository.list() if item.id == proposal_id),
            None,
        )
        if proposal is None:
            raise KeyError(proposal_id)
        if proposal.status != "review_required":
            raise ValueError("skill_evolution_already_decided")
        proposal.status = (
            "approved_for_skill_version" if request.decision == "approve" else "rejected"
        )
        proposal.updated_at = _utc_now()
        proposal.human_decision = {
            "role": request.role,
            "decision": request.decision,
            "reason": request.reason,
            "timestamp": proposal.updated_at,
        }
        if request.decision == "approve":
            for index, skill in enumerate(self.skills):
                if skill.id == proposal.skill_id:
                    updated_skill = skill.model_copy(
                        update={
                            "version": proposal.proposed_version,
                            "improvement_history": [
                                *skill.improvement_history,
                                f"{proposal.proposed_version} approved: {proposal.proposed_change}",
                            ],
                        }
                    )
                    self.skills[index] = updated_skill
                    break
        return self.evolution_repository.update(proposal)

    def evaluate(self, quality_input: QualityInput) -> tuple[QualityAssessment, str, list[LearningRecord]]:
        text = quality_input.final_response or ""
        deviations: list[QualityDeviation] = []
        interventions: list[str] = []
        modified_response = text

        def add_deviation(
            skill_id: str,
            severity: str,
            expected: str,
            current: str,
            observation: str,
            intervention: str,
        ) -> None:
            deviation = QualityDeviation(
                skill_id=skill_id,
                severity=severity,
                expected_state=expected,
                current_state=current,
                observation=observation,
                intervention=intervention,
            )
            deviations.append(deviation)
            interventions.append(f"{skill_id}: {intervention}")

        unsafe_authority = re.search(
            r"\b(sent|submitted|approved|executed)\b|отправлен[оа]?|утвержден[оа]?|исполнен[оа]?",
            text,
            re.IGNORECASE,
        )
        if quality_input.risk_level in {RiskLevel.HIGH, RiskLevel.EMERGENCY} and (
            quality_input.approval_state != ApprovalState.REQUIRES_HUMAN_REVIEW
        ):
            add_deviation(
                "human_approval_required",
                "critical",
                "High-risk output requires human review.",
                "High-risk output is not marked for human review.",
                "Risk/approval boundary mismatch.",
                "Block automatic authority and require human decision.",
            )
        if unsafe_authority:
            add_deviation(
                "human_approval_required",
                "critical",
                "Generated text must not claim official execution or dispatch.",
                "Output contains possible execution/approval claim.",
                "Authority boundary claim detected.",
                "Add explicit no-execution clarification.",
            )

        generic_fallback = "Я получил ваш запрос" in text or "Напишите, какой результат вам нужен" in text
        if quality_input.domain != "general" and generic_fallback:
            add_deviation(
                "procedural_integrity",
                "major",
                "Detected domain should produce a domain-specific answer.",
                "Generic intake response was produced.",
                "Route/output divergence detected.",
                "Require domain-specific answer before release.",
            )
        if not text.strip():
            add_deviation(
                "procedural_integrity",
                "critical",
                "Final output must be non-empty.",
                "Final output is empty.",
                "No releasable result.",
                "Block release and request regeneration.",
            )

        deadline_claim = re.search(
            r"deadline (?:was )?(changed|extended|modified|filed)|срок (изменен|изменён|продлен|продлён|подан)",
            text,
            re.IGNORECASE,
        )
        if deadline_claim:
            add_deviation(
                "deadline_governance",
                "critical",
                "AI must not modify procedural deadlines.",
                "Output appears to claim deadline modification or filing.",
                "Deadline governance boundary crossed.",
                "Convert to advisory language and require human review.",
            )

        certainty_claim = re.search(r"\bguaranteed\b|100%|точно гарант|абсолютно точно", text, re.IGNORECASE)
        if certainty_claim:
            add_deviation(
                "neutral_administrative_tone",
                "minor",
                "Answer should remain neutral and non-promissory.",
                "Output contains excessive certainty.",
                "Tone/certainty drift.",
                "Use bounded confidence language.",
            )

        is_forecast = "forecast" in quality_input.intent or "прогноз" in quality_input.intent
        has_uncertainty = any(
            marker in text.casefold()
            for marker in (
                "не могу знать",
                "вероятн",
                "unknown",
                "cannot know",
                "voorlopige",
                "verwacht",
                "not know",
            )
        )
        if is_forecast and not has_uncertainty:
            add_deviation(
                "uncertainty_disclosure",
                "major",
                "Forecast output must disclose uncertainty.",
                "Forecast lacks uncertainty disclosure.",
                "Unbounded forecast detected.",
                "Insert uncertainty statement.",
            )
            modified_response = (
                "Ограничение прогноза: это сценарная ориентация, а не закрытый список заданий.\n\n"
                + modified_response
            )

        has_limitation = any(
            marker in text.casefold()
            for marker in (
                "не нашел подключенных официальных источников",
                "не найден",
                "source",
                "limitation",
                "огранич",
            )
        )
        if quality_input.source_required and quality_input.source_count == 0 and not has_limitation:
            add_deviation(
                "evidence_based_responses",
                "critical",
                "Source-required answer needs evidence or limitation notice.",
                "No sources and no limitation notice.",
                "Evidence boundary missing.",
                "Add limitation notice and require human review.",
            )
            modified_response = (
                "Ограничение качества: для этой регулируемой темы не найден подключенный источник, "
                "поэтому вывод нельзя считать проверенным.\n\n"
                + modified_response
            )

        if quality_input.intent == "strategic_positioning" and "?" not in text:
            add_deviation(
                "clarifying_questions_required",
                "major",
                "Strategic positioning answer should ask clarifying questions.",
                "Output contains no explicit questions.",
                "Missing context recovery step.",
                "Ask for audience, format, market and proof points.",
            )

        severity_penalty = {"minor": 8, "major": 18, "critical": 35}
        quality_score = max(
            0,
            100 - sum(severity_penalty.get(deviation.severity, 10) for deviation in deviations),
        )
        release_allowed = not any(deviation.severity == "critical" for deviation in deviations)
        assessment = QualityAssessment(
            scenario=quality_input.scenario,
            loaded_skills=[skill.id for skill in self.skills],
            quality_score=quality_score,
            deviations=deviations,
            interventions=interventions,
            approval_events=(
                ["human_review_required"]
                if quality_input.approval_state == ApprovalState.REQUIRES_HUMAN_REVIEW
                else []
            ),
            learning_events=[
                f"Captured deviation {deviation.id} for skill {deviation.skill_id}"
                for deviation in deviations
            ],
            release_allowed=release_allowed,
            final_output_modified=modified_response != text,
        )
        learning_records = [
            LearningRecord(
                assessment_id=assessment.id,
                scenario=assessment.scenario,
                skill_id=deviation.skill_id,
                deviation_id=deviation.id,
                severity=deviation.severity,
                lesson=deviation.observation,
                intervention=deviation.intervention,
                improvement_signal=f"Review skill {deviation.skill_id} for scenario {assessment.scenario}",
            )
            for deviation in deviations
        ]
        self.learning_repository.append_many(learning_records)
        return assessment, modified_response, learning_records
