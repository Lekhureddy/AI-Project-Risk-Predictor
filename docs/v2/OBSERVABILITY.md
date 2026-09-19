# Observability and Drift

Risk Copilot includes lightweight local observability hooks and model-input drift checks.

## Drift

Feature distributions can be compared between a reference dataset and a current dataset using Population Stability Index (PSI).

The implementation marks:

- low drift
- moderate drift
- high drift
- insufficient data

A high-drift feature triggers an alert in the drift summary.

PSI thresholds are operational heuristics, not universal statistical guarantees. They should be tuned using the actual deployment population.

## Event observability

The JSONL observer can record application events and measured latency without requiring a paid monitoring platform.

For a production deployment this interface can be replaced by OpenTelemetry / managed observability without changing product logic.

## Weekly digest

The weekly digest compares current and previous portfolio assessments and surfaces worsening, improving, and newly observed delivery risks.
