from __future__ import annotations

from typing import Any

SEVERITY_SCORES = {
    "CRITICAL": 10.0,
    "HIGH": 8.0,
    "MEDIUM": 5.0,
    "LOW": 2.5,
    "NONE": 0.0,
    "UNKNOWN": 0.0,
}


def normalize_severity(value: Any) -> str:
    if value is None:
        return "UNKNOWN"

    normalized = str(value).strip().upper()
    aliases = {
        "CRIT": "CRITICAL",
        "SEV0": "NONE",
        "SEV1": "LOW",
        "SEV2": "MEDIUM",
        "SEV3": "MEDIUM",
        "SEV4": "HIGH",
        "SEV5": "CRITICAL",
        "IMPORTANT": "HIGH",
        "MODERATE": "MEDIUM",
        "MED": "MEDIUM",
    }

    return aliases.get(normalized, normalized if normalized in SEVERITY_SCORES else "UNKNOWN")


def score_vulnerability_risk(record: dict[str, Any]) -> int:
    if not isinstance(record, dict):
        return 0

    severity_value = record.get("severity")
    severity = normalize_severity(severity_value)
    score = SEVERITY_SCORES.get(severity, 0.0)

    cvss_value = record.get("cvss_score")
    if isinstance(cvss_value, int | float):
        score = max(score, float(cvss_value))

    source = str(record.get("source", "")).upper()
    if "CISA" in source or "KEV" in source:
        score += 10
    if record.get("known_ransomware_campaign_use"):
        score += 10

    if source.startswith("NVD") and severity_value is None and cvss_value is None:
        return 0

    return int(min(max(score * 10, 0), 100))


def classify_priority(record: dict[str, Any]) -> str:
    score = score_vulnerability_risk(record)
    if score >= 85:
        return "CRITICAL"
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    if score > 0:
        return "LOW"
    return "LOW"
