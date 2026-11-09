from __future__ import annotations

from datetime import UTC, datetime

from openpulse.collectors.base import CollectorHTTPError, fetch_json
from openpulse.config import Settings
from openpulse.models import CollectorResult, Record


def _collect_provider_status(url: str, provider: str, settings: Settings) -> list[Record]:
    payload = fetch_json(url, settings)
    collected_at = datetime.now(UTC).isoformat()

    records: list[Record] = []
    incidents = payload.get("incidents", [])
    for incident in incidents:
        incident_id = incident.get("id")
        if not incident_id:
            continue
        records.append(
            {
                "id": f"{provider}:{incident_id}",
                "source": "STATUS_API",
                "category": "devops",
                "provider": provider,
                "status": incident.get("status"),
                "name": incident.get("name"),
                "impact": incident.get("impact"),
                "created_at": incident.get("created_at"),
                "updated_at": incident.get("updated_at"),
                "resolved_at": incident.get("resolved_at"),
                "source_url": incident.get("shortlink") or url,
                "collected_at": collected_at,
            }
        )
    return records


def collect_status_incidents(settings: Settings) -> CollectorResult:
    records: list[Record] = []
    errors: list[str] = []

    providers = (
        ("github", settings.github_status_url),
        ("cloudflare", settings.cloudflare_status_url),
    )

    for provider, url in providers:
        try:
            records.extend(_collect_provider_status(url, provider, settings))
        except CollectorHTTPError as exc:
            errors.append(f"{provider}: {exc}")

    success = len(errors) == 0
    return CollectorResult(
        source="STATUS_API",
        records=records,
        success=success,
        error="; ".join(errors) if errors else None,
    )
