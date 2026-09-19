# Risk Copilot — AI Project Risk Predictor

Risk Copilot is an evidence-oriented delivery intelligence project for identifying project risk early, explaining the signals behind that risk, and supporting human decision-making.

The repository is evolving from an earlier CSV-based prediction proof of concept into a system built around real engineering-delivery data, temporal features, measurable model quality, and later evidence-grounded AI explanations.

## Current status

The original Streamlit application remains available as a working proof of concept:

https://ai-project-risk-predictor-jhb6k9onjkannf7g5ugpqj.streamlit.app/

The new Risk Copilot pipeline is being built in parallel. It currently includes:

- GitHub REST data ingestion
- historical point-in-time snapshots
- deterministic project-outcome labels
- temporal engineering-delivery features
- data-quality gates
- automated functional tests and CI
- public-data smoke testing

The legacy synthetic dataset and human-authored risk field are not treated as training truth for the new model.

## Product direction

Risk Copilot is designed to answer four practical questions:

1. Which delivery targets need attention?
2. What signals are driving the risk?
3. What project evidence supports the assessment?
4. What actions could a manager evaluate before deciding?

The final application will combine predictive risk intelligence, risk trends, evidence-backed explanations, decision support, human feedback, and AI quality monitoring.

## Architecture

```text
GitHub engineering data
        |
        v
Temporal data pipeline
        |
        v
Quality and leakage checks
        |
        v
Calibrated risk model
        |
        v
Evidence-grounded AI layer
        |
        v
Risk Copilot web application
```

The V2 implementation lives primarily under:

```text
src/risk_copilot/
scripts/
tests/
docs/v2/
.github/workflows/
```

## Data integrity

Risk Copilot does not silently treat unavailable historical values as facts. Data provenance and training eligibility are recorded explicitly, and the predictive model is trained only after the dataset passes the quality gate.

See:

- `docs/v2/ARCHITECTURE.md`
- `docs/v2/DATA_CONTRACT.md`
- `docs/v2/DATA_QUALITY_GATE.md`
- `docs/v2/TEST_PLAN.md`
- `docs/v2/DATA_AND_LABEL_DECISION.md`

## Running tests

```bash
python -m pip install -r requirements-dev.txt
PYTHONPATH=src python -m pytest -q
```

## Building a public-data sample

Set an optional GitHub token for a higher API rate limit:

```bash
export GITHUB_TOKEN=your_token
```

Then run the dataset builder against a public repository:

```bash
PYTHONPATH=src python scripts/build_v2_dataset.py \
  --repo owner/repository \
  --out data/processed
```

Validate the resulting dataset before model training:

```bash
PYTHONPATH=src python scripts/validate_v2_dataset.py \
  data/processed/milestone_features.csv
```

## Legacy proof-of-concept assets

The following files belong to the earlier working prototype and are kept for reproducibility while the new application is developed:

- `app.py`
- `model.pkl`
- `feature_columns.pkl`
- `AI_BASED_PREDICATION.ipynb`
- `updated_report1.csv`
- `java-risk-service/`
- `powerbi/`

They should not be interpreted as the final Risk Copilot architecture or model-validation evidence.

## Technology

Python, Streamlit, pandas, scikit-learn, GitHub REST API, Docker, pytest, and GitHub Actions.

The project prioritizes free and open-source tooling where practical.
