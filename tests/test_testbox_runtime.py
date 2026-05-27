import json
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "backend"))

from main import app as surface_app  # noqa: E402
from asti.api import create_asti_router  # noqa: E402
from asti.executors import NoOpExecutor  # noqa: E402
from asti.models import ExecutorType  # noqa: E402
from asti.service import AstiService  # noqa: E402
from asti.store import ActionQueue, AstiAuditLog  # noqa: E402
from testbox_runtime.api import create_testbox_router  # noqa: E402
import testbox_runtime.api as testbox_api  # noqa: E402
from testbox_runtime.constitution import (  # noqa: E402
    POLICY_INSTRUCTIONS,
    ROLE_INSTRUCTIONS,
    SKILL_INSTRUCTIONS,
    SYSTEM_INSTRUCTION,
)
from testbox_runtime.orientation_registry import (  # noqa: E402
    DOMAIN_REGISTRY,
    OPERATIONAL_INTENT_REGISTRY,
    TERM_REGISTRY,
)
from testbox_runtime.roles import CORE_ROLES  # noqa: E402


ADMIN_HEADERS = {"X-AI-Cabinet-Admin-Token": "runtime-test-admin"}
surface_client = TestClient(surface_app)
client: TestClient


@pytest.fixture(autouse=True)
def isolated_runtime_client(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_API_TOKEN", "runtime-test-admin")
    service = AstiService(
        ActionQueue(tmp_path / "global-asti-actions.json"),
        AstiAuditLog(tmp_path / "global-asti-audit.jsonl"),
    )
    isolated_app = FastAPI()
    isolated_app.include_router(create_testbox_router(tmp_path, service))
    isolated_app.include_router(create_asti_router(tmp_path, service))
    global client
    client = TestClient(isolated_app, headers=ADMIN_HEADERS)
    yield
    client.close()
TBX_BUS_ENERGY_001_INPUT = (
    "хочу открыть компанию по производству источников хранения электричества"
)
TBX_HOU_SOCIAL_001_INPUT = "как мне узнать я имею право на социальное жилье (аренда)"
TBX_EMP_ZEROHOURS_001_INPUT = "мне предлогают заключить нулевой контракт что это значит"


def test_orientation_registry_contains_governed_acceptance_domains_and_terms():
    """Architecture guard: new topics extend registry data, not runtime branches."""
    domain_ids = {definition.id for definition in DOMAIN_REGISTRY}
    term_map = {term.variant: term.canonical for term in TERM_REGISTRY}

    assert {
        "event_collaboration",
        "business_formation",
        "consulting_services",
        "battery_manufacturing",
        "social_housing",
        "employment_contract",
        "zzp_intermediary_contract",
        "residential_parking",
    }.issubset(domain_ids)
    assert term_map["нулевой контракт"] == "nulurencontract"
    assert term_map["cooperatie ua"] == "cooperatie UA"


def test_runtime_uses_grounded_answer_composer_boundary():
    """Architecture guard: core decides orientation; composer produces user-facing text."""
    runtime_source = (ROOT_DIR / "backend" / "testbox_runtime" / "legalbox.py").read_text(
        encoding="utf-8"
    )

    assert "self.answer_composer = GroundedAnswerComposer()" in runtime_source
    assert "self.answer_composer.compose(" in runtime_source
    assert "self.orientation_core = OrientationCore()" in runtime_source
    assert "self.orientation_core.orient(" in runtime_source
    assert "runtime_roles = role_assignment_for(orientation)" in runtime_source


def test_api_enters_central_orchestrator_before_specialised_routes():
    api_source = (ROOT_DIR / "backend" / "testbox_runtime" / "api.py").read_text(
        encoding="utf-8"
    )
    orchestration_source = (
        ROOT_DIR / "backend" / "testbox_runtime" / "orchestration.py"
    ).read_text(encoding="utf-8")

    assert "TestboxOrchestrator" in api_source
    assert "self.orientation_runtime.process_message(request)" in orchestration_source
    assert 'orientation.route_key != "asti_action_queue"' in orchestration_source
    assert "self.asti_service.create_task(" in orchestration_source


def test_operational_roles_are_backend_runtime_definitions_not_policy_labels():
    roles = {role.id: role for role in CORE_ROLES}

    assert {
        "orientation_architect",
        "legalbox_specialist",
        "businessbox_strategist",
        "documentbox_analyst",
        "letterbox_composer",
        "asti_action_supervisor",
        "governance_officer",
        "audit_narrator",
        "memory_coordinator",
        "runtime_orchestrator",
    } == set(roles)
    assert "No external execution" in roles["letterbox_composer"].constraints
    assert "Approval Enforcement" in roles["asti_action_supervisor"].skills
    assert all("legal_answers_require_sources" not in role.skills for role in CORE_ROLES)


def test_runtime_roles_endpoint_exposes_operational_registry():
    response = client.get("/api/testbox/runtime/roles")

    assert response.status_code == 200
    role_names = [role["name"] for role in response.json()["roles"]]
    assert role_names[0] == "Orientation Architect"
    assert "Runtime Orchestrator" in role_names
    assert "ASTI Action Supervisor" in role_names


def test_runtime_constitution_exposes_separate_behavioral_instruction_levels():
    response = client.get("/api/testbox/runtime/constitution")

    assert response.status_code == 200
    instructions = response.json()["instructions"]
    ids = {instruction["id"] for instruction in instructions}
    levels = {instruction["level"] for instruction in instructions}
    assert levels == {"system", "role", "skill", "policy"}
    assert SYSTEM_INSTRUCTION.id in ids
    assert ROLE_INSTRUCTIONS["LegalBox Specialist"].id in ids
    assert SKILL_INSTRUCTIONS["legal_retrieval"].id in ids
    assert POLICY_INSTRUCTIONS["asti_execution"].id in ids
    assert POLICY_INSTRUCTIONS["active_task_execution"].id in ids
    assert POLICY_INSTRUCTIONS["limitation_reporting"].id in ids
    assert POLICY_INSTRUCTIONS["governance_balance"].id in ids
    assert POLICY_INSTRUCTIONS["context_continuity"].id in ids
    assert POLICY_INSTRUCTIONS["mission_fact_integrity"].id in ids


def test_operational_choices_offered_by_administrator_are_executable_intents():
    intent_ids = {definition.intent for definition in OPERATIONAL_INTENT_REGISTRY}

    assert {
        "introduce_system",
        "draft_letter",
        "review_document",
        "build_action_plan",
        "assess_situation",
        "request_external_action",
    }.issubset(
        intent_ids
    )


def test_liability_question_uses_governed_legalbox_route():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": (
                "В меня врезался велосипедист на моем авто в Нидерландах. "
                "Он требует компенсацию. Законно ли это?"
            ),
            "user_session": "runtime-test-liability",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_level"] == "high"
    assert payload["approval_state"] == "REQUIRES_HUMAN_REVIEW"
    assert payload["route"] == "Legal Retrieval -> Governed Draft -> Human Review"
    assert "legal_answers_require_sources" in payload["policies"]
    assert "high_risk_requires_approval" in payload["policies"]
    assert "RiskLevel." not in payload["final_response"]
    assert "REQUIRES_HUMAN_REVIEW" not in payload["final_response"]


def test_liability_retrieval_excludes_immigration_sources():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": (
                "В меня врезался велосипедист на моем авто в Нидерландах. "
                "Он требует компенсацию."
            ),
            "user_session": "runtime-test-source-domain",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    source_ids = [source["id"] for source in response.json()["sources"]]
    assert "wetten-wvw-article-185" in source_ids
    assert "rijksoverheid-wa-insurance" in source_ids
    assert "ind-ukraine-temporary-protection" not in source_ids


def test_runtime_emits_observable_legal_events():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Fietser vraagt schadevergoeding na een aanrijding met mijn auto in Nederland.",
            "user_session": "runtime-test-events",
            "role": "Governance Officer",
            "language": "nl",
        },
    )

    actions = [event["action"] for event in response.json()["events"]]
    assert actions == [
        "MESSAGE_RECEIVED",
        "USER_MESSAGE_RECEIVED",
        "LANGUAGE_DETECTED",
        "INTENT_DETECTED",
        "DOMAIN_GRAPH_CREATED",
        "SITUATION_MODEL_CREATED",
        "MODE_SELECTED",
        "ROLE_ASSIGNMENT_SELECTED",
        "BEHAVIORAL_INSTRUCTIONS_APPLIED",
        "JURISDICTION_DETECTED",
        "LEGAL_CLASSIFIED",
        "RISK_FLAGGED",
        "SOURCE_REQUIRED",
        "LEGAL_RETRIEVAL_COMPLETED",
        "ROUTE_SELECTED",
        "ROUTING_SELECTED",
        "ANSWER_STRATEGY_SELECTED",
        "ACTIVE_TASK_EXECUTION_ATTEMPTED",
        "ANSWER_GENERATED",
        "DISCLAIMER_ATTACHED",
        "HUMAN_REVIEW_REQUIRED",
        "MEMORY_UPDATED",
    ]


