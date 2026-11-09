from __future__ import annotations

import json
from datetime import UTC, datetime

from openpulse.analyzer.releases import classify_release_significance
from openpulse.analyzer.security import classify_priority, normalize_severity


def _published_year(record: dict) -> int | None:
    published_at = record.get("published_at")
    if not published_at:
        return None

    text = str(published_at).strip()
    if not text:
        return None

    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text).year
    except ValueError:
        return None


def _is_actionable_security_record(record: dict) -> bool:
    if not isinstance(record, dict):
        return False

    identifier = str(record.get("id") or "").strip()
    if not identifier:
        return False

    source = str(record.get("source") or "").upper()
    product = str(record.get("product") or record.get("vendor") or "").strip()

    published_year = _published_year(record)
    if published_year is not None and published_year < 2019 and source != "CISA_KEV":
        return False

    if not product and source != "CISA_KEV":
        return False

    return True


def summarize_findings(
    security_records: list[dict] | None = None,
    devops_records: list[dict] | None = None,
    status_records: list[dict] | None = None,
) -> dict[str, list[dict]]:
    security_records = security_records or []
    devops_records = devops_records or []
    status_records = status_records or []

    critical_security: list[dict] = []
    for record in security_records:
        if not _is_actionable_security_record(record):
            continue

        priority = classify_priority(record)
        if priority in {"CRITICAL", "HIGH"}:
            critical_security.append(
                {
                    "id": record.get("id"),
                    "severity": normalize_severity(record.get("severity")),
                    "source": record.get("source"),
                    "product": record.get("product") or record.get("vendor"),
                    "description": record.get("description"),
                    "source_url": record.get("source_url"),
                }
            )

    release_highlights: list[dict] = []
    for release in devops_records:
        significance = classify_release_significance(release)
        if significance in {"MAJOR", "PRE_RELEASE"}:
            release_highlights.append(
                {
                    "repository": release.get("repository"),
                    "version": release.get("version"),
                    "release_name": release.get("release_name") or release.get("version"),
                    "significance": significance,
                    "release_url": release.get("release_url"),
                }
            )

    status_incidents: list[dict] = []
    for event in status_records:
        if event.get("provider") or event.get("name"):
            status_incidents.append(
                {
                    "provider": event.get("provider"),
                    "name": event.get("name"),
                    "status": event.get("status"),
                    "source_url": event.get("source_url"),
                }
            )

    return {
        "critical_security": critical_security[:5],
        "release_highlights": release_highlights[:5],
        "status_incidents": status_incidents[:5],
    }


def build_markdown_report(
    summary: dict,
    security_records: list[dict] | None = None,
    devops_records: list[dict] | None = None,
    status_records: list[dict] | None = None,
) -> str:
    run_date = datetime.now(UTC).strftime("%Y-%m-%d")
    findings = summarize_findings(security_records, devops_records, status_records)

    lines = [
        "# OpenPulse Daily Intelligence Report",
        "",
        f"Date: {run_date}",
        "",
        "## Summary",
        "",
        f"- New security records: {summary['new_security']}",
        f"- Updated security records: {summary['updated_security']}",
        f"- New DevOps records: {summary['new_devops']}",
        f"- Updated DevOps records: {summary['updated_devops']}",
        f"- New status records: {summary['new_status']}",
        f"- Updated status records: {summary['updated_status']}",
        "",
        "## Critical Security Findings",
        "",
    ]

    if findings["critical_security"]:
        for record in findings["critical_security"]:
            lines.append(f"### {record['id']}")
            lines.append(f"- Severity: {record['severity']}")
            lines.append(f"- Source: {record['source']}")
            lines.append(f"- Product: {record['product']}")
            lines.append(f"- Reference: {record['source_url']}")
            lines.append("")
    else:
        lines.append("No critical or high-priority security findings identified in this run.")
        lines.append("")

    lines.extend(["## DevOps Release Highlights", ""])
    if findings["release_highlights"]:
        for release in findings["release_highlights"]:
            lines.append(f"### {release['repository']}")
            lines.append(f"- Version: {release['version']}")
            lines.append(f"- Significance: {release['significance']}")
            lines.append(f"- Release: {release['release_name']}")
            lines.append(f"- URL: {release['release_url']}")
            lines.append("")
    else:
        lines.append("No notable DevOps release highlights identified.")
        lines.append("")

    lines.extend(["## Status Incidents", ""])
    if findings["status_incidents"]:
        for incident in findings["status_incidents"]:
            lines.append(f"- Provider: {incident['provider']}")
            lines.append(f"  Status: {incident['status']}")
            lines.append(f"  Name: {incident['name']}")
            lines.append(f"  Source: {incident['source_url']}")
            lines.append("")
    else:
        lines.append("No notable status incidents detected.")
        lines.append("")

    lines.extend(
        [
            "## Collection Summary",
            "",
            f"- Successful collectors: {summary['successful_collectors']}",
            f"- Failed collectors: {summary['failed_collectors']}",
            f"- Duplicates removed: {summary['duplicates_removed']}",
            f"- New records stored: {summary['new_total']}",
            f"- Updated records stored: {summary['updated_total']}",
        ]
    )
    return "\n".join(lines) + "\n"


def build_json_report(summary: dict) -> str:
    return json.dumps(summary, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
