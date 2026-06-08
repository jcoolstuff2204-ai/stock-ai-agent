from fastapi.testclient import TestClient

from backend.app.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_paper_trade_creation():
    client = TestClient(app)
    response = client.post(
        "/api/paper-trades",
        json={"ticker": "NVDA", "action": "BUY", "entry_price": 100, "stop_loss": 95, "target_price": 110, "shares": 1},
    )
    assert response.status_code == 200
    assert response.json()["ticker"] == "NVDA"

