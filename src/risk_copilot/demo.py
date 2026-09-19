from __future__ import annotations


def demo_assessments() -> list[dict]:
    return [
        {
            "assessment_id": "demo-checkout",
            "project_id": "checkout-platform",
            "project_name": "Checkout Platform",
            "created_at": "2026-09-19T15:00:00-05:00",
            "risk_score": 82.0,
            "risk_band": "Critical",
            "risk_change": 18.0,
            "probabilities": {"On Track": 0.08, "Delayed": 0.20, "Critical": 0.72},
        },
        {
            "assessment_id": "demo-mobile",
            "project_id": "mobile-release",
            "project_name": "Mobile Release",
            "created_at": "2026-09-19T15:00:00-05:00",
            "risk_score": 64.0,
            "risk_band": "High",
            "risk_change": 7.0,
            "probabilities": {"On Track": 0.22, "Delayed": 0.42, "Critical": 0.36},
        },
        {
            "assessment_id": "demo-search",
            "project_id": "search-upgrade",
            "project_name": "Search Upgrade",
            "created_at": "2026-09-19T15:00:00-05:00",
            "risk_score": 23.0,
            "risk_band": "Low",
            "risk_change": -4.0,
            "probabilities": {"On Track": 0.68, "Delayed": 0.26, "Critical": 0.06},
        },
    ]


def demo_timeline(project_id: str) -> list[dict]:
    if project_id == "checkout-platform":
        scores = [31, 39, 52, 67, 82]
    elif project_id == "mobile-release":
        scores = [45, 49, 54, 57, 64]
    else:
        scores = [30, 28, 27, 25, 23]
    dates = ["2026-08-22", "2026-08-29", "2026-09-05", "2026-09-12", "2026-09-19"]
    return [
        {"timestamp": f"{date}T15:00:00-05:00", "risk_score": score}
        for date, score in zip(dates, scores)
    ]


def demo_evidence(project_id: str) -> list[dict]:
    if project_id != "checkout-platform":
        return []
    return [
        {
            "evidence_id": "PR-1842",
            "source_type": "pull_request",
            "title": "Payment retry logic",
            "url": "https://github.com/example/checkout/pull/1842",
            "text": "Review has been waiting for four days and remains required for the release.",
        },
        {
            "evidence_id": "ISSUE-428",
            "source_type": "issue",
            "title": "Payment service dependency",
            "url": "https://github.com/example/checkout/issues/428",
            "text": "The checkout release depends on the payment service migration being completed.",
        },
        {
            "evidence_id": "ISSUE-517",
            "source_type": "issue",
            "title": "Late scope addition",
            "url": "https://github.com/example/checkout/issues/517",
            "text": "Seven additional release-scope issues were added during the final two weeks.",
        },
    ]


def demo_drivers() -> list[dict]:
    return [
        {
            "claim": "PR review latency is elevated.",
            "feature": "median_first_review_latency_hours",
            "contribution": 12.0,
            "citations": [{"evidence_id": "PR-1842", "quote": "waiting for four days"}],
        },
        {
            "claim": "A delivery dependency remains unresolved.",
            "feature": "open_issue_count",
            "contribution": 9.0,
            "citations": [{"evidence_id": "ISSUE-428", "quote": "depends on the payment service migration"}],
        },
        {
            "claim": "Scope increased close to the due date.",
            "feature": "scope_added_14d",
            "contribution": 7.0,
            "citations": [{"evidence_id": "ISSUE-517", "quote": "Seven additional release-scope issues"}],
        },
    ]
