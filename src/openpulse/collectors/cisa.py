from __future__ import annotations

from datetime import UTC, datetime

from openpulse.collectors.base import CollectorHTTPError, fetch_json
from openpulse.config import Settings
from openpulse.models import CollectorResult, Record


def collect_cisa_kev(settings: Settings) -> CollectorResult:
    try:
        payload = fetch_json(settings.cisa_kev_url, settings)
        vulnerabilities = payload.get("vulnerabilities", [])
        collected_at = datetime.now(UTC).isoformat()

        records: list[Record] = []
        for item in vulnerabilities:
            cve_id = item.get("cveID")
            if not cve_id:
                continue

            records.append(
                {
                    "id": cve_id,
                    "source": "CISA_KEV",
                    "category": "security",
                    "vendor": item.get("vendorProject"),
                    "product": item.get("product"),
                    "severity": None,
                    "description": item.get("shortDescription"),
                    "published_at": item.get("dateAdded"),
                    "source_url": settings.cisa_kev_url,
                    "due_date": item.get("dueDate"),
                    "known_ransomware_campaign_use": item.get("knownRansomwareCampaignUse"),
                    "notes": item.get("notes"),
                    "collected_at": collected_at,
                }
            )

        return CollectorResult(source="CISA_KEV", records=records, success=True)
    except CollectorHTTPError as exc:
        return CollectorResult(source="CISA_KEV", records=[], success=False, error=str(exc))
