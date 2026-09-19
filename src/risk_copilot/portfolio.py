from __future__ import annotations

from collections import Counter
from typing import Iterable


def risk_band(score: float) -> str:
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def build_portfolio_summary(assessments: Iterable[dict]) -> dict:
    rows = [dict(x) for x in assessments]
    for row in rows:
        row["risk_score"] = float(row["risk_score"])
        row["risk_band"] = row.get("risk_band") or risk_band(row["risk_score"])
        row["risk_change"] = float(row.get("risk_change") or 0.0)

    ranked = sorted(rows, key=lambda r: (r["risk_score"], r["risk_change"]), reverse=True)
    bands = Counter(row["risk_band"] for row in rows)

    emerging = [
        row for row in ranked
        if row["risk_change"] >= 10 and row["risk_score"] >= 35
    ]

    return {
        "active_count": len(rows),
        "band_counts": {
            "Critical": bands.get("Critical", 0),
            "High": bands.get("High", 0),
            "Medium": bands.get("Medium", 0),
            "Low": bands.get("Low", 0),
        },
        "needs_attention": ranked[:10],
        "emerging_risks": emerging[:10],
    }
