from datetime import datetime, timezone

from risk_copilot.live_repository import current_milestone_features, inspect_milestone, list_due_milestones


class FakeClient:
    def list_milestones(self, repo, state="all"):
        return [
            {
                "number": 3,
                "title": "Release",
                "state": "open",
                "due_on": "2026-10-01T00:00:00Z",
                "closed_at": None,
                "open_issues": 2,
                "closed_issues": 1,
                "html_url": "https://example.test/milestone/3",
            }
        ]

    def list_milestone_items(self, repo, milestone_number):
        return [
            {
                "number": 7,
                "title": "Issue",
                "body": "Needs work",
                "created_at": "2026-09-01T00:00:00Z",
                "closed_at": None,
                "html_url": "https://example.test/issues/7",
            },
            {
                "number": 8,
                "title": "PR",
                "body": "Review pending",
                "created_at": "2026-09-10T00:00:00Z",
                "closed_at": None,
                "html_url": "https://example.test/pull/8",
                "pull_request": {"url": "x"},
            },
        ]

    def list_issue_events(self, repo, issue_number):
        return [
            {
                "event": "milestoned",
                "created_at": "2026-09-15T00:00:00Z",
                "milestone": {"title": "Release"},
            }
        ]

    def list_pull_reviews(self, repo, pull_number):
        return [{"submitted_at": "2026-09-16T00:00:00Z"}]

    def list_commits(self, repo, since, until):
        return [
            {
                "author": {"login": "dev"},
                "commit": {"author": {"date": "2026-09-18T00:00:00Z", "email": "dev@example.com"}},
            }
        ]


def test_live_repository_inspection():
    milestones = list_due_milestones("org/repo", FakeClient())
    assert milestones[0]["number"] == 3

    result = inspect_milestone("org/repo", 3, FakeClient())
    assert result["summary"]["issues"] == 1
    assert result["summary"]["pull_requests"] == 1
    assert len(result["evidence"]) == 2


def test_current_milestone_features_are_derived_from_live_state():
    result = current_milestone_features(
        "org/repo",
        3,
        FakeClient(),
        now=datetime(2026, 9, 19, tzinfo=timezone.utc),
    )
    assert result["features"]["open_issue_count"] == 1
    assert result["features"]["open_pr_count"] == 1
    assert result["features"]["reviews_14d"] == 1
    assert result["features"]["commit_count_14d"] == 1
    assert result["features"]["active_contributors_14d"] == 1
    assert len(result["evidence"]) == 2
