from risk_copilot.github_evidence import evidence_from_milestone_items


def test_github_evidence_adapter_redacts_email_and_preserves_source():
    evidence = evidence_from_milestone_items(
        "org/repo",
        [
            {
                "number": 7,
                "title": "Blocked payment task",
                "body": "Owner is person@example.com",
                "html_url": "https://github.com/org/repo/issues/7",
            }
        ],
    )
    assert evidence[0]["evidence_id"] == "org/repo:ISSUE-7"
    assert "[REDACTED_EMAIL]" in evidence[0]["text"]
