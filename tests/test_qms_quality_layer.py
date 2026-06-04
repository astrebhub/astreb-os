from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "backend"))

from asti.executors import NoOpExecutor  # noqa: E402
from asti.models import ExecutorType  # noqa: E402
from asti.service import AstiService  # noqa: E402
from asti.store import ActionQueue, AstiAuditLog  # noqa: E402
from testbox_runtime.api import create_testbox_router  # noqa: E402
from testbox_runtime.models import ApprovalState, RiskLevel  # noqa: E402
from testbox_runtime.quality_layer import LearningRepository, QualityInput, QualityLayer  # noqa: E402


ADMIN_HEADERS = {"X-AI-Cabinet-Admin-Token": "qms-runtime-admin"}


def qms_client(tmp_path: Path, monkeypatch) -> TestClient:
    monkeypatch.setenv("ADMIN_API_TOKEN", "qms-runtime-admin")
    service = AstiService(
        ActionQueue(tmp_path / "global-asti-actions.json"),
        AstiAuditLog(tmp_path / "global-asti-audit.jsonl"),
        executors={ExecutorType.NO_OP: NoOpExecutor()},
    )
    app = FastAPI()
    app.include_router(create_testbox_router(tmp_path, service))
    return TestClient(app, headers=ADMIN_HEADERS)


def test_runtime_message_runs_quality_layer_before_final_release(tmp_path, monkeypatch):
    client = qms_client(tmp_path, monkeypatch)

    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "ты можешь спрогнозировать какие будут задания, задачи в этом выпуске хакатона",
            "user_session": "qms-forecast",
            "role": "Operator",
            "language": "ru",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assessment = payload["quality_assessment"]
    actions = [event["action"] for event in payload["events"]]
    assert assessment["scenario"] == "event_collaboration:forecast_event_challenges"
    assert assessment["quality_score"] >= 90
    assert assessment["release_allowed"] is True
    assert "human_approval_required" in assessment["loaded_skills"]
    assert "uncertainty_disclosure" in assessment["loaded_skills"]
    assert actions.index("QUALITY_EVALUATED") < actions.index("ANSWER_GENERATED")
    assert "QUALITY_INTERVENTION_APPLIED" not in actions


def test_qms_skill_library_and_learning_observation_are_visible(tmp_path, monkeypatch):
    client = qms_client(tmp_path, monkeypatch)

    skills = client.get("/api/testbox/runtime/qms/skills")
    learning = client.get("/api/testbox/runtime/qms/learning")
    scenarios = client.get("/api/testbox/runtime/qms/scenarios")
    meta = client.get("/api/testbox/runtime/qms/meta")

    assert skills.status_code == 200
    assert learning.status_code == 200
    assert scenarios.status_code == 200
    assert meta.status_code == 200
    skill_ids = {skill["id"] for skill in skills.json()["skills"]}
    assert {
        "human_approval_required",
        "procedural_integrity",
        "deadline_governance",
        "clarifying_questions_required",
        "uncertainty_disclosure",
        "evidence_based_responses",
    }.issubset(skill_ids)
    assert skills.json()["lifecycle"] == [
        "Skill",
        "Execution",
        "Evaluation",
        "Deviation",
        "Correction",
        "Updated Skill Version",
    ]
    assert learning.json()["quality_loop"][-3:] == ["Intervention", "Learning", "Improvement"]
    scenario_ids = {scenario["id"] for scenario in scenarios.json()["scenarios"]}
    assert {"citizen_request", "permit_request", "policy_consultation", "qms_skill_evolution"}.issubset(
        scenario_ids
    )
    assert scenarios.json()["cycle"] == [
        "Goal",
        "Action",
        "Result",
        "Observation",
        "Deviation Detection",
        "Correction",
        "Learning",
        "Improved State",
    ]
    assert "recommendations" in meta.json()
    assert "authority_boundary" in meta.json()


