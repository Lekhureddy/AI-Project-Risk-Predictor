from __future__ import annotations

from collections import Counter
from statistics import mean


def build_trust_summary(
    *,
    model_report: dict | None = None,
    narrative_evaluations: list[dict] | None = None,
    feedback: list[dict] | None = None,
    security_checks: list[dict] | None = None,
) -> dict:
    model_report = model_report or {}
    narrative_evaluations = narrative_evaluations or []
    feedback = feedback or []
    security_checks = security_checks or []

    citation_values = [
        float(x["citation_validity"])
        for x in narrative_evaluations
        if x.get("citation_validity") is not None
    ]
    unsupported_values = [
        float(x["unsupported_driver_rate"])
        for x in narrative_evaluations
        if x.get("unsupported_driver_rate") is not None
    ]
    verdicts = Counter(str(x.get("verdict")) for x in feedback)
    security_passed = sum(bool(x.get("passed")) for x in security_checks)

    return {
        "predictive_model": {
            "status": model_report.get("status", "not_validated"),
            "selected_model": model_report.get("selected_model"),
            "macro_f1": (model_report.get("calibrated_metrics") or {}).get("macro_f1"),
            "mean_brier": (model_report.get("calibrated_metrics") or {}).get("mean_brier"),
            "baseline_macro_f1": model_report.get("baseline_macro_f1"),
            "lift_vs_baseline": model_report.get("macro_f1_lift_vs_majority"),
        },
        "generative_ai": {
            "evaluation_count": len(narrative_evaluations),
            "citation_validity": round(mean(citation_values), 4) if citation_values else None,
            "unsupported_driver_rate": round(mean(unsupported_values), 4) if unsupported_values else None,
        },
        "human_feedback": {
            "agree": verdicts.get("agree", 0),
            "disagree": verdicts.get("disagree", 0),
            "total": len(feedback),
        },
        "security": {
            "checks_total": len(security_checks),
            "checks_passed": security_passed,
            "all_passed": bool(security_checks) and security_passed == len(security_checks),
        },
    }
