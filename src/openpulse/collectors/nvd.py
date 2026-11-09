from __future__ import annotations

from datetime import UTC, datetime

from openpulse.collectors.base import CollectorHTTPError, fetch_json
from openpulse.config import Settings
from openpulse.models import CollectorResult, Record


def _extract_cvss(metrics: dict) -> tuple[str | None, float | None]:
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        entries = metrics.get(key) or []
        if not entries:
            continue
        data = entries[0].get("cvssData", {})
        return data.get("baseSeverity"), data.get("baseScore")
    return None, None


def collect_nvd_cves(settings: Settings, max_results: int = 200) -> CollectorResult:
    try:
        payload = fetch_json(
            settings.nvd_cve_url,
            settings,
            params={"startIndex": 0, "resultsPerPage": max_results},
        )
        items = payload.get("vulnerabilities", [])
        collected_at = datetime.now(UTC).isoformat()

        records: list[Record] = []
        for wrapper in items:
            cve = wrapper.get("cve", {})
            cve_id = cve.get("id")
            if not cve_id:
                continue

            descriptions = cve.get("descriptions", [])
            description = next(
                (d.get("value") for d in descriptions if d.get("lang") == "en"),
                descriptions[0].get("value") if descriptions else None,
            )

            severity, score = _extract_cvss(cve.get("metrics", {}))

            records.append(
                {
                    "id": cve_id,
                    "source": "NVD",
                    "category": "security",
                    "vendor": None,
                    "product": None,
                    "severity": severity,
                    "cvss_score": score,
                    "description": description,
                    "published_at": cve.get("published"),
                    "last_modified": cve.get("lastModified"),
                    "source_url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                    "collected_at": collected_at,
                }
            )

        return CollectorResult(source="NVD", records=records, success=True)
    except CollectorHTTPError as exc:
        return CollectorResult(source="NVD", records=[], success=False, error=str(exc))
