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


def test_chat_endpoint_returns_followup():
    client = TestClient(app)

    response = client.post("/api/chat", json={"message": "Tư vấn du lịch Nha Trang"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["needs_followup"] is True
    assert payload["profile"]["destination"] == "Nha Trang"
    assert payload["suggestions"]


def test_chat_endpoint_returns_recommendations():
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        json={
            "message": "Gia đình 2 người lớn 1 bé đi Nha Trang 3 ngày 2 đêm, budget 15-20 triệu, ưu tiên vui chơi cho trẻ em."
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["needs_followup"] is False
    assert payload["cards"]
    assert payload["confidence"] in {"high", "medium"}
