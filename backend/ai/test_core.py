from fastapi.testclient import TestClient
from core import app


def test_calibrate_returns_recommendation():
    client = TestClient(app)
    payload = {"foo": "bar"}
    response = client.post("/calibrate", json={"payload": payload})

    assert response.status_code == 200
    data = response.json()
    assert "omega_score" in data
    assert data["recommendation"] in {"ACCELERATE", "MONITOR"}
