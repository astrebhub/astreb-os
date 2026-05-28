import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "backend"))

from asti.api import create_asti_router  # noqa: E402
from asti.executors import LocalReportExecutor, NoOpExecutor, TelegramExecutor  # noqa: E402
from asti.models import Action, ExecutorType  # noqa: E402
from asti.service import AstiService  # noqa: E402
from asti.store import ActionQueue, AstiAuditLog  # noqa: E402


TELEGRAM_HEADERS = {"X-Telegram-Bot-Api-Secret-Token": "webhook-secret"}
ADMIN_HEADERS = {"X-AI-Cabinet-Admin-Token": "admin-secret"}


@pytest.fixture(autouse=True)
def configured_privileged_runtime(monkeypatch):
    monkeypatch.setenv("ADMIN_API_TOKEN", "admin-secret")
    monkeypatch.setenv("ASTI_EXTERNAL_EXECUTION_ENABLED", "true")


class RecordingTelegramExecutor:
    def __init__(self) -> None:
        self.calls = []

    def execute(self, action):
        self.calls.append(action.id)
        return {
            "executor": "telegram",
            "method": "sendMessage",
            "chat_id": "1001",
            "message_id": 44,
            "telegram_message_id": 44,
        }


def asti_client(tmp_path: Path, telegram_executor=None):
    queue = ActionQueue(tmp_path / "actions.json")
    audit = AstiAuditLog(tmp_path / "audit.jsonl")
    telegram_executor = telegram_executor or RecordingTelegramExecutor()
    service = AstiService(
        queue,
        audit,
        executors={
            ExecutorType.TELEGRAM: telegram_executor,
            ExecutorType.LOCAL_REPORT: LocalReportExecutor(),
            ExecutorType.NO_OP: NoOpExecutor(),
        },
    )
    app = FastAPI()
    app.include_router(create_asti_router(tmp_path, service))
    return TestClient(app, headers=ADMIN_HEADERS), audit, telegram_executor


def test_action_requires_approval_before_telegram_execution(tmp_path):
    client, audit, telegram = asti_client(tmp_path)

    response = client.post("/asti/task", json={"text": "test message"})
    assert response.status_code == 200
    action_id = response.json()["action"]["id"]
    assert response.json()["action"]["status"] == "pending"

    blocked = client.post(f"/asti/actions/{action_id}/execute")
    assert blocked.status_code == 409
    assert telegram.calls == []

    approved = client.post(f"/asti/actions/{action_id}/approve")
    assert approved.json()["action"]["status"] == "approved"

    executed = client.post(f"/asti/actions/{action_id}/execute")
    assert executed.json()["action"]["status"] == "executed"
    assert executed.json()["action"]["execution_metadata"]["executor"] == "telegram"
    assert executed.json()["action"]["execution_metadata"]["telegram_message_id"] == 44
    assert executed.json()["action"]["execution_metadata"]["executed_at"]
    assert telegram.calls == [action_id]

    repeated = client.post(f"/asti/actions/{action_id}/execute")
    assert repeated.status_code == 409
    assert telegram.calls == [action_id]
    assert [event.event.value for event in audit.list(action_id)] == [
        "created",
        "execution_blocked",
        "approved",
        "execution_started",
        "executed",
        "duplicate_execute_attempt",
        "execution_blocked",
    ]
    assert executed.json()["action"]["execution_started_at"]
    assert executed.json()["action"]["execution_attempt_id"]
    assert (
        executed.json()["action"]["execution_metadata"]["execution_attempt_id"]
        == executed.json()["action"]["execution_attempt_id"]
    )


def test_rejected_action_never_executes(tmp_path):
    client, audit, telegram = asti_client(tmp_path)
    action_id = client.post("/asti/task", json={"task": "declined message"}).json()["action"]["id"]

    rejected = client.post(f"/asti/actions/{action_id}/reject", json={"reason": "not authorized"})
    blocked = client.post(f"/asti/actions/{action_id}/execute")

    assert rejected.json()["action"]["status"] == "rejected"
    assert blocked.status_code == 409
    assert telegram.calls == []
    assert [event.event.value for event in audit.list(action_id)] == [
        "created",
        "rejected",
        "execution_blocked",
    ]


