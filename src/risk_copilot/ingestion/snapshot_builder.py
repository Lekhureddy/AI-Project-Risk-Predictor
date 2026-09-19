from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from ..features import build_snapshot_features
from ..labels import derive_milestone_label, parse_dt
from ..temporal import DEFAULT_HORIZONS, snapshot_dates
from .github_client import GitHubClient


@dataclass
class RepositoryCollection:
    repo: str
    features: list[dict]
    labels: list[dict]
    warnings: list[str]


def _scope_removed_ratio(items, events_by_number, title):
    ever_added = set()
    removed_after_add = set()
    for item in items:
        number = int(item["number"])
        for event in events_by_number.get(number, []):
            if (event.get("milestone") or {}).get("title") != title:
                continue
            if event.get("event") == "milestoned":
                ever_added.add(number)
            elif event.get("event") == "demilestoned" and number in ever_added:
                removed_after_add.add(number)
    if not ever_added:
        return None
    return len(removed_after_add) / len(ever_added)


def collect_repository(client: GitHubClient, repo: str, *, horizons=DEFAULT_HORIZONS, max_milestones=None, collect_reviews=True, allow_due_date_proxy=False, allow_membership_proxy=False, as_of=None):
    now = as_of or datetime.now(timezone.utc)
    warnings = []
    feature_rows = []
    labels = []

    milestones = [m for m in client.list_milestones(repo, state="all") if m.get("due_on")]
    if max_milestones is not None:
        milestones = milestones[:max_milestones]

    for milestone in milestones:
        milestone = dict(milestone)
        milestone["repo"] = repo
        milestone["due_date_source"] = "current_api_value"
        number = int(milestone["number"])
        title = str(milestone.get("title") or "")

        items = client.list_milestone_items(repo, number)
        events_by_number = {}
        reviews_by_number = {}

        for item in items:
            item_number = int(item["number"])
            events_by_number[item_number] = client.list_issue_events(repo, item_number)
            if collect_reviews and "pull_request" in item:
                reviews_by_number[item_number] = client.list_pull_reviews(repo, item_number)

        scope_ratio = _scope_removed_ratio(items, events_by_number, title)
        label = derive_milestone_label(milestone, scope_moved_out_ratio=scope_ratio, as_of=now)
        labels.append({
            "repo": repo,
            "milestone_number": number,
            "milestone_title": title,
            "outcome": label.outcome.value,
            "label_reason": label.reason,
            "days_late": label.days_late,
            "label_version": label.label_version,
            "scope_moved_out_ratio": scope_ratio,
        })

        due = parse_dt(milestone.get("due_on"))
        if due is None:
            continue
        earliest = due - timedelta(days=max(horizons))
        commits = client.list_commits(repo, since=earliest.isoformat(), until=due.isoformat())

        for horizon, snap_at in snapshot_dates(milestone["due_on"], horizons):
            if snap_at > now:
                continue
            row = build_snapshot_features(
                milestone=milestone,
                items=items,
                events_by_number=events_by_number,
                reviews_by_number=reviews_by_number,
                commits=commits,
                snapshot_at=snap_at,
                horizon_days=horizon,
                allow_membership_proxy=allow_membership_proxy,
            )
            row["training_eligible"] = bool(
                allow_due_date_proxy and (row["membership_history_complete"] or allow_membership_proxy)
            )
            notes = []
            if allow_due_date_proxy:
                notes.append("current due_on used as historical proxy")
            else:
                notes.append("historical due_on changes unavailable; excluded in strict mode")
            if row.get("membership_proxy_used"):
                notes.append("current milestone membership used as historical proxy")
            row["data_quality_note"] = "; ".join(notes)
            row["label"] = label.outcome.value
            row["label_version"] = label.label_version
            feature_rows.append(row)

        if not allow_due_date_proxy:
            warnings.append(
                f"{repo} milestone #{number}: historical due-date changes are not exposed by the standard "
                "milestone API; snapshots are retained for analysis but training_eligible=false in strict mode."
            )

    return RepositoryCollection(repo=repo, features=feature_rows, labels=labels, warnings=warnings)
