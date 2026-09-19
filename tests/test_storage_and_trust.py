from pathlib import Path

from risk_copilot.storage import SQLiteStore
from risk_copilot.trust import build_trust_summary


def test_sqlite_store_round_trip(tmp_path: Path):
    store = SQLiteStore(str(tmp_path / "risk.db"))
    assessment = {
        "assessment_id": "A1",
        "project_id": "P1",
        "created_at": "2026-01-01T00:00:00Z",
        "risk_score": 72,
        "risk_band": "High",
    }
    store.save_assessment(assessment)
    assert store.list_assessments("P1")[0]["assessment_id"] == "A1"

    store.save_feedback(
        assessment_id="A1",
        verdict="agree",
        note="useful",
        created_at="2026-01-01T01:00:00Z",
    )
    assert store.list_feedback()[0]["verdict"] == "agree"


def test_trust_center_never_invents_missing_model_metrics():
    result = build_trust_summary(
        model_report={"status": "not_validated"},
        narrative_evaluations=[],
        feedback=[],
        security_checks=[{"name": "read_only", "passed": True}],
    )
    assert result["predictive_model"]["macro_f1"] is None
    assert result["predictive_model"]["status"] == "not_validated"
    assert result["security"]["all_passed"] is True
