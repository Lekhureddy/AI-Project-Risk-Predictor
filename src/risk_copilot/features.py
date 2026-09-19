from __future__ import annotations

from datetime import timedelta
from statistics import median

from .labels import parse_dt
from .temporal import item_exists_at, item_open_at, membership_at


def _safe_median(values):
    return float(median(values)) if values else None


def build_snapshot_features(*, milestone, items, events_by_number, reviews_by_number, commits, snapshot_at, horizon_days, allow_membership_proxy=False):
    title = str(milestone.get("title") or "")
    milestone_number = milestone.get("number")
    window_start = snapshot_at - timedelta(days=14)

    members = []
    history_complete = True
    membership_proxy_used = False
    scope_added_14d = 0
    scope_removed_14d = 0

    for item in items:
        number = int(item["number"])
        events = events_by_number.get(number, [])
        current_member = (item.get("milestone") or {}).get("number") == milestone_number
        member, complete = membership_at(
            events=events,
            milestone_title=title,
            snapshot_at=snapshot_at,
            current_member=current_member,
            issue_created_at=item.get("created_at"),
        )
        history_complete = history_complete and complete
        if member is None and current_member and allow_membership_proxy and item_exists_at(item, snapshot_at):
            member = True
            membership_proxy_used = True
        if member is True and item_exists_at(item, snapshot_at):
            members.append(item)

        for event in events:
            when = parse_dt(event.get("created_at"))
            event_title = (event.get("milestone") or {}).get("title")
            if not when or event_title != title or not (window_start < when <= snapshot_at):
                continue
            if event.get("event") == "milestoned":
                scope_added_14d += 1
            elif event.get("event") == "demilestoned":
                scope_removed_14d += 1

    issues = [x for x in members if "pull_request" not in x]
    prs = [x for x in members if "pull_request" in x]
    open_issues = [x for x in issues if item_open_at(x, snapshot_at)]
    open_prs = [x for x in prs if item_open_at(x, snapshot_at)]

    issue_ages = []
    for item in open_issues:
        created = parse_dt(item.get("created_at"))
        if created:
            issue_ages.append((snapshot_at - created).total_seconds() / 86400.0)

    review_latencies = []
    reviews_14d = 0
    for pr in prs:
        created = parse_dt(pr.get("created_at"))
        valid_reviews = []
        for review in reviews_by_number.get(int(pr["number"]), []):
            submitted = parse_dt(review.get("submitted_at"))
            if submitted and submitted <= snapshot_at:
                valid_reviews.append(submitted)
                if submitted > window_start:
                    reviews_14d += 1
        if created and valid_reviews:
            first_review = min(valid_reviews)
            if first_review >= created:
                review_latencies.append((first_review - created).total_seconds() / 3600.0)

    commit_count_14d = 0
    contributors = set()
    for commit in commits:
        commit_at = parse_dt((((commit.get("commit") or {}).get("author") or {}).get("date")))
        if not commit_at or not (window_start < commit_at <= snapshot_at):
            continue
        commit_count_14d += 1
        login = (commit.get("author") or {}).get("login")
        email = (((commit.get("commit") or {}).get("author") or {}).get("email"))
        contributors.add(str(login or email or "unknown"))

    return {
        "repo": milestone.get("repo"),
        "milestone_number": milestone_number,
        "milestone_title": title,
        "snapshot_date": snapshot_at.isoformat(),
        "horizon_days": horizon_days,
        "due_on_at_snapshot": milestone.get("due_on"),
        "due_date_source": milestone.get("due_date_source", "current_api_value"),
        "membership_history_complete": history_complete,
        "membership_proxy_used": membership_proxy_used,
        "open_issue_count": len(open_issues),
        "closed_issue_count": len(issues) - len(open_issues),
        "open_pr_count": len(open_prs),
        "closed_pr_count": len(prs) - len(open_prs),
        "median_open_issue_age_days": _safe_median(issue_ages),
        "scope_added_14d": scope_added_14d,
        "scope_removed_14d": scope_removed_14d,
        "reviews_14d": reviews_14d,
        "median_first_review_latency_hours": _safe_median(review_latencies),
        "commit_count_14d": commit_count_14d,
        "active_contributors_14d": len(contributors),
    }
