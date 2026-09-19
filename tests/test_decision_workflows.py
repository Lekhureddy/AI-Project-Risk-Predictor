from risk_copilot.challenge import challenge_assessment
from risk_copilot.interventions import close_intervention, create_intervention
from risk_copilot.portfolio import build_portfolio_summary


def test_challenge_removes_driver_without_faking_model_change():
    drivers = [
        {"claim": "review delay", "citations": [{"evidence_id": "PR-9", "quote": "waiting"}]},
        {"claim": "scope growth", "citations": [{"evidence_id": "ISSUE-4", "quote": "added"}]},
    ]
    remaining, result = challenge_assessment(
        drivers=drivers,
        challenged_evidence_ids=["PR-9"],
    )

    assert len(remaining) == 1
    assert result["removed_driver_count"] == 1
    assert result["predictive_score_changed"] is False


def test_intervention_records_observed_outcome_without_causal_claim():
    record = create_intervention(
        assessment_id="A-1",
        recommendation="Increase review capacity",
        decision="accepted",
        risk_before=78,
    )
    closed = close_intervention(record, risk_after=55, actual_outcome="On Track")
    assert closed["observed_risk_change"] == -23.0
    assert closed["causal_claim_allowed"] is False


def test_portfolio_ranks_attention_and_emerging_risk():
    summary = build_portfolio_summary([
        {"project_id": "A", "risk_score": 82, "risk_change": 4},
        {"project_id": "B", "risk_score": 66, "risk_change": 18},
        {"project_id": "C", "risk_score": 22, "risk_change": -3},
    ])
    assert summary["band_counts"]["Critical"] == 1
    assert summary["needs_attention"][0]["project_id"] == "A"
    assert summary["emerging_risks"][0]["project_id"] == "B"
