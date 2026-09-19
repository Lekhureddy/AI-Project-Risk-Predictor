# V2 Data Contract

Each feature row represents one delivery target at one prediction horizon.

Identity and provenance fields include repository, delivery-target identifier/title, snapshot time, prediction horizon, due-date source, outcome label, label policy version, and training eligibility.

Core features include open/closed issue counts, open/closed PR counts, median open issue age, recent scope additions/removals, review activity, first-review latency, commit activity, and active contributors.

Quality metadata records whether historical membership reconstruction is complete.

## Outcome policy

- On Track — closed on or before the due date.
- Delayed — closed 1–30 days late; also open 1–30 days past due.
- Critical — closed more than 30 days late, more than 40% of tracked scope moved out, or open more than 60 days past due.
- Unknown — insufficient evidence for a defensible supported class.

Unknown is intentional: unsupported cases are not silently forced into a class.
