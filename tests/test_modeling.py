import pandas as pd
import pytest

from risk_copilot.modeling import (
    grouped_split,
    prepare_training_frame,
    risk_score_from_probabilities,
    train_candidates,
)


def make_rows():
    labels = ["On Track", "Delayed", "Critical"]
    rows = []
    for repo_index in range(9):
        for horizon in (28, 21, 14, 7):
            label = labels[repo_index % 3]
            severity = labels.index(label)
            rows.append({
                "repo": f"org/repo-{repo_index}",
                "label": label,
                "training_eligible": True,
                "horizon_days": horizon,
                "open_issue_count": 2 + severity * 5 + (28 - horizon) // 7,
                "closed_issue_count": 12 - severity * 2,
                "open_pr_count": 1 + severity * 2,
                "closed_pr_count": 8 - severity,
                "median_open_issue_age_days": 3 + severity * 10,
                "scope_added_14d": severity * 2,
                "scope_removed_14d": severity,
                "reviews_14d": 8 - severity * 2,
                "median_first_review_latency_hours": 4 + severity * 12,
                "commit_count_14d": 30 - severity * 6,
                "active_contributors_14d": 7 - severity,
            })
    return rows


def test_grouped_training_has_no_repo_leakage_and_produces_metrics():
    df = prepare_training_frame(make_rows())
    split = grouped_split(df, test_size=0.33, random_state=7)

    assert set(split.train["repo"]).isdisjoint(set(split.test["repo"]))

    models, metrics = train_candidates(split, random_state=7)
    assert "majority_baseline" in models
    assert "logistic_regression" in models
    assert "hist_gradient_boosting" in models
    assert all(0.0 <= m["macro_f1"] <= 1.0 for m in metrics.values())


def test_training_rejects_single_repo_and_single_class():
    rows = make_rows()
    one_repo = pd.DataFrame([r for r in rows if r["repo"] == "org/repo-0"])
    with pytest.raises(ValueError, match="at least two supported outcome classes"):
        prepare_training_frame(one_repo)

    same_class = pd.DataFrame([{**r, "label": "Critical"} for r in rows])
    with pytest.raises(ValueError, match="at least two supported outcome classes"):
        prepare_training_frame(same_class)


def test_risk_score_is_expected_severity_not_confidence():
    score = risk_score_from_probabilities({
        "On Track": 0.10,
        "Delayed": 0.30,
        "Critical": 0.60,
    })
    assert score == 75.0
