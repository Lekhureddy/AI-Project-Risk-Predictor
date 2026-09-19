from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    source_type: str
    title: str
    url: str
    text: str


def build_evidence_index(items: Iterable[dict]) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for item in items:
        evidence_id = str(item.get("evidence_id") or "").strip()
        if not evidence_id:
            raise ValueError("evidence item requires evidence_id")
        if evidence_id in index:
            raise ValueError(f"duplicate evidence_id: {evidence_id}")
        record = EvidenceRecord(
            evidence_id=evidence_id,
            source_type=str(item.get("source_type") or "unknown"),
            title=str(item.get("title") or ""),
            url=str(item.get("url") or ""),
            text=str(item.get("text") or ""),
        )
        index[evidence_id] = asdict(record)
    return index


def verify_citation(citation: dict, evidence_index: dict[str, dict]) -> tuple[bool, str]:
    evidence_id = str(citation.get("evidence_id") or "")
    quote = str(citation.get("quote") or "").strip()

    if evidence_id not in evidence_index:
        return False, "unknown_evidence_id"
    if not quote:
        return False, "missing_quote"

    source_text = evidence_index[evidence_id]["text"]
    if quote not in source_text:
        return False, "quote_not_found_verbatim"

    return True, "verified"


def filter_verified_drivers(drivers: list[dict], evidence_index: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    verified = []
    dropped = []

    for driver in drivers:
        citations = driver.get("citations") or []
        if not citations:
            dropped.append({"driver": driver, "reason": "no_citations"})
            continue

        checks = [verify_citation(citation, evidence_index) for citation in citations]
        if all(ok for ok, _ in checks):
            verified.append(driver)
        else:
            dropped.append({
                "driver": driver,
                "reason": ",".join(reason for ok, reason in checks if not ok),
            })

    return verified, dropped
