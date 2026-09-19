# Deployment

Risk Copilot can be run as a Streamlit web application, a FastAPI service, or both.

## Local application

```bash
python -m pip install -r requirements-dev.txt
PYTHONPATH=src streamlit run app.py
```

## API

```bash
PYTHONPATH=src uvicorn api.main:app --host 0.0.0.0 --port 8000
```

The API health endpoint is `/health` and interactive OpenAPI documentation is `/docs`.

## Docker Compose

```bash
docker compose up --build
```

This starts the web application on port 8501 and the API on port 8000 with shared persistent SQLite storage.

## Streamlit Community Cloud

The root `app.py` remains the Streamlit entry point. The application automatically uses demo mode when no validated model artifact is present. Demo data is explicitly labeled and is not presented as measured performance.

## Model artifact

A validated model should be placed at:

`artifacts/model/risk_model.pkl`

with its generated report at:

`artifacts/model/model_report.json`

Until those artifacts exist, real assessment and Decision Lab inference are intentionally disabled.

## Production hardening

For an enterprise deployment, use managed PostgreSQL instead of SQLite, a secret manager, SSO/RBAC, encrypted persistent storage, centralized audit logs, and a production API/web hosting platform.