def test_local_report_and_no_op_fallbacks_return_metadata_after_approval(tmp_path):
    client, _, telegram = asti_client(tmp_path)

    for executor in ("local_report", "no_op"):
        action = client.post(
            "/asti/task", json={"text": "local task", "executor": executor}
        ).json()["action"]
        client.post(f"/asti/actions/{action['id']}/approve")
        executed = client.post(f"/asti/actions/{action['id']}/execute").json()["action"]
        assert executed["execution_metadata"]["executor"] == executor

    assert telegram.calls == []


def test_telegram_owner_command_flow_creates_approves_and_executes_action(tmp_path, monkeypatch):
    monkeypatch.setenv("TELEGRAM_OWNER_CHAT_ID", "1001")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "webhook-secret")
    client, audit, telegram = asti_client(tmp_path)

    created = client.post(
        "/webhooks/telegram",
        headers=TELEGRAM_HEADERS,
        json={"update_id": 1, "message": {"chat": {"id": 1001}, "text": "/task test message"}},
    )
    action_id = created.json()["action"]["id"]
    inbox = client.post(
        "/webhooks/telegram",
        headers=TELEGRAM_HEADERS,
        json={"update_id": 2, "message": {"chat": {"id": 1001}, "text": "/actions"}},
    )
    assert inbox.json()["actions"][0]["status"] == "pending"

    client.post(
        "/webhooks/telegram",
        headers=TELEGRAM_HEADERS,
        json={"update_id": 3, "message": {"chat": {"id": 1001}, "text": f"/approve {action_id}"}},
    )
    executed = client.post(
        "/webhooks/telegram",
        headers=TELEGRAM_HEADERS,
        json={"update_id": 4, "message": {"chat": {"id": 1001}, "text": f"/execute {action_id}"}},
    )
    assert executed.json()["action"]["status"] == "executed"
    assert telegram.calls == [action_id]
    assert [event.event.value for event in audit.list(action_id)] == [
        "created",
        "approved",
        "execution_started",
        "executed",
    ]


def test_telegram_webhook_rejects_unknown_chat(tmp_path, monkeypatch):
    monkeypatch.setenv("TELEGRAM_OWNER_CHAT_ID", "1001")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "webhook-secret")
    client, _, telegram = asti_client(tmp_path)

    response = client.post(
        "/webhooks/telegram",
        headers=TELEGRAM_HEADERS,
        json={"update_id": 5, "message": {"chat": {"id": 9999}, "text": "/task unauthorized"}},
    )

    assert response.status_code == 403
    assert client.get("/asti/inbox").json()["count"] == 0
    assert telegram.calls == []


def test_direct_asti_routes_require_admin_token(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_API_TOKEN", "admin-secret")
    client, _, _ = asti_client(tmp_path)
    unauthenticated_client = TestClient(client.app)

    unauthorized = unauthenticated_client.post("/asti/task", json={"text": "not accepted"})
    authorized = client.post(
        "/asti/task",
        json={"text": "accepted"},
        headers={"X-AI-Cabinet-Admin-Token": "admin-secret"},
    )

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200


def test_telegram_execution_is_frozen_without_explicit_release_flag(tmp_path, monkeypatch):
    monkeypatch.delenv("ASTI_EXTERNAL_EXECUTION_ENABLED", raising=False)
    client, audit, telegram = asti_client(tmp_path)
    action_id = client.post("/asti/task", json={"text": "must stay queued"}).json()["action"]["id"]
    client.post(f"/asti/actions/{action_id}/approve")

    blocked = client.post(f"/asti/actions/{action_id}/execute")

    assert blocked.status_code == 503
    assert blocked.json()["detail"] == "external_execution_frozen"
    assert telegram.calls == []
    assert audit.list(action_id)[-1].event.value == "execution_blocked"
    assert audit.list(action_id)[-1].metadata["reason"] == "external_execution_frozen"


def test_telegram_executor_reads_env_and_returns_delivery_metadata(monkeypatch):
    class Response:
        is_success = True

        @staticmethod
        def json():
            return {"ok": True, "result": {"message_id": 91}}

    captured = {}

    def post(url, json, timeout):
        captured.update({"url": url, "json": json, "timeout": timeout})
        return Response()

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "telegram-secret")
    monkeypatch.setenv("TELEGRAM_OWNER_CHAT_ID", "1001")
    monkeypatch.setattr("asti.executors.httpx.post", post)

    metadata = TelegramExecutor().execute(
        Action(executor=ExecutorType.TELEGRAM, payload={"text": "approved"})
    )

    assert captured["url"].endswith("/bottelegram-secret/sendMessage")
    assert captured["json"] == {"chat_id": "1001", "text": "approved"}
    assert metadata["executor"] == "telegram"
    assert metadata["message_id"] == 91
    assert metadata["telegram_message_id"] == 91
    assert "telegram-secret" not in str(metadata)


