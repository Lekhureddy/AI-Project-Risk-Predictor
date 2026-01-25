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

DevOps and CI

This project uses a simple DevOps setup that fits a small, working prototype.

Docker is used to ensure the app runs the same way locally and in deployment.

GitHub Actions are configured for basic checks like dependency installation.

The live application is deployed using Streamlit Cloud.

This setup keeps things easy to maintain while still following good engineering practice.

Networking and Architecture

The system currently runs as a single-container application.

Flow overview:

Users access the app through a web browser.

The Streamlit app handles data preprocessing and model inference.

Trained model files (model.pkl, feature_columns.pkl) are loaded locally.

No external APIs are required during prediction.

More details are documented in:

NETWORKING_ARCHITECTURE.md

Java Decision Layer

The machine learning model produces:

a predicted project outcome

a numerical risk score

In real project environments, predictions are usually followed by simple business rules.

The Java module in java-risk-service/:

reads prediction output from a CSV file

applies rule-based logic

generates a decision label (GO / HOLD / ESCALATE)

adds a short explanation for the decision

This reflects how analytics outputs are commonly used in practice.

Power BI Reporting

Prediction results are visualized using Power BI dashboards for stakeholder review.

The dashboards include:

overall risk distribution

decision breakdown

risk score comparison

detailed table views for individual projects

Dashboard files and screenshots are available in:

powerbi/

Project Management (Jira)

Project planning and tracking were done using Jira with a simple Agile workflow.

Jira board (private):
https://lekhureddy-122.atlassian.net/jira/software/projects/KAN/boards/1

The board is private, which reflects real-world project environments.
Screenshots or walkthroughs can be shared if needed.

Product Perspective

This project was treated as a small product rather than just a model.

Key considerations:

clear problem definition

focus on non-technical users

simple and explainable outputs

separation of prediction, decision logic, and reporting

a realistic path for future improvements

Product-related notes are documented in:

PRODUCT_MANAGEMENT.md

Future Improvements

Possible next steps include:

API-based data ingestion instead of manual CSV uploads

storing historical results in a database for trend analysis

separating inference into a dedicated backend service

adding authentication and access control

basic monitoring for performance and model drift


