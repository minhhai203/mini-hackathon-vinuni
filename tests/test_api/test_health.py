from fastapi.testclient import TestClient

from src.main import app


def test_health_check():
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_static_homepage_served():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Vinpearl" in response.text
