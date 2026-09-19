# Data Quality Gate

The predictive model is not trained merely because a CSV exists. The dataset must pass a reproducible quality gate first.

## Blocking checks

- enough rows for a meaningful experiment
- enough independent repositories
- enough rows marked safe for training
- no duplicate project/snapshot identities
- no missing required identity, time, provenance, label, or eligibility fields
- at least two supported outcome classes represented

## Warning checks

- high feature missingness
- unresolved/unknown labels
- incomplete historical membership reconstruction
- concentration in one due-date provenance source

Thresholds are command-line parameters so experiments can be explicit instead of silently changing the definition of acceptable data.

## Why this exists

A model trained on sparse, duplicate, temporally contaminated, or provenance-unclear data can produce attractive metrics without being trustworthy. This gate intentionally stops model work when the data foundation is not defensible.
