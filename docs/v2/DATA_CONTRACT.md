# V2 Data Contract — M0-M4

Each feature row is one milestone at one prediction horizon.

Identity fields: repo, milestone_number, milestone_title, snapshot_date, horizon_days, due_on_at_snapshot, due_date_source, label, label_version, training_eligible.

Core features: open/closed issue counts, open/closed PR counts, median open issue age, 14-day scope adds/removals, review count, median first-review latency, 14-day commits, and active contributors.

Quality field: membership_history_complete.

## Frozen label policy v2.0

- On Track — closed on or before due date.
- Delayed — closed 1-30 days late; also open 1-30 days past due.
- Critical — closed more than 30 days late, more than 40% scope moved out, or open more than 60 days past due.
- Unknown — missing due date, unfinished future milestone, or a policy gap such as an open milestone 31-60 days past due.

Unknown is deliberate: unsupported cases are not silently forced into a class.
