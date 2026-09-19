from __future__ import annotations

FEATURE_LABELS = {
    "open_issue_count": "Open issue count",
    "closed_issue_count": "Closed issue count",
    "open_pr_count": "Open pull request count",
    "closed_pr_count": "Closed pull request count",
    "median_open_issue_age_days": "Median open issue age",
    "scope_added_14d": "Scope added in last 14 days",
    "scope_removed_14d": "Scope removed in last 14 days",
    "reviews_14d": "Reviews in last 14 days",
    "median_first_review_latency_hours": "Median first-review latency",
    "commit_count_14d": "Commits in last 14 days",
    "active_contributors_14d": "Active contributors in last 14 days",
    "horizon_days": "Days until due date",
}

UNITS = {
    "median_open_issue_age_days": "days",
    "median_first_review_latency_hours": "hours",
    "horizon_days": "days",
}


def metric_evidence_from_features(features: dict) -> tuple[list[dict], dict[str, list[dict]]]:
    evidence = []
    mapping: dict[str, list[dict]] = {}

    for feature, label in FEATURE_LABELS.items():
        if feature not in features:
            continue
        value = features.get(feature)
        if value is None:
            continue
        unit = UNITS.get(feature, "")
        rendered = f"{label} is {value}{(' ' + unit) if unit else ''}."
        evidence_id = f"METRIC:{feature}"
        row = {
            "evidence_id": evidence_id,
            "source_type": "metric",
            "title": label,
            "url": "",
            "text": rendered,
        }
        evidence.append(row)
        mapping[feature] = [{"evidence_id": evidence_id, "quote": rendered}]
    return evidence, mapping
