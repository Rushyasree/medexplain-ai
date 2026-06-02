from __future__ import annotations


EMERGENCY_KEYWORDS = {
    "chest pain": "Possible cardiac emergency",
    "breathing difficulty": "Respiratory distress",
    "shortness of breath": "Respiratory distress",
    "unconscious": "Loss of consciousness",
    "seizure": "Neurological emergency",
    "stroke": "Possible stroke warning sign",
    "severe bleeding": "Severe bleeding",
    "oxygen saturation 90": "Low oxygen saturation",
}


def emergency_findings(text: str) -> list[dict]:
    normalized = (text or "").lower()
    return [
        {"trigger": trigger, "reason": reason}
        for trigger, reason in EMERGENCY_KEYWORDS.items()
        if trigger in normalized
    ]


def check_emergency(text: str) -> bool:
    return bool(emergency_findings(text))


def risk_level(abnormalities: dict, emergency_count: int = 0) -> str:
    if emergency_count:
        return "critical"
    statuses = [value.get("status") if isinstance(value, dict) else value for value in abnormalities.values()]
    high_or_low = [status for status in statuses if status in {"HIGH", "LOW"}]
    if len(high_or_low) >= 2:
        return "moderate"
    if high_or_low:
        return "elevated"
    return "low"
