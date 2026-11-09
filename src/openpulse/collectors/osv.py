from __future__ import annotations

from datetime import UTC, datetime

from openpulse.collectors.base import CollectorHTTPError, fetch_json
from openpulse.config import Settings
from openpulse.models import CollectorResult, Record


def collect_osv_advisories(settings: Settings) -> CollectorResult:
    collected_at = datetime.now(UTC).isoformat()

    records: list[Record] = []
    errors: list[str] = []

    for ecosystem, package_name, package_version in settings.osv_packages:
        try:
            payload = fetch_json(
                settings.osv_query_url,
                settings,
                method="POST",
                json_body={
                    "package": {"ecosystem": ecosystem, "name": package_name},
                    "version": package_version,
                },
            )
            vulns = payload.get("vulns", [])
            for vuln in vulns:
                vuln_id = vuln.get("id")
                if not vuln_id:
                    continue
                affected = vuln.get("affected", [])
                fixed_versions: list[str] = []
                for item in affected:
                    for r in item.get("ranges", []):
                        for event in r.get("events", []):
                            fixed = event.get("fixed")
                            if fixed:
                                fixed_versions.append(fixed)

                records.append(
                    {
                        "id": vuln_id,
                        "source": "OSV",
                        "category": "security",
                        "vendor": ecosystem,
                        "product": package_name,
                        "severity": None,
                        "description": vuln.get("summary") or vuln.get("details"),
                        "published_at": vuln.get("published"),
                        "modified_at": vuln.get("modified"),
                        "source_url": vuln.get("database_specific", {}).get("url")
                        or f"https://osv.dev/vulnerability/{vuln_id}",
                        "fixed_versions": sorted(set(fixed_versions)),
                        "aliases": vuln.get("aliases", []),
                        "collected_at": collected_at,
                    }
                )
        except CollectorHTTPError as exc:
            errors.append(f"{ecosystem}/{package_name}@{package_version}: {exc}")

    success = len(errors) == 0
    return CollectorResult(
        source="OSV",
        records=records,
        success=success,
        error="; ".join(errors) if errors else None,
    )
