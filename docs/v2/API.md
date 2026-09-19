# Risk Copilot API

The FastAPI service exposes the application logic independently from the Streamlit interface.

## Core routes

- `GET /health` — service and validated-model availability
- `GET /portfolio` — portfolio risk summary
- `GET /projects/{project_id}` — project timeline, drivers, evidence, and graph
- `POST /assess` — validated-model assessment
- `POST /challenge` — remove challenged evidence from narrative review
- `POST /simulate` — non-causal what-if model scenario
- `POST /feedback` — human agree/disagree feedback
- `POST /interventions` — record human intervention decisions
- `GET /trust` — model, AI, security, and feedback quality summary

OpenAPI documentation is available automatically at `/docs` when the API server is running.
