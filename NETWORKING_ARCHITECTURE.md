# Networking & System Architecture  
## AI Project Risk Predictor

This document explains how the AI Project Risk Predictor is structured from a system and networking perspective.  
The focus is on keeping the architecture simple, practical, and aligned with how early-stage AI products are typically built and deployed.

---

## System Architecture Diagram
![System Architecture](architecture_diagram.png)

---

## Networking & Communication Flow (Actual Implementation)

The current version of this project runs as a **single-container application**.  
The networking design is intentionally kept minimal to make the system easy to deploy, test, and maintain.

- Users interact with the application through a web browser.
- Communication between the browser and the application happens over HTTPS.
- The Streamlit application runs inside a Docker container and listens on a configurable port (default: **8501**).
- All data preprocessing, model inference, and result generation happen within the same container.
- Model artifacts (`model.pkl` and `feature_columns.pkl`) are loaded locally at runtime.
- No external APIs are called during inference.

This approach was chosen to:
- Keep latency low
- Avoid unnecessary network complexity
- Simplify CI validation and deployment

In future iterations, the inference logic could be separated into a dedicated service if scalability requirements increase.

---

## 1. High-Level Goal

The goal of this project is to provide an **AI-driven project risk prediction tool** that helps teams understand delivery risk early.

Users upload a project dataset (CSV), and the system returns:
- Predicted project outcome (On Track / Delayed / Critical)
- Risk score (0–100)
- Risk level (Low / Medium / High)
- A recommended action based on the risk level

---

## 2. Architecture Overview (Client–Server Model)

### Client (User Browser)
- Accesses the Streamlit web interface over HTTPS
- Uploads project CSV files
- Views predictions and downloads result files

### Server (Streamlit Application)
- Hosts the user interface and prediction logic (`app.py`)
- Loads trained model artifacts (`model.pkl`, `feature_columns.pkl`)
- Preprocesses uploaded data to match the training feature set
- Generates predictions, risk scores, and recommendations

### Artifacts & Outputs
- Model artifacts are bundled with the application
- Prediction results are available for download as CSV files

---

## 3. End-to-End Data Flow

1. **Access**
   - User opens the application URL (local Docker or Streamlit Cloud).
   - A secure HTTPS connection is established.

2. **Upload**
   - User uploads a CSV file through the UI.
   - The file is sent to the server over HTTPS.

3. **Preprocessing**
   - Data is read into pandas.
   - Categorical variables are encoded.
   - Missing columns required by the trained model are added.
   - Column order is aligned using `feature_columns.pkl`.

4. **Prediction**
   - The trained model generates outcome predictions.
   - Probability scores are used to calculate a risk score.

5. **Results**
   - Results are displayed in the UI.
   - Users can download the prediction output as a CSV file.

---

## 4. Ports, Protocols, and Security

### Ports & Protocols
- **HTTPS (443)**: Used when deployed via Streamlit Cloud
- **HTTP (8501)**: Used for local Docker execution

### Security Considerations
- Data is encrypted in transit using HTTPS
- No authentication is required in the current prototype
- Production-ready improvements could include:
  - Authentication (SSO / OAuth)
  - Role-based access control
  - File size limits and input validation
  - Secure handling of secrets via environment variables

---

## 5. Deployment & CI Networking

### Docker
- The application is containerized using Docker.
- Port **8501** is exposed and bound to `0.0.0.0` inside the container.
- This ensures consistent behavior across environments.

### GitHub Actions (CI)
- CI pipelines validate dependency installation
- Required files are checked before builds
- Docker image builds are tested automatically
- This reduces deployment failures caused by missing artifacts or configuration issues

---

## 6. Scalability & Reliability (Future Enhancements)

For larger usage scenarios involving multiple teams or projects, the following improvements could be considered:

- Introduce a backend API layer (e.g., FastAPI) behind a load balancer
- Store model artifacts in an object store
- Cache repeated inference requests
- Add monitoring for latency, error rates, and data drift
- Persist prediction results in a SQL database or data warehouse to support historical analysis and reporting

These enhancements are not part of the current implementation but represent a natural evolution path.

---

## 7. Integrations Used and Planned

### Jira (Project Tracking)

Jira was used to manage tasks, risks, and workflow states such as *Planned*, *In Progress*, *At Risk*, and *Completed*.  
Although the system does not directly pull data via Jira APIs, the prediction outputs are designed to align with Jira-style project tracking and risk categorization.

This makes it easier to conceptually map AI predictions to Jira issues and project boards.

---

### Power BI (Reporting & Visualization)

Prediction outputs generated by the application are exported as CSV files and used in Power BI dashboards.

Power BI dashboards are used to visualize:
- Overall project risk distribution
- High-risk versus low-risk project counts
- Risk trends and summary metrics
- Recommendation insights for stakeholders

This allows non-technical users to monitor project health without interacting directly with the ML application.

---

## Summary

The system architecture reflects a **practical, early-stage AI product design**:
- Simple client-server communication
- Containerized deployment
- Clear separation between inference, reporting, and future scalability

The design prioritizes clarity, maintainability, and realistic production readiness over unnecessary complexity.
