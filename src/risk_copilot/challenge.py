from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Iterable


@dataclass(frozen=True)
class ChallengeResult:
    challenged_evidence_ids: list[str]
    remaining_driver_count: int
    removed_driver_count: int
    predictive_score_changed: bool
    note: str
    created_at: str


def challenge_assessment(
    *,
    drivers: Iterable[dict],
    challenged_evidence_ids: Iterable[str],
) -> tuple[list[dict], dict]:
    challenged = {str(x) for x in challenged_evidence_ids}
    remaining = []
    removed = []

    for driver in drivers:
        citations = driver.get("citations") or []
        cited_ids = {str(c.get("evidence_id")) for c in citations}
        if cited_ids & challenged:
            removed.append(driver)
        else:
            remaining.append(driver)

    result = ChallengeResult(
        challenged_evidence_ids=sorted(challenged),
        remaining_driver_count=len(remaining),
        removed_driver_count=len(removed),
        predictive_score_changed=False,
        note=(
            "The evidence-backed narrative was revised. The predictive score remains unchanged "
            "because no model input was modified. Use the Decision Lab for explicit feature scenarios."
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    return remaining, asdict(result)