def test_quality_layer_captures_deviation_intervention_and_learning(tmp_path):
    layer = QualityLayer(LearningRepository(tmp_path / "qms_learning_records.jsonl"))

    assessment, modified_response, records = layer.evaluate(
        QualityInput(
            user_session="qms-direct",
            scenario="legal_general:forecast_event_challenges",
            domain="legal_general",
            intent="forecast_event_challenges",
            route="Legal Retrieval",
            risk_level=RiskLevel.HIGH,
            approval_state=ApprovalState.AUTO,
            source_required=True,
            source_count=0,
            policies=[],
            final_response="The deadline was extended and the answer is guaranteed.",
        )
    )

    deviation_skills = {deviation.skill_id for deviation in assessment.deviations}
    assert assessment.release_allowed is False
    assert assessment.quality_score < 70
    assert assessment.final_output_modified is True
    assert "human_approval_required" in deviation_skills
    assert "deadline_governance" in deviation_skills
    assert "evidence_based_responses" in deviation_skills
    assert "Ограничение качества" in modified_response
    assert records
    assert layer.learning_repository.metrics()["learning_records_total"] == len(records)


def test_quality_layer_flags_positioning_answer_without_questions(tmp_path):
    layer = QualityLayer(LearningRepository(tmp_path / "qms_learning_records.jsonl"))

    assessment, _, records = layer.evaluate(
        QualityInput(
            user_session="qms-positioning",
            scenario="testbox_product:strategic_positioning",
            domain="testbox_product",
            intent="strategic_positioning",
            route="Orientation -> Strategic Positioning",
            risk_level=RiskLevel.LOW,
            approval_state=ApprovalState.AUTO,
            source_required=False,
            source_count=0,
            policies=[],
            final_response="ASTREB TESTBOX is a governance runtime.",
        )
    )

    assert "clarifying_questions_required" in {item.skill_id for item in assessment.deviations}
    assert records[0].skill_id == "clarifying_questions_required"


def test_skill_evolution_requires_human_decision_and_preserves_history(tmp_path, monkeypatch):
    client = qms_client(tmp_path, monkeypatch)

    proposal_response = client.post(
        "/api/testbox/runtime/qms/skills/procedural_integrity/evolution",
        json={
            "user_session": "qms-skill-evolution",
            "role": "Governance Officer",
            "reason": "Recurring generic fallback in strategic requests.",
            "proposed_change": "Add strategic positioning fallback guard.",
            "evidence": ["ASTREB TESTBOX positioning query routed to generic intake."],
        },
    )

    assert proposal_response.status_code == 200
    proposal = proposal_response.json()["proposal"]
    assert proposal["status"] == "review_required"
    assert proposal["approval_required"] is True
    assert proposal["automatic_execution"] is False
    assert proposal["history_preserved"] is True
    assert proposal_response.json()["event"]["action"] == "SKILL_EVOLUTION_PROPOSED"

    skills_before = client.get("/api/testbox/runtime/qms/skills").json()["skills"]
    procedural_before = next(skill for skill in skills_before if skill["id"] == "procedural_integrity")
    assert procedural_before["version"] == proposal["current_version"]

    decision_response = client.post(
        f"/api/testbox/runtime/qms/skills/evolution/{proposal['id']}/decision",
        json={
            "user_session": "qms-skill-evolution",
            "role": "Governance Officer",
            "decision": "approve",
            "reason": "Human-approved QMS improvement.",
        },
    )

    assert decision_response.status_code == 200
    decided = decision_response.json()["proposal"]
    assert decided["status"] == "approved_for_skill_version"
    assert decision_response.json()["event"]["action"] == "SKILL_EVOLUTION_APPROVED"
    procedural_after = next(
        skill for skill in decision_response.json()["skills"]["skills"]
        if skill["id"] == "procedural_integrity"
    )
    assert procedural_after["version"] == proposal["proposed_version"]
    assert any("strategic positioning fallback guard" in item for item in procedural_after["improvement_history"])