def test_execution_failure_stays_in_progress_and_cannot_retry_send(tmp_path, monkeypatch):
    class FailedResponse:
        is_success = False

    monkeypatch.setattr("asti.executors.httpx.post", lambda *args, **kwargs: FailedResponse())
    client, audit, _ = asti_client(
        tmp_path, TelegramExecutor(token="secret-token", owner_chat_id="1001")
    )
    action_id = client.post("/asti/task", json={"text": "approved send"}).json()["action"]["id"]
    client.post(f"/asti/actions/{action_id}/approve")

    failed = client.post(f"/asti/actions/{action_id}/execute")
    action = client.get("/asti/inbox").json()["actions"][0]
    repeated = client.post(f"/asti/actions/{action_id}/execute")

    assert failed.status_code == 502
    assert "secret-token" not in failed.text
    assert action["status"] == "execution_in_progress"
    assert action["execution_attempt_id"]
    assert repeated.status_code == 409
    assert [event.event.value for event in audit.list(action_id)] == [
        "created",
        "approved",
        "execution_started",
        "execution_failed",
        "duplicate_execute_attempt",
        "execution_blocked",
    ]
    assert "secret-token" not in str([event.metadata for event in audit.list(action_id)])


def test_invalid_telegram_webhook_secret_is_rejected_and_audited(tmp_path, monkeypatch):
    monkeypatch.setenv("TELEGRAM_OWNER_CHAT_ID", "1001")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "webhook-secret")
    client, audit, telegram = asti_client(tmp_path)

    response = client.post(
        "/webhooks/telegram",
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
        json={"update_id": 6, "message": {"chat": {"id": 1001}, "text": "/task denied"}},
    )

    assert response.status_code == 403
    assert telegram.calls == []
    assert [event.event.value for event in audit.list()] == ["invalid_webhook_secret"]
    assert "webhook-secret" not in str(audit.list()[0].metadata)


def test_replayed_telegram_update_is_ignored_and_audited(tmp_path, monkeypatch):
    monkeypatch.setenv("TELEGRAM_OWNER_CHAT_ID", "1001")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "webhook-secret")
    client, audit, _ = asti_client(tmp_path)
    update = {"update_id": 7, "message": {"chat": {"id": 1001}, "text": "/task once"}}

    first = client.post("/webhooks/telegram", headers=TELEGRAM_HEADERS, json=update)
    duplicate = client.post("/webhooks/telegram", headers=TELEGRAM_HEADERS, json=update)

    assert first.status_code == 200
    assert duplicate.json() == {"status": "ignored", "reason": "duplicate_webhook_update"}
    assert client.get("/asti/inbox").json()["count"] == 1
    assert [event.event.value for event in audit.list()] == ["created", "duplicate_webhook_update"]


def test_unknown_executor_is_rejected_by_allowlist(tmp_path):
    client, _, _ = asti_client(tmp_path)

    response = client.post("/asti/task", json={"text": "no", "executor": "arbitrary_tool"})

    assert response.status_code == 422
    assert client.get("/asti/inbox").json()["count"] == 0


def test_prod_mode_requires_admin_api_token_at_router_startup(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_CABINET_ENV", "prod")
    monkeypatch.delenv("ADMIN_API_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="admin_api_token_required_in_prod"):
        create_asti_router(tmp_path)


def test_prod_preview_refuses_external_execution_flag_at_router_startup(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_CABINET_ENV", "prod")
    monkeypatch.setenv("ADMIN_API_TOKEN", "production-placeholder")
    monkeypatch.setenv("ASTI_EXTERNAL_EXECUTION_ENABLED", "true")

    with pytest.raises(RuntimeError, match="external_execution_forbidden_in_production_preview"):
        create_asti_router(tmp_path)
