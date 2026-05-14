from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_jazekker_public_pages_are_available():
    for path in ("/jazekker", "/jazekker/news", "/jazekker/articles"):
        response = client.get(path)

        assert response.status_code == 200


def test_jazekker_public_pages_hide_internal_controls():
    for path in ("/jazekker", "/jazekker/news"):
        response = client.get(path)

        assert response.status_code == 200
        assert "/jazekker/news/collect" not in response.text
        assert "AI Cabinet" not in response.text


def test_jazekker_articles_api_exposes_launch_metadata():
    response = client.get("/jazekker/articles")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 8
    assert payload["categories"]
    assert all("url" in article for article in payload["articles"])
    assert all("orientation_score" in article for article in payload["articles"])


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
