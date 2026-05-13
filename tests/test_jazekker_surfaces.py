from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_jazekker_public_pages_are_available():
    for path in ("/jazekker", "/jazekker/news", "/jazekker/articles"):
        response = client.get(path)

        assert response.status_code == 200


def test_jazekker_article_uses_reader_facing_language():
    response = client.get("/jazekker/articles/ai-coordination-control-before-autonomy")

    assert response.status_code == 200
    assert "Фокус материала:" in response.text
    assert "Orientation lens:" not in response.text


def test_editorial_apis_require_admin_token():
    for path in ("/jazekker/orientation-objects", "/jazekker/news/sources"):
        response = client.get(path)

        assert response.status_code == 403


def test_editorial_apis_accept_admin_token():
    response = client.get(
        "/jazekker/orientation-objects",
        headers={"X-AI-Cabinet-Admin-Token": "change-me-before-public-demo"},
    )

    assert response.status_code == 200
    assert "objects" in response.json()
