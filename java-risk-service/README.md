# Java Decision Rules (Post-Processing)

This folder contains a small Java program that adds a simple “decision step” on top of the ML prediction output.

The ML model gives:
- Predicted Outcome
- Risk Score

This Java step converts that into:
- Decision: GO / HOLD / ESCALATE
- Reason: a short explanation

I added this because in real projects, predictions are usually followed by business rules before taking action.

---

## Input file
`sample_input_predictions.csv`

Required columns:
- Predicted Outcome
- Risk Score

---

## How to run

Open a terminal inside `java-risk-service/` and run:

```bash
javac RiskDecisionEngine.java
java RiskDecisionEngine sample_input_predictions.csv sample_output_decisions.csv