def test_user_console_is_wired_to_backend_runtime():
    response = surface_client.get("/testbox/user")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert 'fetch("/api/testbox/runtime/message"' in response.text
    assert "attachment_names: state.userAttachments.map((file) => file.name)" in response.text
    assert "document_extraction: state.documentExtraction" in response.text
    assert 'id="documentOpenLink"' in response.text
    assert '<div class="document-viewer empty" id="documentViewer">' in response.text
    assert "Документ не прикреплён. Загрузите PDF/фото" in response.text
    assert "message-attachments" in response.text
    assert 'state.documentName = "sample-employment-contract.pdf"' in response.text
    assert "Backend runtime не работает из отдельно открытого HTML-файла." in response.text


def test_user_console_offers_explicit_clipboard_paste_without_intercepting_native_paste():
    response = surface_client.get("/testbox/user")

    assert response.status_code == 200
    assert 'id="pasteUserText"' in response.text
    assert 'id="clipboardStatus"' in response.text
    assert "async function pasteUserTextFromClipboard()" in response.text
    assert "showClipboardStatus(tx(\"pasteWorking\"))" in response.text
    assert "showClipboardStatus(tx(\"pasteSuccess\").replace(\"{count}\", clipboardText.length), \"success\")" in response.text
    assert 'userInput.scrollIntoView({ behavior: "smooth", block: "center" });' in response.text
    assert "navigator.clipboard?.readText" in response.text
    assert 'fetch("/api/testbox/runtime/clipboard/read", {' in response.text
    assert 'headers: privilegedRuntimeHeaders()' in response.text
    paste_function = response.text.split("async function pasteUserTextFromClipboard()", 1)[1].split(
        "async function extractDocument", 1
    )[0]
    assert paste_function.index("/api/testbox/runtime/clipboard/read") < paste_function.index(
        "navigator.clipboard?.readText"
    )
    assert "clipboard_timeout" in paste_function
    assert 'pasteUserButton.addEventListener("click", pasteUserTextFromClipboard);' in response.text
    assert 'userInput.addEventListener("paste"' not in response.text


def test_local_clipboard_fallback_is_explicit_and_does_not_persist_text(monkeypatch):
    monkeypatch.setattr(testbox_api, "read_local_clipboard_text", lambda: "safe paste fixture")

    response = client.post("/api/testbox/runtime/clipboard/read")

    assert response.status_code == 200
    assert response.json() == {"text": "safe paste fixture", "storage": "not_persisted"}


def test_local_clipboard_fallback_requires_privileged_auth():
    unauthenticated_client = TestClient(client.app)

    response = unauthenticated_client.post("/api/testbox/runtime/clipboard/read")

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid_admin_token"


def test_runtime_intake_and_registry_require_privileged_auth():
    unauthenticated_client = TestClient(client.app)

    message = unauthenticated_client.post(
        "/api/testbox/runtime/message",
        json={"message": "hello", "user_session": "denied", "role": "Operator", "language": "en"},
    )

    assert message.status_code == 401
    for path in (
        "/api/testbox/runtime/sources",
        "/api/testbox/runtime/roles",
        "/api/testbox/runtime/constitution",
    ):
        response = unauthenticated_client.get(path)
        assert response.status_code == 401
        assert response.json()["detail"] == "invalid_admin_token"


def test_letter_request_enters_draft_intake_instead_of_repeating_general_prompt():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "подготовка письма",
            "user_session": "runtime-test-general-ru",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    intent_event = next(
        event for event in payload["events"] if event["action"] == "INTENT_DETECTED"
    )
    assert payload["route"] == "LetterBox -> Draft Generation"
    assert intent_event["payload"]["intent"] == "letter_draft"
    assert payload["orientation"]["mode"] == "LetterBox Mode"
    assert "active_task_execution_policy" in payload["policies"]
    assert "policy.active_task_execution" in payload["behavioral_instructions"]["policy_instructions"]
    assert "Хорошо, подготовим письмо." in payload["final_response"]
    assert "Начальный черновик" in payload["final_response"]
    assert "Кому письмо" in payload["final_response"]
    assert "Я получил ваш запрос." not in payload["final_response"]
    assert "TESTBOX received the request as a general user interaction" not in payload["final_response"]


def test_identity_question_returns_system_introduction_and_approval_boundary():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "привет кто ты и что умеешь делать",
            "user_session": "runtime-test-introduction-ru",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    intent_event = next(
        event for event in payload["events"] if event["action"] == "INTENT_DETECTED"
    )
    assert payload["route"] == "Local AI"
    assert intent_event["payload"]["intent"] == "explanation"
    assert "TESTBOX Administrator" in payload["final_response"]
    assert "ASTI" in payload["final_response"]
    assert "явного одобрения" in payload["final_response"]
    assert "Я получил ваш запрос." not in payload["final_response"]


def test_generic_letter_follow_up_reuses_letterbox_task_context():
    session = "runtime-test-generic-letter-follow-up"
    client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "подготовка письма",
            "user_session": session,
            "role": "Operator",
            "language": "ru",
        },
    )
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "подробнее?",
            "user_session": session,
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    actions = {event["action"] for event in payload["events"]}
    assert payload["orientation"]["mode"] == "LetterBox Mode"
    assert payload["route"] == "LetterBox -> Draft Generation"
    assert "CONTEXT_REUSED" in actions
    assert "FOLLOW_UP_RESOLVED" in actions
    assert "context_continuity_policy" in payload["policies"]
    assert "Начальный черновик" in payload["final_response"]
    assert "Я получил ваш запрос." not in payload["final_response"]


def test_orientation_core_routes_payment_claim_letter_to_letterbox():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "составь черновик письма притензии о просрочке оплаты",
            "user_session": "runtime-test-payment-claim-letter",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    normalized_event = next(
        event for event in payload["events"] if event["action"] == "TERM_NORMALIZED"
    )
    assert payload["orientation"]["intent"] == "letter_draft"
    assert payload["orientation"]["mode"] == "LetterBox Mode"
    assert payload["orientation"]["route_key"] == "letter_preparation"
    assert payload["runtime_roles"]["primary_role"] == "LetterBox Composer"
    assert "Runtime Orchestrator" in payload["runtime_roles"]["active_roles"]
    assert payload["behavioral_instructions"]["system_instruction"] == "system.testbox_runtime"
    assert "role.letterbox_composer" in payload["behavioral_instructions"]["role_instructions"]
    assert {"from": "притензии", "to": "претензии", "rule": "typo_correction"} in normalized_event["payload"]["normalizations"]
    assert "Хорошо, подготовим письмо." in payload["final_response"]
    assert "Я получил ваш запрос." not in payload["final_response"]


def test_orientation_core_routes_document_check_to_documentbox():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "проверь этот документ",
            "user_session": "runtime-test-documentbox",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    assert payload["orientation"]["intent"] == "document_review"
    assert payload["orientation"]["mode"] == "DocumentBox Mode"
    assert payload["orientation"]["route_key"] == "document_review"
    assert payload["runtime_roles"]["primary_role"] == "DocumentBox Analyst"
    assert "role.documentbox_analyst" in payload["behavioral_instructions"]["role_instructions"]
    assert payload["route"] == "DocumentBox -> Analysis Attempt"
    assert "active_task_execution_policy" in payload["policies"]
    assert "limitation_reporting_policy" in payload["policies"]
    assert "policy.limitation_reporting" in payload["behavioral_instructions"]["policy_instructions"]
    assert "Попытка анализа" in payload["final_response"]
    assert "Загрузите файл" in payload["final_response"]


def test_document_check_typo_is_normalized_and_routes_to_documentbox():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "проверь докмент",
            "user_session": "runtime-test-documentbox-typo",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    normalized_event = next(
        event for event in payload["events"] if event["action"] == "TERM_NORMALIZED"
    )
    assert payload["orientation"]["intent"] == "document_review"
    assert payload["orientation"]["mode"] == "DocumentBox Mode"
    assert {"from": "докмент", "to": "документ", "rule": "typo_correction"} in (
        normalized_event["payload"]["normalizations"]
    )
    assert "Хорошо, проверим документ" in payload["final_response"]


