from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from risk_copilot.modeling import FEATURE_COLUMNS
from risk_copilot.service import RiskCopilotService
from risk_copilot.simulation import simulate_scenario


app = FastAPI(
    title="Risk Copilot API",
    version="2.0",
    description="Evidence-oriented project delivery risk intelligence.",
)
service = RiskCopilotService()


class AssessmentRequest(BaseModel):
    project_id: str = Field(min_length=1, max_length=200)
    project_name: str = Field(min_length=1, max_length=300)
    features: dict[str, float | int | None]


class ChallengeRequest(BaseModel):
    drivers: list[dict[str, Any]]
    evidence_ids: list[str]


class ScenarioRequest(BaseModel):
    current_features: dict[str, float | int | None]
    changes: dict[str, float]


class FeedbackRequest(BaseModel):
    assessment_id: str
    verdict: Literal["agree", "disagree"]
    note: str | None = None


class InterventionRequest(BaseModel):
    assessment_id: str
    recommendation: str
    decision: Literal["accepted", "modified", "rejected"]
    risk_before: float = Field(ge=0, le=100)
    decision_reason: str | None = None


@app.get("/health")
def health():
    return {"status": "ok", "model_available": service.model_available}


@app.get("/portfolio")
def portfolio(demo: bool = False):
    return service.portfolio(demo=demo)


@app.get("/projects/{project_id}")
def project(project_id: str, demo: bool = False):
    try:
        return service.project_detail(project_id, demo=demo)
    except KeyError:
        raise HTTPException(status_code=404, detail="project not found")


@app.post("/assess")
def assess(request: AssessmentRequest):
    unknown = sorted(set(request.features) - set(FEATURE_COLUMNS))
    if unknown:
        raise HTTPException(status_code=422, detail={"unsupported_features": unknown})
    try:
        return service.assess_features(
            project_id=request.project_id,
            project_name=request.project_name,
            features=request.features,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.post("/challenge")
def challenge(request: ChallengeRequest):
    return service.challenge(drivers=request.drivers, evidence_ids=request.evidence_ids)


@app.post("/simulate")
def simulate(request: ScenarioRequest):
    try:
        model = service.load_model()
        return simulate_scenario(model, request.current_features, request.changes)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post("/feedback")
def feedback(request: FeedbackRequest):
    service.store.save_feedback(
        assessment_id=request.assessment_id,
        verdict=request.verdict,
        note=request.note,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    return {"status": "recorded"}


@app.post("/interventions")
def intervention(request: InterventionRequest):
    return service.record_intervention(**request.model_dump())


@app.get("/trust")
def trust():
    return service.trust_center()
