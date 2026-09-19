from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Iterable


@dataclass(frozen=True)
class TimelinePoint:
    timestamp: str
    risk_score: float
    risk_band: str
    change_from_previous: float | None


def risk_band(score: float) -> str:
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def _timestamp_for(item: dict) -> str:
    """
    Accept all timestamp fields produced by Risk Copilot.

    Saved assessments use created_at; historical research rows may use
    snapshot_date; timeline-only demo records may use timestamp.
    """
    return str(
        item.get("timestamp")
        or item.get("snapshot_date")
        or item.get("created_at")
        or ""
    )


def build_risk_timeline(assessments: Iterable[dict]) -> list[dict]:
    rows = []
    for item in assessments:
        timestamp = _timestamp_for(item)
        if not timestamp:
            # Skip malformed legacy records instead of crashing the entire
            # Project Intelligence page.
            continue
        score = float(item["risk_score"])
        rows.append((datetime.fromisoformat(timestamp.replace("Z", "+00:00")), timestamp, score))

    rows.sort(key=lambda x: x[0])
    result = []
    previous = None
    for _, timestamp, score in rows:
        delta = None if previous is None else round(score - previous, 2)
        point = TimelinePoint(
            timestamp=timestamp,
            risk_score=round(score, 2),
            risk_band=risk_band(score),
            change_from_previous=delta,
        )
        result.append(asdict(point))
        previous = score
    return result


def summarize_timeline(points: list[dict]) -> dict:
    if not points:
        return {"direction": "unknown", "net_change": None, "largest_increase": None}

    net_change = round(points[-1]["risk_score"] - points[0]["risk_score"], 2)
    if net_change >= 5:
        direction = "worsening"
    elif net_change <= -5:
        direction = "improving"
    else:
        direction = "stable"

    increases = [p for p in points if p["change_from_previous"] is not None]
    largest = max(increases, key=lambda p: p["change_from_previous"], default=None)
    return {
        "direction": direction,
        "net_change": net_change,
        "largest_increase": largest,
    }