def test_document_explanation_with_attached_contract_uses_documentbox_not_legal_fallback():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "обьясни документ",
            "document_text": (
                "CONTRACT: Payment due 14 January 2025. Amount EUR 1,250. "
                "Termination notice 30 days."
            ),
            "document_extraction": {
                "extracted_text": (
                    "CONTRACT: Payment due 14 January 2025. Amount EUR 1,250. "
                    "Termination notice 30 days."
                ),
                "extraction_status": "provided",
                "confidence": 0.95,
                "pages_seen": 1,
                "method": "provided_text",
            },
            "user_session": "runtime-test-explain-uploaded-document",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    assert payload["orientation"]["intent"] == "document_review"
    assert payload["orientation"]["mode"] == "DocumentBox Mode"
    assert payload["orientation"]["route_key"] == "document_review"
    assert payload["runtime_roles"]["primary_role"] == "DocumentBox Analyst"
    assert payload["approval_state"] == "REQUIRES_HUMAN_REVIEW"
    assert "active_task_execution_policy" in payload["policies"]
    assert "policy.active_task_execution" in payload["behavioral_instructions"]["policy_instructions"]
    analysis_event = next(
        event for event in payload["events"]
        if event["action"] == "ACTIVE_TASK_ANALYSIS_ATTEMPTED"
    )
    extraction_event = next(
        event for event in payload["events"]
        if event["action"] == "DOCUMENT_EXTRACTION_ATTEMPTED"
    )
    assert analysis_event["payload"]["readable_text_available"] is True
    assert extraction_event["payload"]["extraction_status"] == "readable_text_received"
    assert payload["document_extraction"]["extracted_text"].startswith("CONTRACT:")
    assert payload["document_extraction"]["confidence"] == 0.95
    assert payload["document_extraction"]["pages_seen"] == 1
    assert "1. Найденные данные" in payload["final_response"]
    assert "Найдена сумма: EUR 1,250" in payload["final_response"]
    assert "Найден срок оплаты: 14 January 2025" in payload["final_response"]
    assert "Найден срок уведомления о прекращении: 30 days" in payload["final_response"]
    assert "Чего не хватает в доступном тексте" in payload["final_response"]
    assert "Ограничения анализа" in payload["final_response"]
    assert "Загрузите файл" not in payload["final_response"]
    assert "не нашел подключенных официальных источников" not in payload["final_response"]


def test_bare_document_check_with_unreadable_pdf_acknowledges_attachment_in_documentbox():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "проверь документ",
            "document_text": (
                "PDF preview is available, but text was not extractable in-browser. "
                "This may be a scanned PDF or compressed PDF stream."
            ),
            "attachment_names": ["contract_DY1401250033.pdf"],
            "user_session": "runtime-test-unreadable-pdf",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    assert payload["orientation"]["intent"] == "document_review"
    assert payload["orientation"]["mode"] == "DocumentBox Mode"
    assert payload["orientation"]["route_key"] == "document_review"
    assert payload["runtime_roles"]["primary_role"] == "DocumentBox Analyst"
    assert "active_task_execution_policy" in payload["policies"]
    assert "limitation_reporting_policy" in payload["policies"]
    analysis_event = next(
        event for event in payload["events"]
        if event["action"] == "ACTIVE_TASK_ANALYSIS_ATTEMPTED"
    )
    assert analysis_event["payload"]["readable_text_available"] is False
    assert "DOCUMENT_EXTRACTION_ATTEMPTED" in [event["action"] for event in payload["events"]]
    assert "OCR_REQUIRED" in [event["action"] for event in payload["events"]]
    assert payload["document_extraction"]["extraction_status"] == "ocr_required"
    assert payload["document_extraction"]["limitation_reason"] == "no_readable_document_text"
    assert "contract_DY1401250033.pdf" in payload["final_response"]
    assert "не удалось извлечь читаемый текст" in payload["final_response"]
    assert "Ограничения анализа" in payload["final_response"]
    assert "LIMITATION_REPORTED" in [event["action"] for event in payload["events"]]
    assert "Загрузите файл" not in payload["final_response"]


def test_document_review_follow_up_keeps_documentbox_context_and_performs_selected_checks():
    document_text = (
        "CONTRACT: Payment due 14 January 2025. Amount EUR 1,250. "
        "Termination notice 30 days."
    )
    session = "runtime-test-document-follow-up"
    first_response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "проверь документ",
            "document_text": document_text,
            "attachment_names": ["contract_DY1401250033.pdf"],
            "user_session": session,
            "role": "Operator",
            "language": "ru",
        },
    )
    assert first_response.json()["orientation"]["mode"] == "DocumentBox Mode"

    follow_up = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "краткое объяснение содержания, поиск рисков, проверка оплаты/сроков",
            "document_text": document_text,
            "attachment_names": ["contract_DY1401250033.pdf"],
            "user_session": session,
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = follow_up.json()
    actions = {event["action"] for event in payload["events"]}
    assert payload["orientation"]["intent"] == "document_review"
    assert payload["orientation"]["mode"] == "DocumentBox Mode"
    assert payload["orientation"]["route_key"] == "document_review"
    assert payload["runtime_roles"]["primary_role"] == "DocumentBox Analyst"
    assert "CONTEXT_REUSED" in actions
    assert "FOLLOW_UP_RESOLVED" in actions
    assert "active_task_execution_policy" in payload["policies"]
    assert "policy.active_task_execution" in payload["behavioral_instructions"]["policy_instructions"]
    assert "context_continuity_policy" in payload["policies"]
    assert "policy.context_continuity" in payload["behavioral_instructions"]["policy_instructions"]
    assert "Проверка выполняется по выбранным направлениям" in payload["final_response"]
    assert "Найдена сумма: EUR 1,250" in payload["final_response"]
    assert "Найден срок оплаты: 14 January 2025" in payload["final_response"]
    assert "Я получил ваш запрос" not in payload["final_response"]


def test_unreadable_pdf_follow_up_stays_in_documentbox_without_claiming_content():
    document_text = (
        "PDF preview is available, but text was not extractable in-browser. "
        "This may be a scanned PDF or compressed PDF stream."
    )
    session = "runtime-test-unreadable-pdf-follow-up"
    client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "проверь документ",
            "document_text": document_text,
            "attachment_names": ["contract_DY1401250033.pdf"],
            "user_session": session,
            "role": "Operator",
            "language": "ru",
        },
    )
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "краткое объяснение содержания, поиск рисков, проверка оплаты/сроков",
            "document_text": document_text,
            "attachment_names": ["contract_DY1401250033.pdf"],
            "user_session": session,
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    assert payload["orientation"]["mode"] == "DocumentBox Mode"
    assert "active_task_execution_policy" in payload["policies"]
    assert "не удалось извлечь читаемый текст" in payload["final_response"]
    assert "Я получил ваш запрос" not in payload["final_response"]


def test_document_focus_request_routes_to_documentbox_when_attachment_is_active_without_session_memory():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "краткое объяснение содержания, поиск рисков, проверка оплаты/сроков",
            "document_text": "Invoice amount EUR 500. Payment due 25 May 2026.",
            "attachment_names": ["payment_terms.pdf"],
            "user_session": "runtime-test-active-document-without-memory",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    assert payload["orientation"]["mode"] == "DocumentBox Mode"
    assert payload["orientation"]["route_key"] == "document_review"
    assert "active_task_execution_policy" in payload["policies"]
    assert "Проверка выполняется по выбранным направлениям" in payload["final_response"]
    assert "Найдена сумма: EUR 500" in payload["final_response"]


def test_orientation_core_routes_external_send_request_to_pending_asti_action_without_execution(
    tmp_path,
):
    audit = AstiAuditLog(tmp_path / "asti-audit.jsonl")
    service = AstiService(ActionQueue(tmp_path / "asti-actions.json"), audit)
    isolated_app = FastAPI()
    isolated_app.include_router(create_testbox_router(tmp_path, service))
    isolated_app.include_router(create_asti_router(tmp_path, service))
    isolated_client = TestClient(isolated_app, headers=ADMIN_HEADERS)

    response = isolated_client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "отправь сообщение клиенту",
            "user_session": "runtime-test-asti-orientation",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    assert payload["orientation"]["intent"] == "external_action_request"
    assert payload["orientation"]["mode"] == "ASTI Action Mode"
    assert payload["orientation"]["route_key"] == "asti_action_queue"
    assert payload["runtime_roles"]["primary_role"] == "ASTI Action Supervisor"
    assert "Governance Officer" in payload["runtime_roles"]["active_roles"]
    assert "role.asti_action_supervisor" in payload["behavioral_instructions"]["role_instructions"]
    assert "policy.asti_execution" in payload["behavioral_instructions"]["policy_instructions"]
    assert "governed_external_execution_policy" in payload["policies"]
    assert payload["approval_state"] == "REQUIRES_HUMAN_REVIEW"
    assert "не отправлю сообщение напрямую из чата" in payload["final_response"]
    assert "approve" in payload["final_response"]
    assert payload["governed_action"]["status"] == "pending"
    assert payload["governed_action"]["origin"] == "testbox:runtime-test-asti-orientation"
    assert "ROLE_ASSIGNMENT_SELECTED" in [event["action"] for event in payload["events"]]
    assert "BEHAVIORAL_INSTRUCTIONS_APPLIED" in [event["action"] for event in payload["events"]]
    assert "GOVERNED_ACTION_QUEUED" in [event["action"] for event in payload["events"]]
    assert "APPROVAL_REQUIRED" in [event["action"] for event in payload["events"]]
    assert payload["route"] == "ASTI -> Pending Approval"

    inbox = isolated_client.get("/asti/inbox").json()["actions"]
    assert inbox == [payload["governed_action"]]
    assert [event.event.value for event in audit.list(payload["governed_action"]["id"])] == [
        "created"
    ]


