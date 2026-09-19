# Risk Copilot V2 Architecture

## Purpose

This build replaces the V1 synthetic training path with an auditable GitHub-data foundation. V1 artifacts remain in repository history for comparison, but `updated_report1.csv`, `model.pkl`, `feature_columns.pkl`, and the Java rule layer are **not** treated as V2 training truth.

## Current foundation

- V2 package, docs, tests, and CI foundation.
- GitHub REST ingestion for milestones, milestone items, issue events, PR reviews, and commits.
- Deterministic versioned project-outcome labels.
- T-28/T-21/T-14/T-7 point-in-time snapshots and leakage checks.
- Engineering-delivery feature generation.

## Data flow

`GitHub REST -> raw API objects -> historical membership replay -> temporal snapshots -> V2 labels/features -> model training`

## Important limitation discovered during research

GitHub's standard milestone REST object exposes the current `due_on` value, but the public milestone API does not provide a reliable historical log of due-date edits. Using today's due date to represent an old snapshot can leak rescheduling information.

The code therefore makes this explicit:

- `due_date_source=current_api_value`
- strict mode: `training_eligible=false`
- research mode: `--allow-due-date-proxy` permits experimentation but keeps the proxy flag in every row

We will not report historical due-date accuracy that GitHub does not actually expose.

## Free/open resources used

- GitHub public REST API
- Python standard library for the ingestion client
- pytest for automated tests
- GitHub Actions for CI

No paid data source or paid model is required for the current foundation.
