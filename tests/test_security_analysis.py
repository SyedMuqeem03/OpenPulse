from openpulse.analyzer.security import (
    classify_priority,
    normalize_severity,
    score_vulnerability_risk,
)


def test_normalize_severity_handles_aliases() -> None:
    assert normalize_severity("critical") == "CRITICAL"
    assert normalize_severity("High") == "HIGH"
    assert normalize_severity("none") == "NONE"


def test_score_vulnerability_risk_uses_cvss_and_exploitation() -> None:
    record = {
        "id": "CVE-2026-1234",
        "source": "CISA_KEV",
        "severity": "CRITICAL",
        "cvss_score": 9.8,
        "known_ransomware_campaign_use": True,
    }

    score = score_vulnerability_risk(record)
    assert score >= 90
    assert classify_priority(record) == "CRITICAL"


def test_score_vulnerability_risk_handles_missing_values() -> None:
    assert score_vulnerability_risk({"source": "NVD"}) == 0
    assert classify_priority({"source": "NVD"}) == "LOW"
