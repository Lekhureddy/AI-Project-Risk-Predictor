from __future__ import annotations

from datetime import timedelta

from .labels import parse_dt

DEFAULT_HORIZONS = (28, 21, 14, 7)


def snapshot_dates(due_on, horizons=DEFAULT_HORIZONS):
    due = parse_dt(due_on)
    if due is None:
        return []
    return [(int(h), due - timedelta(days=int(h))) for h in horizons]


def item_exists_at(item, snapshot_at):
    created = parse_dt(item.get("created_at"))
    return created is not None and created <= snapshot_at


def item_open_at(item, snapshot_at):
    if not item_exists_at(item, snapshot_at):
        return False
    closed = parse_dt(item.get("closed_at"))
    return closed is None or closed > snapshot_at


def membership_at(*, events, milestone_title, snapshot_at, current_member, issue_created_at=None):
    created = parse_dt(issue_created_at)
    if created and snapshot_at < created:
        return False, True

    relevant = []
    for event in events:
        event_type = event.get("event")
        title = (event.get("milestone") or {}).get("title")
        when = parse_dt(event.get("created_at"))
        if event_type in {"milestoned", "demilestoned"} and title == milestone_title and when:
            relevant.append((when, event_type))
    relevant.sort(key=lambda x: x[0])

    if not relevant:
        if current_member:
            return None, False
        return False, True

    member = False
    for when, event_type in relevant:
        if when > snapshot_at:
            break
        member = event_type == "milestoned"
    return member, True


def assert_no_future_timestamps(rows, *, snapshot_key="snapshot_date", event_time_keys=("created_at", "closed_at", "review_submitted_at", "commit_at")):
    for row in rows:
        snapshot = parse_dt(str(row.get(snapshot_key)))
        if snapshot is None:
            raise ValueError(f"missing/invalid {snapshot_key}")
        for key in event_time_keys:
            value = row.get(key)
            if not value:
                continue
            event_at = parse_dt(str(value))
            if event_at and event_at > snapshot:
                raise ValueError(f"future leakage: {key}={value} > {snapshot_key}={row.get(snapshot_key)}")
