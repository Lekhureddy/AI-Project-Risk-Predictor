from __future__ import annotations

from .security import sanitize_evidence


def evidence_from_milestone_items(repo: str, items: list[dict]) -> list[dict]:
    evidence = []
    for item in items:
        number = int(item["number"])
        is_pr = "pull_request" in item
        source_type = "pull_request" if is_pr else "issue"
        prefix = "PR" if is_pr else "ISSUE"
        body = str(item.get("body") or "")
        title = str(item.get("title") or f"{prefix} #{number}")
        text = f"{title}\n\n{body}".strip()
        evidence.append(
            {
                "evidence_id": f"{repo}:{prefix}-{number}",
                "source_type": source_type,
                "title": title,
                "url": str(item.get("html_url") or ""),
                "text": text,
            }
        )
    return sanitize_evidence(evidence)
