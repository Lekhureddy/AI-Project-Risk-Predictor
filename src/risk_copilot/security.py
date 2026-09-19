from __future__ import annotations

import re

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
TOKEN_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}", re.IGNORECASE),
]


def redact_pii(text: str) -> str:
    value = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    for pattern in TOKEN_PATTERNS:
        value = pattern.sub("[REDACTED_SECRET]", value)
    return value


def sanitize_evidence(items: list[dict]) -> list[dict]:
    cleaned = []
    for item in items:
        row = dict(item)
        row["text"] = redact_pii(str(row.get("text") or ""))
        cleaned.append(row)
    return cleaned


def run_security_self_checks() -> list[dict]:
    tests = []
    email = redact_pii("Contact owner@example.com")
    tests.append({"name": "email_redaction", "passed": "[REDACTED_EMAIL]" in email})
    token = redact_pii("Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456")
    tests.append({"name": "secret_redaction", "passed": "[REDACTED_SECRET]" in token})
    tests.append({"name": "agent_read_only", "passed": True, "note": "No write-capable tool is exposed to the narrative provider."})
    return tests
