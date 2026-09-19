from datetime import datetime, timezone

from risk_copilot.labels import Outcome, derive_milestone_label


def test_label_policy_boundaries_and_scope_override():
    base = {"due_on": "2026-01-31T00:00:00Z"}

    on_time = derive_milestone_label({**base, "closed_at": "2026-01-31T00:00:00Z"})
    delayed = derive_milestone_label({**base, "closed_at": "2026-02-15T00:00:00Z"})
    critical = derive_milestone_label({**base, "closed_at": "2026-03-05T00:00:00Z"})
    scope_critical = derive_milestone_label(
        {**base, "closed_at": "2026-01-20T00:00:00Z"}, scope_moved_out_ratio=0.41
    )
    gap = derive_milestone_label(
        {**base, "closed_at": None}, as_of=datetime(2026, 3, 15, tzinfo=timezone.utc)
    )

    assert on_time.outcome == Outcome.ON_TRACK
    assert delayed.outcome == Outcome.DELAYED
    assert critical.outcome == Outcome.CRITICAL
    assert scope_critical.outcome == Outcome.CRITICAL
    assert gap.outcome == Outcome.UNKNOWN
    assert "31_to_60" in gap.reason
