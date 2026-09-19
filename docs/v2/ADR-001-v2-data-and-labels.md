# ADR-001 — V2 real outcome data and temporal labels

**Status:** Accepted for M0-M4

V2 will not train on the legacy `updated_report1.csv` synthetic/product dataset or the human-authored `Risk Level` field. V2 outcome truth comes from GitHub milestone outcomes and versioned deterministic label rules.

Temporal features are computed as-of T-28/T-21/T-14/T-7 and must not use later events.

The old app/model remain historical V1 artifacts. M5 trains a new model only after M0-M4 data-quality checks pass.
