from risk_copilot.narrative_service import generate_narrative


def test_default_narrative_provider_is_verified_and_free():
    evidence = [
        {
            "evidence_id": "PR-1",
            "source_type": "pull_request",
            "title": "Review",
            "url": "https://example.test/pr/1",
            "text": "Review has been waiting for four days.",
        }
    ]
    result = generate_narrative(
        model_drivers=[
            {
                "feature": "median_first_review_latency_hours",
                "contribution": 10.0,
                "direction": "raises risk",
            }
        ],
        evidence=evidence,
        evidence_for_feature={
            "median_first_review_latency_hours": [
                {"evidence_id": "PR-1", "quote": "waiting for four days"}
            ]
        },
    )
    assert result["provider"] == "TemplateNarrativeProvider"
    assert result["evaluation"]["citation_validity"] == 1.0
    assert result["abstained"] is False
