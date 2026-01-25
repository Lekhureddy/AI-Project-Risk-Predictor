# AI Project Risk Predictor

This repository contains an end-to-end project that predicts project risk from historical data and presents the results in a form that is easy to understand and act on.  
The project is designed as a practical decision-support tool rather than a research-focused model.

A simple web interface allows users to upload project data and receive a predicted outcome, a risk score, and a clear recommended action.

---

## Live Application

Streamlit App:  
https://ai-project-risk-predictor-jhb6k9onjkannf7g5ugpqj.streamlit.app/

---

## Problem Context

Project risks are often identified late, after delays or failures have already occurred.  
Status updates are usually spread across spreadsheets, tools, and meetings, making early risk detection difficult and inconsistent.

This project was built to answer one key question:

Which projects need attention right now, and why?

---

## What the Application Does

1. Users upload a CSV file containing project metrics.
2. The data is preprocessed to match the training feature schema.
3. A machine learning model predicts the project outcome.
4. A risk score (0–100) is calculated from prediction confidence.
5. Each record is assigned a risk band and a recommended action.
6. Results can be filtered and downloaded as CSV files.

---

## Outputs

- Predicted Outcome (On Track / Delayed / Critical)
- Risk Score (0–100)
- Risk Band (Low / Medium / High)
- Recommended Action (plain-language guidance)

---

## Project Structure

- `app.py`  
  Streamlit application for file upload, preprocessing, prediction, filtering, and downloads.

- `model.pkl`  
  Trained machine learning model used for inference.

- `feature_columns.pkl`  
  Feature list used during training to align uploaded data before prediction.

- `AI_BASED_PREDICATION.ipynb`  
  Notebook used during model development and experimentation.

- `updated_report1.csv`  
  Sample dataset used for testing and demonstration.

- `java-risk-service/`  
  Java-based post-processing step that converts model predictions into decision labels (GO / HOLD / ESCALATE).  
  Includes sample input/output CSV files and a folder-level README.

- `powerbi/`  
  Power BI dashboards and screenshots built using the prediction output.

- `NETWORKING_ARCHITECTURE.md`  
  Documentation explaining system architecture and data flow.

- `Dockerfile`, `.dockerignore`  
  Docker configuration for consistent local and containerized runs.

- `.github/workflows/`  
  GitHub Actions workflow used for basic CI checks.

- `PRODUCT_MANAGEMENT.md`  
  Product management documentation covering users, decisions, metrics, and roadmap.

---

## Running the Application Locally

Install dependencies:

```bash
pip install -r requirements.txt

---

## Docker (Local Run)

Build the image:

```bash
docker build -t ai-project-risk-predictor .


