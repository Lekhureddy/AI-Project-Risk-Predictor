from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class Outcome(str, Enum):
    ON_TRACK = "On Track"
    DELAYED = "Delayed"
    CRITICAL = "Critical"
    UNKNOWN = "Unknown"


@dataclass(frozen=True)
class LabelResult:
    outcome: Outcome
    reason: str
    days_late: int | None
    label_version: str = "v2.0"


def parse_dt(value):
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def derive_milestone_label(milestone, *, scope_moved_out_ratio=None, as_of=None):
    due = parse_dt(milestone.get("due_on"))
    closed = parse_dt(milestone.get("closed_at"))
    now = as_of or datetime.now(timezone.utc)

    if scope_moved_out_ratio is not None and scope_moved_out_ratio > 0.40:
        return LabelResult(Outcome.CRITICAL, "scope_moved_out_ratio_gt_40pct", None)
    if due is None:
        return LabelResult(Outcome.UNKNOWN, "missing_due_date", None)
    if closed is not None:
        days_late = (closed.date() - due.date()).days
        if days_late <= 0:
            return LabelResult(Outcome.ON_TRACK, "closed_on_or_before_due_date", days_late)
        if days_late <= 30:
            return LabelResult(Outcome.DELAYED, "closed_1_to_30_days_late", days_late)
        return LabelResult(Outcome.CRITICAL, "closed_more_than_30_days_late", days_late)

    days_past_due = (now.date() - due.date()).days
    if days_past_due > 60:
        return LabelResult(Outcome.CRITICAL, "open_more_than_60_days_past_due", days_past_due)
    if days_past_due <= 0:
        return LabelResult(Outcome.UNKNOWN, "milestone_not_finished", days_past_due)
    if days_past_due <= 30:
        return LabelResult(Outcome.DELAYED, "open_1_to_30_days_past_due", days_past_due)
    return LabelResult(Outcome.UNKNOWN, "open_31_to_60_days_past_due_policy_gap", days_past_due)
