from risk_copilot.explanations import explain_prediction
from risk_copilot.modeling import grouped_split, prepare_training_frame, train_candidates


def rows():
    labels = ["On Track", "Delayed", "Critical"]
    result = []
    for repo_index in range(12):
        severity = repo_index % 3
        for horizon in (28, 21, 14, 7):
            result.append({
                "repo": f"org/r{repo_index}",
                "label": labels[severity],
                "training_eligible": True,
                "horizon_days": horizon,
                "open_issue_count": 2 + severity * 8,
                "closed_issue_count": 15 - severity * 3,
                "open_pr_count": 1 + severity * 3,
                "closed_pr_count": 9 - severity,
                "median_open_issue_age_days": 2 + severity * 12,
                "scope_added_14d": severity * 3,
                "scope_removed_14d": severity,
                "reviews_14d": 10 - severity * 3,
                "median_first_review_latency_hours": 3 + severity * 16,
                "commit_count_14d": 35 - severity * 8,
                "active_contributors_14d": 8 - severity,
            })
    return result


def test_model_grounded_explanation_returns_ranked_drivers():
    df = prepare_training_frame(rows())
    split = grouped_split(df, test_size=0.25, random_state=2)
    models, _ = train_candidates(split, random_state=2)

    sample = split.test.iloc[0]
    drivers = explain_prediction(
        models["logistic_regression"],
        sample,
        split.train,
        top_k=4,
    )

    assert len(drivers) == 4
    assert all("contribution" in d for d in drivers)
    magnitudes = [abs(d["contribution"]) for d in drivers]
    assert magnitudes == sorted(magnitudes, reverse=True)
