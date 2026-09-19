from datetime import datetime, timezone

import pytest

from risk_copilot.temporal import assert_no_future_timestamps, membership_at, snapshot_dates


def test_temporal_membership_and_leakage_guard():
    events = [
        {"event": "milestoned", "created_at": "2026-01-01T00:00:00Z", "milestone": {"title": "M1"}},
        {"event": "demilestoned", "created_at": "2026-01-20T00:00:00Z", "milestone": {"title": "M1"}},
    ]
    member, complete = membership_at(
        events=events,
        milestone_title="M1",
        snapshot_at=datetime(2026, 1, 14, tzinfo=timezone.utc),
        current_member=False,
        issue_created_at="2025-12-20T00:00:00Z",
    )
    assert member is True and complete is True

    horizons = snapshot_dates("2026-02-01T00:00:00Z")
    assert [h for h, _ in horizons] == [28, 21, 14, 7]

    with pytest.raises(ValueError, match="future leakage"):
        assert_no_future_timestamps(
            [{"snapshot_date": "2026-01-14T00:00:00Z", "created_at": "2026-01-15T00:00:00Z"}]
        )
