from risk_copilot.data_quality import validate_rows


def row(repo, project, label, horizon, eligible=True, **overrides):
    base = {
        "repo": repo,
        "milestone_title": project,
        "snapshot_date": f"2026-01-{horizon:02d}T00:00:00+00:00",
        "horizon_days": horizon,
        "due_on_at_snapshot": "2026-02-01T00:00:00Z",
        "due_date_source": "verified_fixture",
        "membership_history_complete": True,
        "training_eligible": eligible,
        "label": label,
        "label_version": "v2.0",
        "open_issue_count": 2,
        "closed_issue_count": 3,
        "open_pr_count": 1,
        "closed_pr_count": 1,
        "median_open_issue_age_days": 4.0,
        "scope_added_14d": 1,
        "scope_removed_14d": 0,
        "reviews_14d": 2,
        "median_first_review_latency_hours": 6.0,
        "commit_count_14d": 12,
        "active_contributors_14d": 3,
    }
    base.update(overrides)
    return base


def test_quality_gate_accepts_diverse_complete_fixture():
    rows = []
    labels = ["On Track", "Delayed", "Critical"]
    for i in range(5):
        for horizon in (7, 14, 21, 28):
            rows.append(row(f"org/repo{i}", f"release-{i}", labels[i % 3], horizon))

    report = validate_rows(
        rows,
        min_rows=20,
        min_repositories=5,
        min_eligible_fraction=0.90,
    )

    assert report.blockers == []
    assert report.repository_count == 5
    assert report.eligible_fraction == 1.0


def test_quality_gate_blocks_sparse_or_duplicate_data():
    duplicate = row("org/repo", "release", "On Track", 14, eligible=False)
    rows = [duplicate, dict(duplicate)]

    report = validate_rows(
        rows,
        min_rows=10,
        min_repositories=2,
        min_eligible_fraction=0.50,
    )

    assert any(x.startswith("too_few_rows") for x in report.blockers)
    assert any(x.startswith("too_few_repositories") for x in report.blockers)
    assert any(x.startswith("eligible_fraction_too_low") for x in report.blockers)
    assert any(x.startswith("duplicate_snapshot_identity") for x in report.blockers)
    assert "insufficient_supported_label_diversity" in report.blockers