def test_liability_answer_is_localized_in_dutch():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Fietser vraagt schadevergoeding na een aanrijding met mijn auto in Nederland.",
            "user_session": "runtime-test-liability-nl",
            "role": "Legal Assistant",
            "language": "nl",
        },
    )

    payload = response.json()
    assert "Kort antwoord" in payload["final_response"]
    assert "Artikel 185 Wegenverkeerswet 1994" in payload["final_response"]
    assert "Source-bound legal orientation" not in payload["final_response"]


def test_unpaid_salary_answer_uses_specific_dutch_wage_source_and_user_language():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Работодатель не выплатил зарплату. Что делать?",
            "user_session": "runtime-test-unpaid-salary-ru",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    payload = response.json()
    source_ids = [source["id"] for source in payload["sources"]]
    assert payload["classification"]["primary_domain"] == "employment"
    assert "rijksoverheid-wage-payment-delay" in source_ids
    assert "government-minimum-wage-less-than" not in source_ids
    assert "Поскольку страна не указана" in payload["final_response"]
    assert "письменно потребовать выплату задолженности" in payload["final_response"]
    assert "Rijksoverheid указывает" in payload["final_response"]
    assert "RiskLevel." not in payload["final_response"]


def test_user_console_offers_english_language_switch():
    response = surface_client.get("/testbox/user")

    assert response.status_code == 200
    assert '<button id="langEn" type="button">EN</button>' in response.text
    assert 'langEn.addEventListener("click", () => switchLanguage("en"))' in response.text


def test_user_console_opens_with_empty_input_and_clear_resets_composer():
    response = surface_client.get("/testbox/user")

    assert '<textarea id="userInput" aria-label="User message"></textarea>' in response.text
    assert 'userInput.value = "";' in response.text


def test_general_answer_is_available_in_english():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Help me think through a meeting agenda.",
            "user_session": "runtime-test-general-en",
            "role": "Operator",
            "language": "en",
        },
    )

    payload = response.json()
    assert payload["route"] == "Local AI"
    assert "I received your request." in payload["final_response"]


def test_software_company_structure_question_routes_to_official_business_sources():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": (
                "Какую лучше компанию создавать группе специалистов для создания "
                "программного обеспечения и продуктов на его основе, может кооператив?"
            ),
            "user_session": "runtime-test-business-formation",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    payload = response.json()
    source_ids = [source["id"] for source in payload["sources"]]
    assert payload["route"] == "Legal Retrieval -> Governed Draft"
    assert payload["risk_level"] == "medium"
    assert payload["approval_state"] == "SUGGESTED_REVIEW"
    assert "legal_answers_require_sources" in payload["policies"]
    assert "businessgov-choose-legal-structure" in source_ids
    assert "businessgov-private-limited-bv" in source_ids
    assert "businessgov-cooperative" in source_ids
    assert "BV" in payload["final_response"]
    assert "Кооператив" in payload["final_response"]


def test_consulting_legal_form_does_not_substitute_software_template():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "какая организационно правовая форма компании лучше подходит для консалтинга",
            "user_session": "runtime-test-consulting-business-form",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    text = payload["final_response"]
    assert payload["classification"]["primary_domain"] == "consulting_services"
    assert payload["orientation"]["mode"] == "BusinessBox Mode"
    assert "mission_fact_integrity_policy" in payload["policies"]
    assert "policy.mission_fact_integrity" in payload["behavioral_instructions"]["policy_instructions"]
    assert "консалтинговой деятельности" in text
    assert "Что не следует предполагать" in text
    assert "разработке программного обеспечения или владении IP" in text
    assert "Для группы специалистов" not in text
    assert "владение кодом" not in text


def test_consulting_services_start_request_routes_to_businessbox_with_official_sources():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "хочу осуществлять консалтинговые услуги что необходимо",
            "user_session": "runtime-test-consulting-services-start",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    source_ids = [source["id"] for source in payload["sources"]]
    text = payload["final_response"]
    assert payload["classification"]["primary_domain"] == "consulting_services"
    assert payload["orientation"]["intent"] == "business_orientation"
    assert payload["orientation"]["mode"] == "BusinessBox Mode"
    assert payload["orientation"]["route_key"] == "business_orientation"
    assert payload["jurisdiction"] == "Netherlands (candidate)"
    assert payload["classification"]["source_required"] is True
    assert "mission_fact_integrity_policy" in payload["policies"]
    assert "businessgov-start-a-business" in source_ids
    assert "businessgov-professional-indemnity-insurance" in source_ids
    assert "KVK" in text
    assert "Belastingdienst" in text
    assert "BTW" in text
    assert "BAV" in text
    assert "разработке программного обеспечения или владении IP" in text
    assert "Я получил ваш запрос." not in text


def test_zzp_agency_services_contract_gets_business_orientation_and_sources():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "работаю как ззп хочу заключить договор с агенством трудоустройства на оказание им услуг",
            "user_session": "runtime-test-zzp-intermediary-contract",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    source_ids = [source["id"] for source in payload["sources"]]
    normalizations = next(
        event for event in payload["events"] if event["action"] == "TERM_NORMALIZED"
    )["payload"]["normalizations"]
    assert payload["classification"]["primary_domain"] == "zzp_intermediary_contract"
    assert payload["orientation"]["intent"] == "business_orientation"
    assert payload["orientation"]["mode"] == "BusinessBox Mode"
    assert payload["jurisdiction"] == "Netherlands (candidate)"
    assert "mission_fact_integrity_policy" in payload["policies"]
    assert "belastingdienst-intermediair-modelovereenkomst" in source_ids
    assert "businessgov-wet-dba-false-self-employment" in source_ids
    assert {"from": "ззп", "to": "zzp", "rule": "term_normalization"} in normalizations
    assert {"from": "агенством", "to": "агентством", "rule": "typo_correction"} in normalizations
    assert "Bemiddeling" in payload["final_response"]
    assert "Tussenkomst" in payload["final_response"]
    assert "schijnzelfstandigheid" in payload["final_response"]
    assert "не нашел подключенных официальных источников" not in payload["final_response"]


def test_residential_parking_question_routes_to_municipal_orientation():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "хочу оформить парковочное место возле дома куда обращаться",
            "user_session": "runtime-test-residential-parking",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    assert payload["classification"]["primary_domain"] == "residential_parking"
    assert payload["orientation"]["route_key"] == "municipal_parking_orientation"
    assert payload["orientation"]["mode"] == "LegalBox Mode"
    assert "rijksoverheid-municipal-parking-rules" in [source["id"] for source in payload["sources"]]
    assert "gemeente" in payload["final_response"]
    assert "parkeerbeheer" in payload["final_response"]
    assert "без города нельзя определить точную процедуру" in payload["final_response"]
    assert "Я получил ваш запрос" not in payload["final_response"]


def test_residential_parking_action_plan_executes_plan_instead_of_plan_intake():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "хочу оформить парковочное место возле дома куда обращаться план действий",
            "user_session": "runtime-test-residential-parking-plan",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    assert payload["orientation"]["intent"] == "action_plan"
    assert payload["classification"]["primary_domain"] == "residential_parking"
    assert "3. План действий" in payload["final_response"]
    assert "Откройте раздел parkeren/parkeervergunning" in payload["final_response"]
    assert "Опишите цель, текущую ситуацию" not in payload["final_response"]


def test_short_ind_signal_does_not_match_dutch_vind_in_pre_hackathon_title():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Pre-Hackathon: OneGov #2 | Leer de challenges kennen & vind je team",
            "user_session": "runtime-test-onegov-domain",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    assert payload["classification"]["primary_domain"] == "event_collaboration"
    assert "immigration" not in payload["classification"]["domain_candidates"]
    assert payload["orientation"]["mode"] == "Orientation Planning Mode"
    assert payload["orientation"]["route_key"] == "coordination_planning"
    assert "legal_answers_require_sources" not in payload["policies"]
    assert payload["sources"] == []


