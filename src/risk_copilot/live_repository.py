from __future__ import annotations

from .github_evidence import evidence_from_milestone_items
from .ingestion.github_client import GitHubClient


def list_due_milestones(repo: str, client: GitHubClient | None = None) -> list[dict]:
    client = client or GitHubClient()
    milestones = client.list_milestones(repo, state="all")
    rows = []
    for m in milestones:
        if not m.get("due_on"):
            continue
        rows.append(
            {
                "number": int(m["number"]),
                "title": str(m.get("title") or ""),
                "state": str(m.get("state") or ""),
                "due_on": m.get("due_on"),
                "closed_at": m.get("closed_at"),
                "open_issues": int(m.get("open_issues") or 0),
                "closed_issues": int(m.get("closed_issues") or 0),
                "html_url": m.get("html_url"),
            }
        )
    return rows


def inspect_milestone(repo: str, milestone_number: int, client: GitHubClient | None = None) -> dict:
    client = client or GitHubClient()
    milestones = {int(m["number"]): m for m in client.list_milestones(repo, state="all")}
    if milestone_number not in milestones:
        raise KeyError(f"milestone {milestone_number} not found")

    milestone = milestones[milestone_number]
    items = client.list_milestone_items(repo, milestone_number)
    evidence = evidence_from_milestone_items(repo, items)

    issue_count = sum(1 for item in items if "pull_request" not in item)
    pr_count = sum(1 for item in items if "pull_request" in item)

    return {
        "repository": repo,
        "milestone": {
            "number": milestone_number,
            "title": milestone.get("title"),
            "state": milestone.get("state"),
            "due_on": milestone.get("due_on"),
            "closed_at": milestone.get("closed_at"),
        },
        "summary": {
            "items": len(items),
            "issues": issue_count,
            "pull_requests": pr_count,
        },
        "evidence": evidence,
        "note": (
            "This view is current repository evidence. Historical risk inference requires "
            "the point-in-time dataset pipeline and a validated model."
        ),
    }
