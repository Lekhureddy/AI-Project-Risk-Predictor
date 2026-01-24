# AI Project Risk Predictor

The AI Project Risk Predictor is a decision-support application built to help project teams identify risk early and take timely action.  
Instead of relying only on manual status updates or subjective assessments, this tool uses historical project data to predict outcomes and recommend next steps.

The focus of this project is not only prediction accuracy, but practical usability for project managers and stakeholders.

---

## Why This Project Exists

In many organizations, project risks are identified only after delays or issues occur.  
Project status is often tracked manually using spreadsheets, meetings, or dashboards that require constant interpretation.

This project was created to answer a simple question:

Which projects need attention right now, and why?

---

## What the Application Does

Users upload a CSV file containing project-related metrics.  
The system then generates:

- A predicted project outcome (On Track / Delayed / Critical)
- A numerical risk score (0–100)
- A recommended action (GO / HOLD / ESCALATE)
- A short explanation supporting the recommendation

The application is deployed and accessible through a simple web interface.

Live Application:  
https://ai-project-risk-predictor-jhb6k9onjkannf7g5ugpqj.streamlit.app/

---

## Machine Learning Approach

A supervised machine learning model is used to analyze historical project data and identify patterns associated with project risk.

- Model type: Random Forest Classifier  
- Input: Project performance metrics  
- Output: Predicted project outcome  
- Risk score: Derived from prediction confidence  

The trained model is stored as `model.pkl` and loaded at runtime.

---

## System Flow (High Level)

1. Project data is uploaded through the web interface  
2. The machine learning model predicts outcome and risk score  
3. A Java-based decision layer converts predictions into actions  
4. Results are exported in a structured format  
5. Power BI dashboards visualize outcomes for stakeholders  

This separation keeps the system modular and easy to extend.

---

## Reporting and Visualization (Power BI)

Prediction results are visualized using Power BI dashboards designed for non-technical users.

The dashboards provide:
- A high-level overview of project risk
- Decision distribution (GO / HOLD / ESCALATE)
- Risk score comparisons
- A detailed drill-down view with explanations

Power BI files and screenshots are available in the `powerbi/` folder.

---

## Java Decision Layer

A lightweight Java module is included to simulate a business decision layer that typically follows machine learning predictions.

The Java program:
- Reads prediction results from a CSV file
- Applies simple rule-based logic
- Generates a clean output file for reporting and visualization

Details are available in the `java-risk-service/` folder.

---

## Project Management and Workflow

Project planning and tracking were done using Jira, following Agile practices.

Jira was used to manage:
- Epics and user stories
- Tasks and sprint planning
- Risk tracking and status updates

Jira Board (Private):  
https://lekhureddy-122.atlassian.net/jira/software/projects/KAN/boards/1

Note: The Jira board is private, which reflects real-world industry usage.  
Screenshots or walkthroughs can be shared upon request.

---

## Product Management Perspective

This project was developed with a product mindset rather than as a standalone technical exercise.

Key considerations included:
- Clear problem definition
- Focus on stakeholder usability
- Simple and explainable decision outputs
- Separation of prediction, decision logic, and reporting
- A realistic roadmap for future improvements

Full product documentation is available in `PRODUCT_MANAGEMENT.md`.

---

## Technology Stack

- Python (machine learning pipeline)
- Pandas, NumPy, Scikit-learn
- Streamlit (web interface)
- Java (decision rules)
- Power BI (visualization)
- Docker and GitHub Actions (DevOps)
- Jira (project management)

---

## Future Improvements

Planned enhancements include:
- Pulling live project data directly from Jira APIs
- Storing historical results in a database
- Tracking risk trends over time
- Supporting multiple teams and projects
- Adding authentication and access control

---

## Summary

This project demonstrates an end-to-end approach to building an AI-assisted decision-support system, from data modeling and prediction to business logic, visualization, and product planning.

It reflects how analytics-driven tools are built and used in real project management environments.