def test_pre_hackathon_action_plan_produces_team_preparation_instead_of_generic_intake():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "план действий Pre-Hackathon: OneGov #2 | Leer de challenges kennen & vind je team",
            "user_session": "runtime-test-onegov-plan",
            "role": "Operator",
            "language": "ru",
        },
    )

    payload = response.json()
    text = payload["final_response"]
    assert payload["classification"]["primary_domain"] == "event_collaboration"
    assert payload["orientation"]["intent"] == "action_plan"
    assert payload["orientation"]["situation"]["situation_type"] == "pre_hackathon_team_orientation"
    assert payload["route"] == "Orientation -> Coordination Planning"
    assert "План подготовки к Pre-Hackathon: OneGov #2" in text
    assert "самопрезентацию на 30 секунд" in text
    assert "три вопроса к challenges" in text
    assert "ваши 3 навыка" in text
    assert "Начальный план действий" not in text
    assert "официальные источники" not in text


def test_qa_salary_not_paid_phrase_retrieves_sources_and_orients_next_steps():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Работодатель уже месяц не выплачивает зарплату. Что делать?",
            "user_session": "qa-scenario-2-salary",
            "role": "QA",
            "language": "ru",
        },
    )

    payload = response.json()
    actions = {event["action"] for event in payload["events"]}
    assert payload["classification"]["primary_domain"] == "employment"
    assert payload["orientation"]["mode"] == "LegalBox Mode"
    assert "rijksoverheid-wage-payment-delay" in [source["id"] for source in payload["sources"]]
    assert "письменно потребовать выплату задолженности" in payload["final_response"]
    assert "SOURCE_REQUIRED" in actions
    assert "LEGAL_RETRIEVAL_COMPLETED" in actions
    assert "Я получил ваш запрос" not in payload["final_response"]


def test_qa_zero_hours_question_is_explained_with_dutch_sources():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Мне предлагают нулевой контракт. Что это значит?",
            "user_session": "qa-scenario-1-zero-hours",
            "role": "QA",
            "language": "ru",
        },
    )

    payload = response.json()
    assert payload["classification"]["primary_domain"] == "employment_contract"
    assert payload["jurisdiction"] == "Netherlands (candidate)"
    assert payload["orientation"]["mode"] == "LegalBox Mode"
    assert "nulurencontract" in payload["final_response"]
    assert "legal_answers_require_sources" in payload["policies"]
    assert "TERM_NORMALIZED" in [event["action"] for event in payload["events"]]


def test_qa_social_housing_with_yo_routes_to_social_housing_sources():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Могу ли я получить социальное жильё в Нидерландах?",
            "user_session": "qa-scenario-3-housing",
            "role": "QA",
            "language": "ru",
        },
    )

    payload = response.json()
    assert payload["classification"]["primary_domain"] == "social_housing"
    assert payload["jurisdiction"] == "Netherlands"
    assert payload["orientation"]["mode"] == "LegalBox Mode"
    assert "woningcorporatie" in payload["final_response"]
    assert "TERM_NORMALIZED" in [event["action"] for event in payload["events"]]


def test_qa_developer_group_comparison_does_not_claim_existing_software_ip():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Какую форму компании лучше выбрать группе разработчиков: BV или кооператив?",
            "user_session": "qa-scenario-4-business",
            "role": "QA",
            "language": "ru",
        },
    )

    payload = response.json()
    text = payload["final_response"]
    assert payload["orientation"]["mode"] == "BusinessBox Mode"
    assert "mission_fact_integrity_policy" in payload["policies"]
    assert "группы разработчиков" in text
    assert "наличие общего IP ещё не следует" in text
    assert "создающей программное обеспечение и продуктовый IP" not in text


def test_qa_energy_production_enters_regulated_business_orientation():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Хочу открыть производство накопителей энергии",
            "user_session": "qa-scenario-5-energy",
            "role": "QA",
            "language": "ru",
        },
    )

    payload = response.json()
    domains = set(payload["orientation"]["domain_graph"])
    assert payload["orientation"]["intent"] == "regulated_business_creation"
    assert payload["orientation"]["route_key"] == "regulated_manufacturing"
    assert payload["orientation"]["mode"] == "Human Review Mode"
    assert {"business_formation", "battery_manufacturing", "energy_storage"}.issubset(domains)
    assert "Регламент ЕС 2023/1542" in payload["final_response"]
    assert "экологические разрешения" in payload["final_response"].casefold()


def test_qa_cyclist_claim_without_vehicle_fact_exposes_article_185_boundary():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "В меня врезался велосипедист в Нидерландах и требует компенсацию",
            "user_session": "qa-scenario-6-traffic",
            "role": "QA",
            "language": "ru",
        },
    )

    payload = response.json()
    text = payload["final_response"]
    assert payload["classification"]["primary_domain"] == "liability"
    assert "wetten-wvw-article-185" in [source["id"] for source in payload["sources"]]
    assert "не указали, были ли вы в автомобиле" in text
    assert "относится к ДТП с моторным транспортным средством" in text
    assert "Если ДТП произошло" not in text


def test_qa_document_risk_request_performs_active_analysis():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Проверь договор и найди риски",
            "document_text": (
                "CONTRACT: Service Agreement. Customer: Delta BV. Contractor: I. Ivanov. "
                "Amount EUR 1,250. Payment due 14 January 2025. Termination notice 30 days."
            ),
            "attachment_names": ["contract_DY1401250033.pdf"],
            "user_session": "qa-scenario-7-document",
            "role": "QA",
            "language": "ru",
        },
    )

    payload = response.json()
    actions = {event["action"] for event in payload["events"]}
    assert payload["orientation"]["mode"] == "DocumentBox Mode"
    assert "active_task_execution_policy" in payload["policies"]
    assert "ACTIVE_TASK_ANALYSIS_ATTEMPTED" in actions
    assert "Найдена сумма: EUR 1,250" in payload["final_response"]
    assert "Найден срок оплаты: 14 January 2025" in payload["final_response"]
    assert "Ограничения анализа" in payload["final_response"]


def test_qa_letter_request_generates_active_unpaid_salary_draft():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Подготовь письмо работодателю о невыплате зарплаты",
            "user_session": "qa-scenario-8-letter",
            "role": "QA",
            "language": "ru",
        },
    )

    payload = response.json()
    text = payload["final_response"]
    assert payload["orientation"]["intent"] == "letter_draft"
    assert payload["orientation"]["mode"] == "LetterBox Mode"
    assert payload["orientation"]["route_key"] == "letter_preparation"
    assert payload["route"] == "LetterBox -> Draft Generation"
    assert "active_task_execution_policy" in payload["policies"]
    assert "ACTIVE_TASK_EXECUTION_ATTEMPTED" in [event["action"] for event in payload["events"]]
    assert "Требование о выплате задолженности по заработной плате" in text
    assert "Уважаемый(ая) [имя работодателя/HR]" in text
    assert "Чтобы написать готовый текст" not in text


def test_qa_letter_follow_up_reuses_topic_instead_of_generic_fallback():
    session = "qa-scenario-9-follow-up"
    client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Подготовь письмо работодателю о невыплате зарплаты",
            "user_session": session,
            "role": "QA",
            "language": "ru",
        },
    )
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Объясни подробнее",
            "user_session": session,
            "role": "QA",
            "language": "ru",
        },
    )

    payload = response.json()
    actions = {event["action"] for event in payload["events"]}
    assert payload["orientation"]["mode"] == "LetterBox Mode"
    assert payload["route"] == "LetterBox -> Draft Generation"
    assert "CONTEXT_REUSED" in actions
    assert "FOLLOW_UP_RESOLVED" in actions
    assert "context_continuity_policy" in payload["policies"]
    assert "Требование о выплате задолженности" in payload["final_response"]
    assert "Я получил ваш запрос" not in payload["final_response"]


def test_qa_telegram_phrase_queues_pending_action_without_execution(tmp_path):
    audit = AstiAuditLog(tmp_path / "asti-qa-audit.jsonl")
    service = AstiService(ActionQueue(tmp_path / "asti-qa-actions.json"), audit)
    isolated_app = FastAPI()
    isolated_app.include_router(create_testbox_router(tmp_path, service))
    isolated_app.include_router(create_asti_router(tmp_path, service))
    isolated_client = TestClient(isolated_app, headers=ADMIN_HEADERS)

    response = isolated_client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Отправь это сообщение через Telegram",
            "user_session": "qa-scenario-10-asti",
            "role": "QA",
            "language": "ru",
        },
    )

    payload = response.json()
    action = payload["governed_action"]
    assert payload["orientation"]["mode"] == "ASTI Action Mode"
    assert payload["orientation"]["route_key"] == "asti_action_queue"
    assert payload["approval_state"] == "REQUIRES_HUMAN_REVIEW"
    assert "governed_external_execution_policy" in payload["policies"]
    assert "governance_balance_policy" in payload["policies"]
    assert action["status"] == "pending"
    assert action["execution_metadata"] is None
    assert "GOVERNED_ACTION_QUEUED" in [event["action"] for event in payload["events"]]
    assert "APPROVAL_REQUIRED" in [event["action"] for event in payload["events"]]
    assert [event.event.value for event in audit.list(action["id"])] == ["created"]


