from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_health_and_demo_portfolio():
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    portfolio = client.get("/portfolio?demo=true")
    assert portfolio.status_code == 200
    body = portfolio.json()
    assert body["active_count"] == 3
    assert body["band_counts"]["Critical"] == 1


def test_demo_project_detail_has_timeline_and_evidence():
    response = client.get("/projects/checkout-platform?demo=true")
    assert response.status_code == 200
    body = response.json()
    assert body["latest"]["risk_score"] == 82.0
    assert len(body["timeline"]) == 5
    assert len(body["evidence"]) == 3
