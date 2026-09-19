# Risk Copilot

Risk Copilot is an evidence-grounded delivery intelligence application for engineering teams. It combines project-risk prediction, risk trends, verifiable project evidence, human challenge workflows, scenario analysis, intervention tracking, and AI quality monitoring.

The product is designed to answer:

1. Which delivery targets need attention?
2. Why is the risk changing?
3. What project evidence supports the assessment?
4. What options can a manager evaluate?
5. How trustworthy is the model and AI explanation?

## Live application

The existing Streamlit deployment remains the public entry point:

https://ai-project-risk-predictor-jhb6k9onjkannf7g5ugpqj.streamlit.app/

The application automatically uses clearly labeled demo mode when a validated V2 model artifact is not available. Demo records are never presented as measured production performance.

## Product capabilities

### Portfolio intelligence

- risk-ranked project view
- current risk band and score
- emerging-risk detection
- portfolio-level attention queue

### Project intelligence

- historical risk timeline
- model-grounded risk drivers
- issue / pull-request evidence
- evidence graph
- challenge workflow for stale or disputed evidence

### Decision support

- what-if feature scenarios
- explicit non-causal scenario disclaimer
- intervention accept / modify / reject workflow
- observed before / after outcome tracking

### AI layer

- provider abstraction
- optional local Ollama structured-output provider
- deterministic zero-cost fallback
- strict structured output
- citation verification
- unsupported-claim removal
- abstention path
- prompt-injection-aware evidence handling

### Trust and safety

- data quality gates
- repository-grouped model validation
- calibration / Brier reporting
- citation-validity evaluation
- PII and secret redaction
- adversarial test cases
- Promptfoo red-team configuration
- human feedback collection
- AI Trust Center

## Data pipeline

```text
GitHub REST
    |
    v
Milestones / issues / PRs / events / reviews / commits
    |
    v
Historical point-in-time reconstruction
    |
    v
Data-quality and leakage gates
    |
    v
Outcome labels + engineering features
    |
    v
Baseline comparison + calibrated model
    |
    v
Risk score / timeline / explanations
    |
    v
Verified evidence + decision workflows
```

The legacy CSV model and human-authored risk field are not treated as training truth for the V2 model.

## Application architecture

```text
Streamlit Web UI
      |
      +----------------------+
      |                      |
      v                      v
Risk Copilot Service     FastAPI
      |                      |
      +----------+-----------+
                 |
     +-----------+-----------+
     |           |           |
 Prediction   Evidence    Decisions
     |           |           |
     +-----------+-----------+
                 |
              SQLite
```

SQLite is intentionally used for the free demo / local build. The documented enterprise path replaces it with managed PostgreSQL and adds SSO/RBAC, tenant isolation, centralized audit logging, and retention controls.

## Repository structure

```text
app.py                         Streamlit product UI
api/                           FastAPI service
src/risk_copilot/              Core product logic
scripts/                       Data and training commands
configs/                       Decision policy and public research cohort
evals/                         AI evaluation / red-team assets
tests/                         Functional and integration tests
docs/v2/                       Architecture, security, model and deployment docs
.github/workflows/             CI and research-data validation
Dockerfile                     Web container
Dockerfile.api                 API container
docker-compose.yml             Local full stack
```

## Quick start

```bash
python -m pip install -r requirements-dev.txt
PYTHONPATH=src streamlit run app.py
```

API:

```bash
PYTHONPATH=src uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Full local stack:

```bash
docker compose up --build
```

## Tests

```bash
PYTHONPATH=src python -m pytest -q
```

CI additionally smoke-tests both the API and Streamlit application and builds both Docker images.

## Public-data research

The repository includes a multi-repository GitHub research cohort builder and automated data-quality report.

```bash
PYTHONPATH=src python scripts/build_research_cohort.py --out data/research
```

The model training command refuses to proceed when the dataset quality gate contains blocking issues.

## Model status

A **research/demo model artifact** is now generated from the public GitHub cohort and committed with its machine-generated report. It is intentionally marked `production_approved: false`.

The current research dataset is small and uses documented historical proxies where GitHub does not expose complete history. The Trust Center displays the measured metrics and limitations rather than presenting the model as enterprise-production validated.

See:

- `docs/v2/MODEL_CARD.md`
- `docs/v2/MODEL_VALIDATION.md`
- `docs/v2/DATA_QUALITY_GATE.md`

## Documentation

- `docs/v2/ARCHITECTURE.md`
- `docs/v2/API.md`
- `docs/v2/SECURITY.md`
- `docs/v2/DECISION_INTELLIGENCE.md`
- `docs/v2/DEPLOYMENT.md`
- `docs/v2/TEST_PLAN.md`

## Legacy proof of concept

The repository still contains the earlier CSV-based artifacts for historical reproducibility. They are not the current Risk Copilot product architecture and should not be used as evidence of V2 model performance.

## Product principle

Risk Copilot is decision support, not an autonomous project manager.

The model predicts. The system explains and verifies. The human decides.