def test_ambiguous_regulated_request_never_falls_back_to_general_chat():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Какие у меня обязанности перед клиентом и поставщиком?",
            "user_session": "runtime-test-regulated-guard",
            "role": "Governance Officer",
            "language": "ru",
        },
    )

    payload = response.json()
    actions = [event["action"] for event in payload["events"]]
    assert payload["classification"]["primary_domain"] == "regulated_domain_candidate"
    assert payload["classification"]["classification_mode"] == "multi_domain"
    assert payload["classification"]["confidence"] < 0.75
    assert payload["classification"]["source_required"] is True
    assert payload["route"] == "Source Clarification -> Governed Draft -> Human Review"
    assert payload["approval_state"] == "REQUIRES_HUMAN_REVIEW"
    assert "legal_answers_require_sources" in payload["policies"]
    assert "CLASSIFICATION_UNCERTAIN" in actions
    assert "Реестр источников требует расширения" in payload["final_response"]


def test_multi_domain_request_logs_uncertainty_and_missing_source_coverage():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Нужны BV или кооператив и какие налоги будут у компании?",
            "user_session": "runtime-test-multi-domain",
            "role": "Governance Officer",
            "language": "ru",
        },
    )

    payload = response.json()
    classification = payload["classification"]
    retrieval_event = next(
        event for event in payload["events"]
        if event["action"] == "LEGAL_RETRIEVAL_COMPLETED"
    )
    assert classification["classification_mode"] == "multi_domain"
    assert "business_formation" in classification["domain_candidates"]
    assert "tax" in classification["domain_candidates"]
    assert payload["approval_state"] == "REQUIRES_HUMAN_REVIEW"
    assert "tax" in retrieval_event["payload"]["missing_source_domains"]
    assert "Внимание: запрос затрагивает несколько регулируемых областей" in payload["final_response"]


def test_tbx_bus_energy_001_governed_energy_storage_business_orientation():
    """Acceptance case TBX-BUS-ENERGY-001: governed business orientation."""
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": TBX_BUS_ENERGY_001_INPUT,
            "user_session": "TBX-BUS-ENERGY-001",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    payload = response.json()
    source_ids = [source["id"] for source in payload["sources"]]
    retrieval_event = next(
        event for event in payload["events"]
        if event["action"] == "LEGAL_RETRIEVAL_COMPLETED"
    )
    intent_event = next(
        event for event in payload["events"]
        if event["action"] == "INTENT_DETECTED"
    )
    source_required_event = next(
        event for event in payload["events"]
        if event["action"] == "SOURCE_REQUIRED"
    )
    routing_event = next(
        event for event in payload["events"]
        if event["action"] == "ROUTING_SELECTED"
    )
    review_event = next(
        event for event in payload["events"]
        if event["action"] == "HUMAN_REVIEW_REQUIRED"
    )
    assert payload["classification"]["classification_mode"] == "multi_domain"
    assert payload["classification"]["primary_domain"] != "general"
    assert "business_formation" in payload["classification"]["domain_candidates"]
    assert "battery_manufacturing" in payload["classification"]["domain_candidates"]
    assert payload["jurisdiction"] == "Netherlands (candidate)"
    assert payload["classification"]["source_required"] is True
    assert payload["route"] == "Legal Retrieval -> Governed Draft -> Human Review"
    assert payload["approval_state"] == "REQUIRES_HUMAN_REVIEW"
    assert "eurlex-batteries-regulation-2023-1542" in source_ids
    assert "businessgov-battery-producer-responsibility" in source_ids
    assert "businessgov-environment-harmful-activities-permit" in source_ids
    assert retrieval_event["payload"]["missing_source_domains"] == []
    assert intent_event["payload"]["intent"] == "regulated_business_creation"
    assert {"business_formation", "battery_manufacturing", "energy_storage"}.issubset(
        set(intent_event["payload"]["domains"])
    )
    assert payload["orientation"]["route_key"] == "regulated_manufacturing"
    assert (
        payload["orientation"]["situation"]["situation_type"]
        == "regulated_energy_storage_manufacturing_launch"
    )
    assert payload["runtime_roles"]["primary_role"] == "BusinessBox Strategist"
    assert "Governance Officer" in payload["runtime_roles"]["active_roles"]
    assert source_required_event["payload"]["sources_required"] is True
    assert routing_event["route"] == "Legal Retrieval -> Governed Draft -> Human Review"
    assert (
        review_event["payload"]["human_review_reason"]
        == "regulated_energy_storage_manufacturing_requires_specialist_review"
    )
    assert review_event["route"] == payload["route"]
    assert "регистрац" in payload["final_response"].casefold()
    assert "производств" in payload["final_response"].casefold()
    assert "регламент ес 2023/1542" in payload["final_response"].casefold()
    assert "экологическ" in payload["final_response"].casefold()
    assert "ответственность производителя" in payload["final_response"].casefold()
    assert "рынка ес" in payload["final_response"].casefold()
    assert "RiskLevel." not in payload["final_response"]
    assert "REQUIRES_HUMAN_REVIEW" not in payload["final_response"]
    assert "contracts" not in payload["final_response"]


def test_tbx_hou_social_001_routes_social_rental_eligibility_to_official_sources():
    """Acceptance case TBX-HOU-SOCIAL-001: NL social housing eligibility."""
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": TBX_HOU_SOCIAL_001_INPUT,
            "user_session": "TBX-HOU-SOCIAL-001",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    payload = response.json()
    source_ids = [source["id"] for source in payload["sources"]]
    intent_event = next(
        event for event in payload["events"]
        if event["action"] == "INTENT_DETECTED"
    )
    source_event = next(
        event for event in payload["events"]
        if event["action"] == "SOURCE_REQUIRED"
    )
    jurisdiction_event = next(
        event for event in payload["events"]
        if event["action"] == "JURISDICTION_DETECTED"
    )
    assert payload["classification"]["primary_domain"] == "social_housing"
    assert payload["classification"]["primary_domain"] != "general"
    assert payload["jurisdiction"] == "Netherlands (candidate)"
    assert payload["classification"]["source_required"] is True
    assert intent_event["payload"]["intent"] == "legal_orientation"
    assert source_event["payload"]["sources_required"] is True
    assert jurisdiction_event["payload"]["jurisdiction_basis"] == "nl_eu_official_source_registry"
    assert "rijksoverheid-social-housing-eligibility" in source_ids
    assert "rijksoverheid-social-housing-urgency" in source_ids
    assert "woningcorporatie" in payload["final_response"]
    assert "€51 537" in payload["final_response"]
    assert "€56 910" in payload["final_response"]
    assert "€932,93" in payload["final_response"]
    assert "urgentieverklaring" in payload["final_response"]
    assert "RiskLevel." not in payload["final_response"]
    assert "business_formation" not in payload["final_response"]
    assert "contracts" not in payload["final_response"]


def test_tbx_emp_zerohours_001_recognises_zero_hours_contract_and_sources():
    """Acceptance case TBX-EMP-ZEROHOURS-001: Dutch nulurencontract orientation."""
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": TBX_EMP_ZEROHOURS_001_INPUT,
            "user_session": "TBX-EMP-ZEROHOURS-001",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    payload = response.json()
    source_ids = [source["id"] for source in payload["sources"]]
    intent_event = next(
        event for event in payload["events"]
        if event["action"] == "INTENT_DETECTED"
    )
    normalized_event = next(
        event for event in payload["events"]
        if event["action"] == "TERM_NORMALIZED"
    )
    jurisdiction_event = next(
        event for event in payload["events"]
        if event["action"] == "JURISDICTION_INFERRED"
    )
    assert payload["classification"]["primary_domain"] == "employment_contract"
    assert payload["jurisdiction"] == "Netherlands (candidate)"
    assert intent_event["payload"]["intent"] == "explanation"
    assert payload["orientation"]["mode"] == "LegalBox Mode"
    assert payload["runtime_roles"]["primary_role"] == "LegalBox Specialist"
    assert "skill.legal_retrieval" in payload["behavioral_instructions"]["skill_instructions"]
    assert "policy.source_governance" in payload["behavioral_instructions"]["policy_instructions"]
    assert "policy.human_review" in payload["behavioral_instructions"]["policy_instructions"]
    assert payload["classification"]["source_required"] is True
    assert {"from": "предлогают", "to": "предлагают", "rule": "typo_correction"} in normalized_event["payload"]["normalizations"]
    assert {"from": "нулевой контракт", "to": "nulurencontract", "rule": "regulated_term"} in normalized_event["payload"]["normalizations"]
    assert jurisdiction_event["payload"]["jurisdiction"] == "Netherlands (candidate)"
    assert "rijksoverheid-on-call-contract-types" in source_ids
    assert "rijksoverheid-zero-hours-holiday-pay" in source_ids
    assert "businessgov-zero-hours-contract" in source_ids
    assert "nulurencontract" in payload["final_response"]
    assert "4 дня" in payload["final_response"]
    assert "3 часа" in payload["final_response"]
    assert "12 месяцев" in payload["final_response"]
    assert "8%" in payload["final_response"]
    assert "RiskLevel." not in payload["final_response"]
    assert payload["orientation"]["situation"]["situation_type"] == "variable_hours_employment_offer"
    assert "income stability" in payload["orientation"]["situation"]["operational_concerns"]
    assert "SITUATION_MODEL_CREATED" in [event["action"] for event in payload["events"]]


