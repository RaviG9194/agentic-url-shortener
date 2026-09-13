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


def test_redirect_with_expiration():
    response = client.post(
        "/api/v1/urls",
        json={
            "url": "https://example.com",
            "custom_alias": "redirect-test2",
            "expires_in_minutes": 60,
        },
    )

    assert response.status_code == 200

    redirect_response = client.get(
        "/redirect-test",
        follow_redirects=False,
    )

    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/"
