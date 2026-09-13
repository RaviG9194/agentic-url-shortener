from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Agentic URL Shortener is running!"


def test_create_short_url():
    response = client.post(
        "/api/v1/urls",
        json={
            "url": "https://www.google.com"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "short_code" in data
    assert "short_url" in data
    assert data["original_url"] == "https://www.google.com/"


def test_invalid_url_is_rejected():
    response = client.post(
        "/api/v1/urls",
        json={
            "url": "not-a-valid-url"
        },
    )

    assert response.status_code == 422
