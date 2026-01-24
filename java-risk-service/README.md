# Java Decision Rules (Post-Processing)

This folder contains a small Java program that adds a **decision layer** on top of the machine learning prediction output.

The goal of this step is to simulate how ML predictions are typically used in real projects — not directly, but through **simple business rules** that help teams decide what action to take.

---

## Why this Java step exists

The machine learning model predicts risk, but real-world systems usually need an extra layer to convert predictions into **clear actions**.

This Java program represents that layer by translating model outputs into:
- GO (safe to proceed)
- HOLD (monitor closely)
- ESCALATE (requires immediate attention)

This mirrors how project management and operations teams work in practice.

---

## What the ML model provides

The Python ML pipeline generates:
- **Predicted Outcome** (On Track / Delayed / Critical)
- **Risk Score** (0–100)

These values are written to a CSV file and passed to this Java program.

---

## Input file

**File name:**  
`sample_input_predictions.csv`

**Required columns:**
- `Predicted Outcome`
- `Risk Score`

Each row represents one project or task prediction.

---

## Output file

**File name:**  
`sample_output_decisions.csv`

**Columns generated:**
- `Predicted Outcome`
- `Risk Score`
- `Decision` (GO / HOLD / ESCALATE)
- `Reason` (short explanation for the decision)

This output file is later used for reporting and visualization (for example, in Power BI).

---

## Decision rules used

The decision logic is intentionally kept simple so that results are easy to understand and explain to non-technical stakeholders.

- If the **Predicted Outcome** is `Critical` → **ESCALATE**
- Else if the **Risk Score** is `60 or higher` → **HOLD**
- Else → **GO**

These rules act as a basic business policy layer that sits on top of the ML model.

---

## How to run

Open a terminal inside the `java-risk-service/` folder and run:

```bash
javac RiskDecisionEngine.java
java RiskDecisionEngine sample_input_predictions.csv sample_output_decisions.csv