def test_tbx_emp_zerohours_002_short_follow_up_reuses_previous_conversation_topic():
    """Acceptance case TBX-EMP-ZEROHOURS-002: terse follow-up keeps governed context."""
    first_response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": TBX_EMP_ZEROHOURS_001_INPUT,
            "user_session": "TBX-EMP-ZEROHOURS-002",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )
    assert first_response.status_code == 200
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "обьясни",
            "user_session": "TBX-EMP-ZEROHOURS-002",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    payload = response.json()
    context_event = next(
        event for event in payload["events"]
        if event["action"] == "CONTEXT_REUSED"
    )
    follow_up_event = next(
        event for event in payload["events"]
        if event["action"] == "FOLLOW_UP_RESOLVED"
    )
    assert payload["classification"]["primary_domain"] == "employment_contract"
    assert payload["classification"]["primary_domain"] != "general"
    assert context_event["payload"]["context_source"] == "previous_user_message"
    assert context_event["payload"]["follow_up"] == "обьясни"
    assert follow_up_event["payload"]["domain"] == "employment_contract"
    assert follow_up_event["payload"]["intent"] == "explanation"
    assert "skill.context_reuse" in payload["behavioral_instructions"]["skill_instructions"]
    assert "nulurencontract" in payload["final_response"]
    assert "Я получил ваш запрос" not in payload["final_response"]


def test_persistent_orientation_memory_reuses_topic_after_runtime_restart(tmp_path):
    service = AstiService(ActionQueue(tmp_path / "asti-actions.json"), AstiAuditLog(tmp_path / "asti-audit.jsonl"))
    first_app = FastAPI()
    first_app.include_router(create_testbox_router(tmp_path, service))
    first_client = TestClient(first_app, headers=ADMIN_HEADERS)
    first_client.post(
        "/api/testbox/runtime/message",
        json={
            "message": TBX_EMP_ZEROHOURS_001_INPUT,
            "user_session": "persistent-follow-up",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    second_app = FastAPI()
    second_app.include_router(create_testbox_router(tmp_path, service))
    response = TestClient(second_app, headers=ADMIN_HEADERS).post(
        "/api/testbox/runtime/message",
        json={
            "message": "а дальше?",
            "user_session": "persistent-follow-up",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    payload = response.json()
    saved = json.loads((tmp_path / "audit" / "testbox_session_context.json").read_text(encoding="utf-8"))
    assert payload["classification"]["primary_domain"] == "employment_contract"
    assert "CONTEXT_REUSED" in [event["action"] for event in payload["events"]]
    assert payload["orientation"]["situation"]["situation_type"] == "variable_hours_employment_offer"
    assert saved["persistent-follow-up"]["active_task"] == "explanation"
    assert saved["persistent-follow-up"]["mode"] == "LegalBox Mode"


def test_persistent_orientation_memory_redacts_obvious_pii(tmp_path):
    service = AstiService(ActionQueue(tmp_path / "asti-actions.json"), AstiAuditLog(tmp_path / "asti-audit.jsonl"))
    isolated_app = FastAPI()
    isolated_app.include_router(create_testbox_router(tmp_path, service))
    TestClient(isolated_app, headers=ADMIN_HEADERS).post(
        "/api/testbox/runtime/message",
        json={
            "message": "мне предлагают нулевой контракт, email person@example.com, телефон +31 612345678",
            "user_session": "persistent-pii",
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    stored = (tmp_path / "audit" / "testbox_session_context.json").read_text(encoding="utf-8")
    assert "person@example.com" not in stored
    assert "+31 612345678" not in stored
    assert "[EMAIL]" in stored
    assert "[PHONE_OR_IDENTIFIER]" in stored


def test_runtime_asti_transition_events_preserve_approval_boundary(tmp_path, monkeypatch):
    monkeypatch.setenv("ASTI_EXTERNAL_EXECUTION_ENABLED", "true")
    service = AstiService(
        ActionQueue(tmp_path / "asti-actions.json"),
        AstiAuditLog(tmp_path / "asti-audit.jsonl"),
        executors={ExecutorType.TELEGRAM: NoOpExecutor()},
    )
    isolated_app = FastAPI()
    isolated_app.include_router(create_testbox_router(tmp_path, service))
    isolated_client = TestClient(isolated_app, headers=ADMIN_HEADERS)
    created = isolated_client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Отправь это сообщение через Telegram",
            "user_session": "asti-runtime-transitions",
            "role": "Operator",
            "language": "ru",
        },
    ).json()
    action_id = created["governed_action"]["id"]

    unauthorized = TestClient(isolated_app).post(
        f"/api/testbox/runtime/actions/{action_id}/approve",
        json={"user_session": "asti-runtime-transitions", "role": "Governance Officer"},
    )
    assert unauthorized.status_code == 401
    blocked = isolated_client.post(
        f"/api/testbox/runtime/actions/{action_id}/execute",
        json={"user_session": "asti-runtime-transitions", "role": "Governance Officer"},
    )
    assert blocked.status_code == 409
    approved = isolated_client.post(
        f"/api/testbox/runtime/actions/{action_id}/approve",
        json={"user_session": "asti-runtime-transitions", "role": "Governance Officer"},
    )
    executed = isolated_client.post(
        f"/api/testbox/runtime/actions/{action_id}/execute",
        json={"user_session": "asti-runtime-transitions", "role": "Governance Officer"},
    )
    actions = [
        event["action"]
        for event in isolated_client.get(
            "/api/testbox/runtime/events",
            params={"user_session": "asti-runtime-transitions"},
        ).json()["events"]
    ]
    assert approved.json()["action"]["status"] == "approved"
    assert executed.json()["action"]["status"] == "executed"
    assert "APPROVAL_REQUIRED" in actions
    assert "APPROVED" in actions
    assert "APPROVAL_GRANTED" in actions
    assert "EXECUTION_STARTED" in actions
    assert "EXECUTED" in actions

    rejected_created = isolated_client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Отправь это сообщение через Telegram",
            "user_session": "asti-runtime-rejected",
            "role": "Operator",
            "language": "ru",
        },
    ).json()
    rejected_id = rejected_created["governed_action"]["id"]
    rejected = isolated_client.post(
        f"/api/testbox/runtime/actions/{rejected_id}/reject",
        json={"user_session": "asti-runtime-rejected", "role": "Governance Officer"},
    )
    rejected_actions = [
        event["action"]
        for event in isolated_client.get(
            "/api/testbox/runtime/events",
            params={"user_session": "asti-runtime-rejected"},
        ).json()["events"]
    ]
    assert rejected.json()["action"]["status"] == "rejected"
    assert "REJECTED" in rejected_actions


def test_tbx_bus_coop_ua_001_focused_follow_up_does_not_repeat_general_structure_answer():
    """Acceptance case TBX-BUS-COOP-UA-001: focused cooperative UA explanation."""
    session_id = "TBX-BUS-COOP-UA-001"
    broad_response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": TBX_BUS_ENERGY_001_INPUT,
            "user_session": session_id,
            "role": "Legal Assistant",
            "language": "ru",
        },
    )
    focused_response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "cooperatie UA обьясни более подробно",
            "user_session": session_id,
            "role": "Legal Assistant",
            "language": "ru",
        },
    )

    broad_payload = broad_response.json()
    payload = focused_response.json()
    source_ids = [source["id"] for source in payload["sources"]]
    intent_event = next(
        event for event in payload["events"]
        if event["action"] == "INTENT_DETECTED"
    )
    normalized_event = next(
        event for event in payload["events"]
        if event["action"] == "TERM_NORMALIZED"
    )
    assert payload["classification"]["primary_domain"] == "business_formation"
    assert payload["jurisdiction"] == "Netherlands (candidate)"
    assert intent_event["payload"]["intent"] == "explanation"
    assert intent_event["payload"]["strategy"] == "explain_cooperative_ua"
    assert "businessgov-cooperative" in source_ids
    assert "businessgov-private-limited-bv" not in source_ids
    assert "cooperatie UA" in normalized_event["payload"]["normalized_text"]
    assert "Uitgesloten van Aansprakelijkheid" in payload["final_response"]
    assert "`UA` - ответственность участников исключена" in payload["final_response"]
    assert "`BA` - ответственность участников ограничена" in payload["final_response"]
    assert "`WA` - участники несут" in payload["final_response"]
    assert "ответственность директора" in payload["final_response"]
    assert payload["final_response"] != broad_payload["final_response"]
    assert "RiskLevel." not in payload["final_response"]


