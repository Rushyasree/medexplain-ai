from __future__ import annotations

import re


PATTERNS = [
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[EMAIL]"),
    (re.compile(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b"), "[PHONE]"),
    (re.compile(r"\b\d{12}\b"), "[ID_NUMBER]"),
]


def redact_sensitive_text(text: str) -> str:
    redacted = text or ""
    for pattern, replacement in PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def summarize_privacy_actions(original: str, redacted: str) -> dict:
    return {
        "redacted": original != redacted,
        "characters_removed": max(0, len(original or "") - len(redacted or "")),
    }
