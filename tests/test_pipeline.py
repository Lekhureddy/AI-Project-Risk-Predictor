from datetime import datetime, timezone

from risk_copilot.ingestion.snapshot_builder import collect_repository


class FakeClient:
    def list_milestones(self, repo, state="all"):
        return [{
            "number": 1,
            "title": "Release 1",
            "due_on": "2026-02-01T00:00:00Z",
            "closed_at": "2026-02-10T00:00:00Z",
        }]

    def list_milestone_items(self, repo, milestone_number):
        return [
            {
                "number": 10,
                "created_at": "2025-12-20T00:00:00Z",
                "closed_at": "2026-01-25T00:00:00Z",
                "milestone": {"number": 1},
            },
            {
                "number": 11,
                "created_at": "2025-12-28T00:00:00Z",
                "closed_at": None,
                "milestone": {"number": 1},
                "pull_request": {"url": "x"},
            },
        ]

    def list_issue_events(self, repo, issue_number):
        return [{
            "event": "milestoned",
            "created_at": "2025-12-29T00:00:00Z" if issue_number == 11 else "2025-12-21T00:00:00Z",
            "milestone": {"title": "Release 1"},
        }]

    def list_pull_reviews(self, repo, pull_number):
        return [{"submitted_at": "2026-01-10T12:00:00Z"}]

    def list_commits(self, repo, since, until):
        return [{
            "author": {"login": "dev1"},
            "commit": {"author": {"date": "2026-01-12T00:00:00Z", "email": "dev1@example.com"}},
        }]


def test_m0_to_m4_end_to_end_with_explicit_due_date_proxy_flag():
    result = collect_repository(
        FakeClient(),
        "acme/demo",
        allow_due_date_proxy=True,
        as_of=datetime(2026, 3, 1, tzinfo=timezone.utc),
    )

    assert len(result.labels) == 1
    assert result.labels[0]["outcome"] == "Delayed"
    assert len(result.features) == 4

    t14 = next(row for row in result.features if row["horizon_days"] == 14)
    assert t14["open_issue_count"] == 1
    assert t14["open_pr_count"] == 1
    assert t14["training_eligible"] is True
    assert t14["due_date_source"] == "current_api_value"
    assert t14["active_contributors_14d"] == 1


def test_membership_proxy_is_explicit_and_training_eligible_only_when_enabled():
    class ProxyClient(FakeClient):
        def list_issue_events(self, repo, issue_number):
            return []

    result = collect_repository(
        ProxyClient(),
        "acme/demo",
        allow_due_date_proxy=True,
        allow_membership_proxy=True,
        as_of=datetime(2026, 3, 1, tzinfo=timezone.utc),
    )
    assert result.features
    assert all(row["training_eligible"] is True for row in result.features)
    assert any(row["membership_proxy_used"] for row in result.features)
    assert any("membership" in row["data_quality_note"] for row in result.features)
