from risk_copilot.modeling import grouped_split, prepare_training_frame, train_candidates
from risk_copilot.simulation import simulate_scenario


def training_rows():
    labels = ["On Track", "Delayed", "Critical"]
    rows = []
    for repo_index in range(15):
        severity = repo_index % 3
        for horizon in (28, 21, 14, 7):
            rows.append({
                "repo": f"org/demo-{repo_index}",
                "label": labels[severity],
                "training_eligible": True,
                "horizon_days": horizon,
                "open_issue_count": 3 + severity * 7,
                "closed_issue_count": 15 - severity * 2,
                "open_pr_count": 1 + severity * 2,
                "closed_pr_count": 8 - severity,
                "median_open_issue_age_days": 4 + severity * 10,
                "scope_added_14d": severity * 2,
                "scope_removed_14d": severity,
                "reviews_14d": 10 - severity * 2,
                "median_first_review_latency_hours": 5 + severity * 15,
                "commit_count_14d": 30 - severity * 6,
                "active_contributors_14d": 8 - severity,
            })
    return rows


def test_decision_lab_returns_noncausal_scenario_result():
    frame = prepare_training_frame(training_rows())
    split = grouped_split(frame, test_size=0.2, random_state=9)
    models, _ = train_candidates(split, random_state=9)
    model = models["logistic_regression"]
    current = split.test.iloc[0].to_dict()

    result = simulate_scenario(
        model,
        current,
        {"open_issue_count": 2, "median_first_review_latency_hours": 4},
        bounds={"open_issue_count": (0, None), "median_first_review_latency_hours": (0, None)},
    )

    assert "scenario_risk_score" in result
    assert "causal" in result["disclaimer"].lower()
    assert set(result["changed_features"]) == {
        "open_issue_count",
        "median_first_review_latency_hours",
    }