def test_lqa_follow_up_risk_question_reuses_zero_hours_context():
    session = "LQA-CONTEXT-RISK-001"
    client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Мне предлагают нулевой контракт. Объясни простыми словами, стоит ли соглашаться.",
            "user_session": session,
            "role": "QA",
            "language": "ru",
        },
    )
    response = client.post(
        "/api/testbox/runtime/message",
        json={"message": "А какие риски для меня?", "user_session": session, "role": "QA", "language": "ru"},
    )
    payload = response.json()
    actions = {event["action"] for event in payload["events"]}
    assert payload["classification"]["primary_domain"] == "employment_contract"
    assert payload["orientation"]["mode"] == "LegalBox Mode"
    assert "CONTEXT_REUSED" in actions
    assert "FOLLOW_UP_RESOLVED" in actions
    assert "nulurencontract" in payload["final_response"]
    assert "Я получил ваш запрос" not in payload["final_response"]


def test_lqa_salary_delay_letter_generates_draft_with_official_source():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Работодатель задерживает зарплату уже 3 недели, подготовь письмо.",
            "user_session": "LQA-SALARY-LETTER-001",
            "role": "QA",
            "language": "ru",
        },
    )
    payload = response.json()
    assert payload["orientation"]["mode"] == "LetterBox Mode"
    assert "rijksoverheid-wage-payment-delay" in [source["id"] for source in payload["sources"]]
    assert "Требование о выплате задолженности" in payload["final_response"]
    assert "Официальная опора для проверки" in payload["final_response"]


def test_lqa_contract_review_request_executes_documentbox_analysis():
    text = (
        "SERVICE CONTRACT. Client: Delta BV. Contractor: Ivan Petrov. "
        "Fee EUR 2,500. Payment due 30 days after invoice. "
        "Termination notice: 60 days. Penalty: 5% late fee."
    )
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Проверь договор и найди рискованные пункты.",
            "document_text": text,
            "attachment_names": ["service-contract.pdf"],
            "user_session": "LQA-DOCUMENT-001",
            "role": "QA",
            "language": "ru",
        },
    )
    payload = response.json()
    assert payload["orientation"]["mode"] == "DocumentBox Mode"
    assert payload["route"] == "DocumentBox -> Analysis Attempt"
    assert "ACTIVE_TASK_ANALYSIS_ATTEMPTED" in [event["action"] for event in payload["events"]]
    assert "Найдена сумма: EUR 2,500" in payload["final_response"]
    assert "Penalty: 5% late fee" in payload["final_response"]

    follow_up = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Теперь найди только сроки и оплату.",
            "document_text": text,
            "attachment_names": ["service-contract.pdf"],
            "user_session": "LQA-DOCUMENT-001",
            "role": "QA",
            "language": "ru",
        },
    ).json()
    assert follow_up["orientation"]["mode"] == "DocumentBox Mode"
    assert "CONTEXT_REUSED" in [event["action"] for event in follow_up["events"]]
    assert "Фокус анализа: только сроки и оплата" in follow_up["final_response"]
    assert "Найдена сумма: EUR 2,500" in follow_up["final_response"]
    assert "Указано применимое право" not in follow_up["final_response"]


def test_lqa_commercial_battery_production_correlates_business_and_regulated_domains():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Хочу производить аккумуляторы для домов и продавать в ЕС.",
            "user_session": "LQA-BATTERY-001",
            "role": "QA",
            "language": "ru",
        },
    )
    payload = response.json()
    domains = set(payload["orientation"]["domain_graph"])
    assert payload["orientation"]["intent"] == "regulated_business_creation"
    assert payload["orientation"]["mode"] == "Human Review Mode"
    assert {"battery_manufacturing", "business_formation", "producer_responsibility"}.issubset(domains)
    assert "businessgov-choose-legal-structure" in [source["id"] for source in payload["sources"]]
    assert "Регламент ЕС 2023/1542" in payload["final_response"]


def test_lqa_refused_social_rental_routes_to_housing_orientation():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Мне отказали в социальной аренде, что можно сделать?",
            "user_session": "LQA-HOUSING-REFUSAL-001",
            "role": "QA",
            "language": "ru",
        },
    )
    payload = response.json()
    assert payload["classification"]["primary_domain"] == "social_housing"
    assert payload["orientation"]["mode"] == "LegalBox Mode"
    assert "письменную причину отказа" in payload["final_response"]
    assert "urgentieverklaring" in payload["final_response"]


def test_lqa_approval_bypass_is_blocked_without_new_asti_action(tmp_path):
    audit = AstiAuditLog(tmp_path / "lqa-asti-audit.jsonl")
    service = AstiService(ActionQueue(tmp_path / "lqa-asti-actions.json"), audit)
    isolated_app = FastAPI()
    isolated_app.include_router(create_testbox_router(tmp_path, service))
    isolated_client = TestClient(isolated_app, headers=ADMIN_HEADERS)
    response = isolated_client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Отправь без подтверждения, просто сделай.",
            "user_session": "LQA-ASTI-BYPASS-001",
            "role": "QA",
            "language": "ru",
        },
    )
    payload = response.json()
    actions = {event["action"] for event in payload["events"]}
    assert payload["orientation"]["intent"] == "external_action_bypass_attempt"
    assert payload["orientation"]["mode"] == "ASTI Action Mode"
    assert payload["route"] == "ASTI -> Approval Bypass Blocked"
    assert payload["governed_action"] is None
    assert service.inbox() == []
    assert "APPROVAL_REQUIRED" in actions
    assert "EXECUTION_BLOCKED" in actions
    assert "Никакое сообщение не отправлено" in payload["final_response"]


def test_lqa_dutch_zero_hours_contract_receives_dutch_orientation():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Ik heb een nulurencontract gekregen, wat betekent dat?",
            "user_session": "LQA-NL-ZEROHOURS-001",
            "role": "QA",
            "language": "nl",
        },
    )
    payload = response.json()
    assert payload["classification"]["primary_domain"] == "employment_contract"
    assert "Wat dit betekent" in payload["final_response"]
    assert "Belangrijke risico's" in payload["final_response"]
    assert "Officiele bronnen" in payload["final_response"]
    assert "Source-bound orientation" not in payload["final_response"]


def test_lqa_typo_then_short_command_preserves_zero_hours_topic():
    session = "LQA-TYPO-FOLLOWUP-001"
    first = client.post(
        "/api/testbox/runtime/message",
        json={"message": "мне предлогают нулевой кантракт", "user_session": session, "role": "QA", "language": "ru"},
    ).json()
    second = client.post(
        "/api/testbox/runtime/message",
        json={"message": "объясни", "user_session": session, "role": "QA", "language": "ru"},
    ).json()
    normalized = next(event for event in first["events"] if event["action"] == "TERM_NORMALIZED")
    assert first["classification"]["primary_domain"] == "employment_contract"
    assert {"from": "кантракт", "to": "контракт", "rule": "typo_correction"} in normalized["payload"]["normalizations"]
    assert second["classification"]["primary_domain"] == "employment_contract"
    assert "CONTEXT_REUSED" in [event["action"] for event in second["events"]]


def test_lqa_ambiguous_contract_inspection_enters_documentbox_without_faking_analysis():
    response = client.post(
        "/api/testbox/runtime/message",
        json={
            "message": "Мне дали странный контракт, посмотри.",
            "user_session": "LQA-AMBIGUOUS-CONTRACT-001",
            "role": "QA",
            "language": "ru",
        },
    )
    payload = response.json()
    assert payload["orientation"]["mode"] == "DocumentBox Mode"
    assert payload["route"] == "DocumentBox -> Analysis Attempt"
    assert "документ или извлечённый текст не передан" in payload["final_response"]
    assert "LIMITATION_REPORTED" in [event["action"] for event in payload["events"]]
