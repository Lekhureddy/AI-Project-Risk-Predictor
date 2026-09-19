from __future__ import annotations

from dataclasses import dataclass, asdict

from .agents.narrative import validate_narrative_schema
from .evidence import verify_citation


@dataclass(frozen=True)
class NarrativeEvaluation:
    schema_valid: bool
    driver_count: int
    citation_count: int
    valid_citation_count: int
    citation_validity: float
    unsupported_driver_count: int
    unsupported_driver_rate: float
    abstained: bool

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_narrative(result: dict, evidence_index: dict[str, dict]) -> NarrativeEvaluation:
    schema_valid, _ = validate_narrative_schema(result)
    drivers = result.get("drivers") if isinstance(result.get("drivers"), list) else []

    citation_count = 0
    valid_count = 0
    unsupported = 0

    for driver in drivers:
        citations = driver.get("citations") or []
        if not citations:
            unsupported += 1
            continue
        driver_valid = True
        for citation in citations:
            citation_count += 1
            ok, _ = verify_citation(citation, evidence_index)
            valid_count += int(ok)
            driver_valid = driver_valid and ok
        if not driver_valid:
            unsupported += 1

    validity = valid_count / citation_count if citation_count else (1.0 if not drivers else 0.0)
    unsupported_rate = unsupported / len(drivers) if drivers else 0.0

    return NarrativeEvaluation(
        schema_valid=schema_valid,
        driver_count=len(drivers),
        citation_count=citation_count,
        valid_citation_count=valid_count,
        citation_validity=round(validity, 4),
        unsupported_driver_count=unsupported,
        unsupported_driver_rate=round(unsupported_rate, 4),
        abstained=bool(result.get("abstained", False)),
    )
