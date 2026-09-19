from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

Decision = Literal["accepted", "modified", "rejected"]


@dataclass(frozen=True)
class Intervention:
    intervention_id: str
    assessment_id: str
    recommendation: str
    decision: Decision
    decision_reason: str | None
    risk_before: float
    created_at: str
    risk_after: float | None = None
    actual_outcome: str | None = None


def create_intervention(
    *,
    assessment_id: str,
    recommendation: str,
    decision: Decision,
    risk_before: float,
    decision_reason: str | None = None,
) -> dict:
    if decision not in {"accepted", "modified", "rejected"}:
        raise ValueError("decision must be accepted, modified, or rejected")
    record = Intervention(
        intervention_id=str(uuid4()),
        assessment_id=assessment_id,
        recommendation=recommendation,
        decision=decision,
        decision_reason=decision_reason,
        risk_before=float(risk_before),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    return asdict(record)


def close_intervention(record: dict, *, risk_after: float, actual_outcome: str) -> dict:
    updated = dict(record)
    updated["risk_after"] = float(risk_after)
    updated["actual_outcome"] = str(actual_outcome)
    updated["observed_risk_change"] = round(float(risk_after) - float(record["risk_before"]), 2)
    updated["causal_claim_allowed"] = False
    return updated
