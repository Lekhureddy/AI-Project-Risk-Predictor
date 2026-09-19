from risk_copilot.live_repository import inspect_milestone, list_due_milestones


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
                "html_url": "https://example.test/issues/7",
            },
            {
                "number": 8,
                "title": "PR",
                "body": "Review pending",
                "html_url": "https://example.test/pull/8",
                "pull_request": {"url": "x"},
            },
        ]


def test_live_repository_inspection():
    milestones = list_due_milestones("org/repo", FakeClient())
    assert milestones[0]["number"] == 3

    result = inspect_milestone("org/repo", 3, FakeClient())
    assert result["summary"]["issues"] == 1
    assert result["summary"]["pull_requests"] == 1
    assert len(result["evidence"]) == 2
