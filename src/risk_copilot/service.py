from __future__ import annotations

import json
import pickle
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from .challenge import challenge_assessment
from .demo import demo_assessments, demo_drivers, demo_evidence, demo_timeline
from .evidence import build_evidence_index
from .evidence_graph import build_evidence_graph, graph_payload
from .evaluation import evaluate_narrative
from .interventions import create_intervention
from .modeling import FEATURE_COLUMNS, risk_score_from_probabilities
from .portfolio import build_portfolio_summary
from .security import run_security_self_checks, sanitize_evidence
from .storage import SQLiteStore
from .timeline import build_risk_timeline, summarize_timeline
from .trust import build_trust_summary


class RiskCopilotService:
    def __init__(
        self,
        *,
        model_path: str = "artifacts/model/risk_model.pkl",
        model_report_path: str = "artifacts/model/model_report.json",
        db_path: str = "data/risk_copilot.db",
    ) -> None:
        self.model_path = Path(model_path)
        self.model_report_path = Path(model_report_path)
        self.store = SQLiteStore(db_path)
        self._model = None

    @property
    def model_available(self) -> bool:
        return self.model_path.exists()

    def load_model(self):
        if self._model is None:
            if not self.model_path.exists():
                raise FileNotFoundError("validated V2 model artifact is not available")
            with self.model_path.open("rb") as handle:
                self._model = pickle.load(handle)
        return self._model

    def model_report(self) -> dict:
        if not self.model_report_path.exists():
            return {"status": "not_validated"}
        return json.loads(self.model_report_path.read_text(encoding="utf-8"))

    def portfolio(self, *, demo: bool = False) -> dict:
        assessments = demo_assessments() if demo else self.store.list_assessments()
        return build_portfolio_summary(assessments)

    def assess_features(self, *, project_id: str, project_name: str, features: dict) -> dict:
        model = self.load_model()
        frame = pd.DataFrame([{k: features.get(k) for k in FEATURE_COLUMNS}])
        probabilities = model.predict_proba(frame)[0]
        classes = list(model.classes_)
        mapped = {str(label): float(probabilities[i]) for i, label in enumerate(classes)}
        score = risk_score_from_probabilities(mapped)
        if score >= 80:
            band = "Critical"
        elif score >= 60:
            band = "High"
        elif score >= 35:
            band = "Medium"
        else:
            band = "Low"

        assessment = {
            "assessment_id": str(uuid4()),
            "project_id": project_id,
            "project_name": project_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "risk_score": score,
            "risk_band": band,
            "probabilities": mapped,
            "features": {k: features.get(k) for k in FEATURE_COLUMNS},
            "source": "validated_model",
        }
        self.store.save_assessment(assessment)
        return assessment

    def project_detail(self, project_id: str, *, demo: bool = False) -> dict:
        if demo:
            assessments = [a for a in demo_assessments() if a["project_id"] == project_id]
            if not assessments:
                raise KeyError(project_id)
            latest = assessments[-1]
            timeline = build_risk_timeline(demo_timeline(project_id))
            evidence_items = sanitize_evidence(demo_evidence(project_id))
            drivers = demo_drivers() if project_id == "checkout-platform" else []
        else:
            assessments = self.store.list_assessments(project_id)
            if not assessments:
                raise KeyError(project_id)
            latest = assessments[-1]
            timeline = build_risk_timeline(assessments)
            evidence_items = latest.get("evidence") or []
            drivers = latest.get("drivers") or []

        graph = build_evidence_graph(
            project_id=project_id,
            project_label=latest.get("project_name") or project_id,
            evidence_items=evidence_items,
        )
        return {
            "latest": latest,
            "timeline": timeline,
            "timeline_summary": summarize_timeline(timeline),
            "drivers": drivers,
            "evidence": evidence_items,
            "evidence_graph": graph_payload(graph),
        }

    def challenge(self, *, drivers: list[dict], evidence_ids: list[str]) -> dict:
        remaining, result = challenge_assessment(
            drivers=drivers,
            challenged_evidence_ids=evidence_ids,
        )
        return {"drivers": remaining, "challenge": result}

    def record_intervention(
        self,
        *,
        assessment_id: str,
        recommendation: str,
        decision: str,
        risk_before: float,
        decision_reason: str | None = None,
    ) -> dict:
        intervention = create_intervention(
            assessment_id=assessment_id,
            recommendation=recommendation,
            decision=decision,
            risk_before=risk_before,
            decision_reason=decision_reason,
        )
        self.store.save_intervention(intervention)
        return intervention

    def trust_center(self, *, narrative_results: list[dict] | None = None, evidence: list[dict] | None = None) -> dict:
        evaluations = []
        if narrative_results and evidence is not None:
            index = build_evidence_index(evidence)
            evaluations = [evaluate_narrative(x, index).to_dict() for x in narrative_results]
        return build_trust_summary(
            model_report=self.model_report(),
            narrative_evaluations=evaluations,
            feedback=self.store.list_feedback(),
            security_checks=run_security_self_checks(),
        )
