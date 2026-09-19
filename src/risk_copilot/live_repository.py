from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .github_evidence import evidence_from_milestone_items
from .labels import parse_dt
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


def current_milestone_features(repo: str, milestone_number: int, client: GitHubClient | None = None, now=None) -> dict:
    client = client or GitHubClient()
    now = now or datetime.now(timezone.utc)
    milestones = {int(m["number"]): m for m in client.list_milestones(repo, state="all")}
    if milestone_number not in milestones:
        raise KeyError(f"milestone {milestone_number} not found")

    milestone = milestones[milestone_number]
    items = client.list_milestone_items(repo, milestone_number)
    issues = [x for x in items if "pull_request" not in x]
    prs = [x for x in items if "pull_request" in x]
    open_issues = [x for x in issues if not x.get("closed_at")]
    open_prs = [x for x in prs if not x.get("closed_at")]

    issue_ages = []
    for item in open_issues:
        created = parse_dt(item.get("created_at"))
        if created:
            issue_ages.append((now - created).total_seconds() / 86400.0)

    window_start = now - timedelta(days=14)
    scope_added = 0
    scope_removed = 0
    review_latencies = []
    reviews_14d = 0

    for item in items:
        for event in client.list_issue_events(repo, int(item["number"])):
            event_at = parse_dt(event.get("created_at"))
            if not event_at or not (window_start < event_at <= now):
                continue
            if event.get("event") == "milestoned":
                scope_added += 1
            elif event.get("event") == "demilestoned":
                scope_removed += 1

    for pr in prs:
        created = parse_dt(pr.get("created_at"))
        reviews = client.list_pull_reviews(repo, int(pr["number"]))
        valid = []
        for review in reviews:
            submitted = parse_dt(review.get("submitted_at"))
            if submitted and submitted <= now:
                valid.append(submitted)
                if submitted > window_start:
                    reviews_14d += 1
        if created and valid:
            first = min(valid)
            if first >= created:
                review_latencies.append((first - created).total_seconds() / 3600.0)

    commits = client.list_commits(repo, since=window_start.isoformat(), until=now.isoformat())
    contributors = set()
    commit_count = 0
    for commit in commits:
        commit_at = parse_dt((((commit.get("commit") or {}).get("author") or {}).get("date")))
        if commit_at and window_start < commit_at <= now:
            commit_count += 1
            login = (commit.get("author") or {}).get("login")
            email = (((commit.get("commit") or {}).get("author") or {}).get("email"))
            contributors.add(str(login or email or "unknown"))

    due = parse_dt(milestone.get("due_on"))
    horizon_days = max((due.date() - now.date()).days, 0) if due else 0

    def median_or_none(values):
        if not values:
            return None
        values = sorted(values)
        mid = len(values) // 2
        if len(values) % 2:
            return float(values[mid])
        return float((values[mid - 1] + values[mid]) / 2)

    return {
        "repo": repo,
        "project_name": str(milestone.get("title") or f"Delivery target {milestone_number}"),
        "milestone_number": milestone_number,
        "features": {
            "open_issue_count": len(open_issues),
            "closed_issue_count": len(issues) - len(open_issues),
            "open_pr_count": len(open_prs),
            "closed_pr_count": len(prs) - len(open_prs),
            "median_open_issue_age_days": median_or_none(issue_ages),
            "scope_added_14d": scope_added,
            "scope_removed_14d": scope_removed,
            "reviews_14d": reviews_14d,
            "median_first_review_latency_hours": median_or_none(review_latencies),
            "commit_count_14d": commit_count,
            "active_contributors_14d": len(contributors),
            "horizon_days": horizon_days,
        },
        "evidence": evidence_from_milestone_items(repo, items),
        "snapshot_at": now.isoformat(),
        "due_on": milestone.get("due_on"),
    }
