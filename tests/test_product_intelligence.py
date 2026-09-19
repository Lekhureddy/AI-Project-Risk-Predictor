from risk_copilot.evidence import build_evidence_index
from risk_copilot.timeline import build_risk_timeline, summarize_timeline


def test_timeline_and_evidence_index():
    points = build_risk_timeline([
        {"timestamp": "2026-01-01T00:00:00Z", "risk_score": 31},
        {"timestamp": "2026-01-08T00:00:00Z", "risk_score": 52},
        {"timestamp": "2026-01-15T00:00:00Z", "risk_score": 78},
    ])
    summary = summarize_timeline(points)

    assert summary["direction"] == "worsening"
    assert summary["net_change"] == 47.0
    assert points[-1]["risk_band"] == "High"

    index = build_evidence_index([
        {
            "evidence_id": "PR-42",
            "source_type": "pull_request",
            "title": "Payment retry logic",
            "url": "https://github.com/acme/demo/pull/42",
            "text": "Review has been waiting for four days.",
        }
    ])
    assert index["PR-42"]["source_type"] == "pull_request"


def test_timeline_accepts_saved_assessment_created_at():
    points = build_risk_timeline([
        {
            "created_at": "2026-09-19T22:00:00+00:00",
            "risk_score": 19.54,
        }
    ])
    assert len(points) == 1
    assert points[0]["risk_score"] == 19.54
    assert points[0]["risk_band"] == "Low"


def test_timeline_skips_malformed_legacy_record_instead_of_crashing():
    points = build_risk_timeline([
        {"risk_score": 40},
        {
            "created_at": "2026-09-19T22:00:00+00:00",
            "risk_score": 55,
        },
    ])
    assert len(points) == 1
    assert points[0]["risk_score"] == 55
