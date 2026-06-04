from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_jazekker_public_pages_are_available():
    for path in ("/jazekker", "/jazekker/news", "/jazekker/workspace", "/jazekker/public-news", "/jazekker/articles"):
        response = client.get(path)

        assert response.status_code == 200


def test_testbox_governance_console_is_available():
    response = client.get("/testbox")

    assert response.status_code == 200
    assert "TESTBOX COCKPIT" in response.text
    assert "AI Operations & Governance Console" in response.text
    assert "Static Layer" in response.text
    assert "Dynamic Layer" in response.text
    assert "Observation Layer" in response.text
    assert "Legal AI Governance Scenario" in response.text
    assert "PII Masking" in response.text
    assert "Human-In-The-Loop Control" in response.text
    assert "TESTBOX Administrator" in response.text
    assert "AI Cabinet remains the static governance architecture" in response.text


def test_testbox_operational_routes_share_the_cockpit_shell():
    for path in (
        "/testbox/cockpit",
        "/testbox/orchestration",
        "/testbox/legal",
        "/testbox/legal-demo",
        "/testbox/audit",
        "/testbox/routing",
        "/testbox/memory",
        "/testbox/settings",
        "/testbox/training",
        "/testbox/hackathon",
    ):
        response = client.get(path)

        assert response.status_code == 200
        assert "TESTBOX COCKPIT" in response.text
        assert "TESTBOX routes" in response.text


def test_jazekker_public_pages_hide_internal_controls():
    for path in ("/jazekker", "/jazekker/news"):
        response = client.get(path)

        assert response.status_code == 200
        assert "/jazekker/news/collect" not in response.text
        assert "X-AI-Cabinet-Admin-Token" not in response.text


def test_foundation_mvp_routes_are_available():
    for path in (
        "/jazekker/orientation",
        "/jazekker/local",
        "/jazekker/research",
        "/jazekker/ai-cabinet",
        "/jazekker/testbox",
        "/jazekker/co-creation",
    ):
        response = client.get(path)

        assert response.status_code == 200


def test_foundation_home_positions_orientation_infrastructure():
    homepage_html = client.get("/jazekker").text

    assert "Navigate complexity calmly." in homepage_html
    assert "AI-native orientation infrastructure" in homepage_html
    for step in ("Noise", "Signal", "Context", "Orientation", "Trust"):
        assert step in homepage_html


def test_orientation_stream_exposes_calm_feed_modes():
    stream_html = client.get("/jazekker/orientation").text

    assert "Global Orientation Stream" in stream_html
    assert "orientationSearch" in stream_html
    for mode in ("Calm", "Standard", "Professional", "Research", "Strategic"):
        assert mode in stream_html


def test_foundation_surfaces_connect_governance_and_coordination():
    cabinet_html = client.get("/jazekker/ai-cabinet").text
    testbox_html = client.get("/jazekker/testbox").text
    coordination_html = client.get("/jazekker/co-creation").text

    assert "Governed intelligence, not a chatbot" in cabinet_html
    assert "Human Approval" in cabinet_html
    assert "Observe AI governance in motion" in testbox_html
    assert "/testbox" in testbox_html
    assert "Not a social network" in coordination_html


def test_foundation_static_runtime_includes_functional_controls():
    runtime_js = client.get("/static/foundation.js?v=foundation-3").text
    research_html = client.get("/jazekker/research").text

    assert "safeText" in runtime_js
    assert "save-signal" in runtime_js
    assert "view\") === \"contradictions\"" in runtime_js
    assert "jazekker-research-preview.txt" in runtime_js
    assert 'id="exportPreview"' in research_html


def test_testbox_preview_exposes_governed_living_evolution_mode():
    preview_html = client.get("/jazekker/testbox").text
    runtime_js = client.get("/static/foundation.js?v=foundation-3").text

    assert "ASTREB META-QMS" in preview_html
    assert "Living Evolution Mode" in preview_html
    assert 'id="runMetaQmsReview"' in preview_html
    assert "No proposed change applies itself." in preview_html
    assert "/api/testbox/runtime/meta-qms/assess" in runtime_js


def test_jazekker_articles_api_exposes_launch_metadata():
    response = client.get("/jazekker/articles")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 8
    assert payload["categories"]
    assert all("url" in article for article in payload["articles"])
    assert all("orientation_score" in article for article in payload["articles"])


def test_news_feed_prioritizes_clarity_for_decisions():
    news_html = client.get("/jazekker/public-news").text

    assert 'let sortMode = "orientation";' in news_html
    assert "clarityDecisionScore" in news_html
    assert "Ясность решений" in news_html
    assert "clickability" not in news_html.lower()


def test_workspace_combines_editorial_tabs():
    workspace_html = client.get("/jazekker/workspace").text

    assert "Кабинет главного редактора" in workspace_html
    assert "AI-workflows" in workspace_html
    assert "черновики" in workspace_html
    assert "Автономия недопустима" in workspace_html
    assert "Дизайн-мышление" in workspace_html
    assert "Журнал решений" in workspace_html
    assert "/jazekker/articles" in workspace_html


def test_root_redirects_to_news_portal_homepage():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/jazekker"


def test_jazekker_article_uses_reader_facing_language():
    response = client.get("/jazekker/articles/ai-coordination-control-before-autonomy")

    assert response.status_code == 200
    assert "Фокус материала:" in response.text
    assert "Orientation lens:" not in response.text
    assert "Р¤" not in response.text
