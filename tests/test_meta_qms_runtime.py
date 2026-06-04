import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from asti.service import AstiService  # noqa: E402
from asti.store import ActionQueue, AstiAuditLog  # noqa: E402
from testbox_runtime.api import create_testbox_router  # noqa: E402


ADMIN_HEADERS = {"X-AI-Cabinet-Admin-Token": "meta-qms-admin"}


@pytest.fixture(autouse=True)
def configured_privileged_runtime(monkeypatch):
    monkeypatch.setenv("ADMIN_API_TOKEN", "meta-qms-admin")


def meta_qms_client(tmp_path: Path) -> TestClient:
    service = AstiService(
        ActionQueue(tmp_path / "actions.json"),
        AstiAuditLog(tmp_path / "asti_audit.jsonl"),
    )
    app = FastAPI()
    app.include_router(create_testbox_router(tmp_path, service))
    return TestClient(app, headers=ADMIN_HEADERS)


def assessment_payload() -> dict:
    return {
        "user_session": "meta-qms-test",
        "role": "Governance Officer",
        "trigger": "runtime_review",
        "observation": "Source provenance is incomplete for contact person@example.com.",
        "deviation_category": "trust_visibility_gap",
        "affected_layers": [
            "Orientation Layer",
            "Governance Layer",
            "Audit Layer",
            "Learning Layer",
            "Evolution Layer",
        ],
        "risk_level": "medium",
        "evidence": ["Review contact +31 612345678 showed missing source timestamp."],
        "proposed_improvement": "Require source provenance before publication.",
        "acceptance_condition": "A test verifies visible provenance on publishable signals.",
    }


def test_meta_qms_exposes_living_mode_and_human_authority_boundary(tmp_path):
    payload = meta_qms_client(tmp_path).get("/api/testbox/runtime/meta-qms").json()

    assert payload["mode"] == "ASTREB META-QMS Living Evolution"
    assert payload["layers"][-2:] == ["Learning Layer", "Evolution Layer"]
    assert payload["runtime_cycle"][-3:] == ["Reflection", "Learning", "Evolution Proposal"]
    assert "no automatic system change" in payload["authority_boundary"]


def test_meta_qms_assessment_records_redacted_review_required_proposal_and_audit(tmp_path):
    client = meta_qms_client(tmp_path)
    response = client.post("/api/testbox/runtime/meta-qms/assess", json=assessment_payload())

    assert response.status_code == 200
    proposal = response.json()["proposal"]
    assert proposal["status"] == "review_required"
    assert proposal["automatic_execution"] is False
    assert "[EMAIL]" in proposal["observation"]
    assert "person@example.com" not in proposal["observation"]
    assert "[PHONE_OR_IDENTIFIER]" in proposal["evidence"][0]
    events = client.get(
        "/api/testbox/runtime/events", params={"user_session": "meta-qms-test"}
    ).json()["events"]
    assert [event["action"] for event in events] == [
        "QUALITY_ASSESSED",
        "DEVIATION_RECORDED",
        "EVOLUTION_PROPOSED",
    ]


def test_meta_qms_human_decision_does_not_execute_proposed_change(tmp_path):
    client = meta_qms_client(tmp_path)
    proposal_id = client.post(
        "/api/testbox/runtime/meta-qms/assess", json=assessment_payload()
    ).json()["proposal"]["id"]

    response = client.post(
        f"/api/testbox/runtime/meta-qms/proposals/{proposal_id}/decision",
        json={
            "user_session": "meta-qms-test",
            "role": "Governance Officer",
            "decision": "approve",
            "reason": "Approved for a separate implementation plan.",
        },
    )

    assert response.status_code == 200
    proposal = response.json()["proposal"]
    assert proposal["status"] == "approved_for_implementation"
    assert proposal["automatic_execution"] is False
    events = client.get(
        "/api/testbox/runtime/events", params={"user_session": "meta-qms-test"}
    ).json()["events"]
    assert events[-1]["action"] == "EVOLUTION_APPROVED"
    assert events[-1]["payload"]["automatic_execution"] is False


def test_meta_qms_rejects_unknown_layer(tmp_path):
    client = meta_qms_client(tmp_path)
    payload = assessment_payload()
    payload["affected_layers"] = ["Autonomous Magic Layer"]

    response = client.post("/api/testbox/runtime/meta-qms/assess", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "unknown_meta_qms_layer"


def test_meta_qms_rejects_unauthenticated_privileged_request(tmp_path):
    authenticated_client = meta_qms_client(tmp_path)
    unauthenticated_client = TestClient(authenticated_client.app)

    response = unauthenticated_client.post(
        "/api/testbox/runtime/meta-qms/assess", json=assessment_payload()
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid_admin_token"
