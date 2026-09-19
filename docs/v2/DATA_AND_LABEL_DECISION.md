# V2 Data and Label Decision

**Status:** Accepted

V2 will not train on the legacy synthetic/product dataset or the human-authored risk-level field.

Outcome truth comes from real GitHub delivery outcomes and versioned deterministic label rules.

Temporal features are computed from historical snapshots and must not use later events.

The original application and model remain available as historical proof-of-concept artifacts while the new model is developed from the validated data pipeline.

Model training is allowed only after the dataset passes the documented quality gate.
