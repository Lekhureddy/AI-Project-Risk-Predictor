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


def test_narrative_endpoint_verifies_citations():
    payload = {
        "model_drivers": [
            {
                "feature": "median_first_review_latency_hours",
                "contribution": 8,
                "direction": "raises risk"
            }
        ],
        "evidence": [
            {
                "evidence_id": "PR-1",
                "source_type": "pull_request",
                "title": "Review",
                "url": "https://example.test/pr/1",
                "text": "Review has been waiting for four days."
            }
        ],
        "evidence_for_feature": {
            "median_first_review_latency_hours": [
                {"evidence_id": "PR-1", "quote": "waiting for four days"}
            ]
        }
    }
    response = client.post("/narrative", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["evaluation"]["citation_validity"] == 1.0
    assert body["abstained"] is False
