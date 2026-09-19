from risk_copilot.metric_evidence import metric_evidence_from_features


def test_metric_evidence_is_verbatim_and_feature_scoped():
    evidence, mapping = metric_evidence_from_features({
        "open_issue_count": 7,
        "median_first_review_latency_hours": 48.5,
    })
    by_id = {row["evidence_id"]: row for row in evidence}
    quote = mapping["open_issue_count"][0]["quote"]
    assert quote == by_id["METRIC:open_issue_count"]["text"]
    assert "7" in quote
    assert "hours" in by_id["METRIC:median_first_review_latency_hours"]["text"]
