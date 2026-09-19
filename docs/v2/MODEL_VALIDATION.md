# Predictive Model Validation

The predictive engine is designed to answer a narrow question: given only information available before a delivery target's due date, how much evidence is there that the target will finish on time, finish late, or become severely delayed?

## Validation design

Repository groups are kept separate between training and test data. This prevents snapshots from the same repository appearing on both sides of evaluation.

The first comparison includes:

- majority-class baseline
- class-balanced logistic regression
- histogram gradient boosting

The model is selected using held-out macro F1, then probability calibration is fitted on training data. Model quality is reported rather than assumed.

## Risk score

The application score represents expected delivery severity, not prediction confidence:

`100 × (0.5 × P(Delayed) + P(Critical))`

A highly confident On Track prediction therefore produces a low risk score rather than a misleading high score.

## Training gate

Training is blocked when the data-quality report contains blocking issues. A model artifact is not produced just because a dataset file exists.

## Reported outputs

The training report includes:

- macro F1
- macro precision and recall
- confusion matrix
- per-class classification metrics
- per-class and mean Brier score when probabilities are available
- baseline comparison
- training/test row counts
- repository separation

Model performance claims must come from this generated report.
