from risk_copilot.agents.narrative import generate_verified_narrative
from risk_copilot.evaluation import evaluate_narrative
from risk_copilot.evidence import build_evidence_index


class FakeProvider:
    def generate(self, payload):
        return {
            "drivers": [
                {
                    "claim": "Review latency is increasing.",
                    "citations": [{"evidence_id": "PR-42", "quote": "waiting for four days"}],
                },
                {
                    "claim": "A fabricated blocker exists.",
                    "citations": [{"evidence_id": "ISSUE-404", "quote": "blocked"}],
                },
            ],
            "mitigations": ["Review the blocking work."],
            "confidence": "high",
            "what_would_change": "New evidence.",
            "abstained": False,
        }


def test_invalid_driver_is_dropped_before_display():
    evidence = build_evidence_index([
        {
            "evidence_id": "PR-42",
            "source_type": "pull_request",
            "title": "Payment retry logic",
            "url": "https://github.com/acme/demo/pull/42",
            "text": "This review has been waiting for four days and needs attention.",
        }
    ])

    result = generate_verified_narrative(FakeProvider(), {}, evidence)
    assert len(result["drivers"]) == 1
    assert result["drivers"][0]["claim"] == "Review latency is increasing."
    assert len(result["dropped_claims"]) == 1

    evaluation = evaluate_narrative(result, evidence)
    assert evaluation.schema_valid is True
    assert evaluation.citation_validity == 1.0
    assert evaluation.unsupported_driver_rate == 0.0
