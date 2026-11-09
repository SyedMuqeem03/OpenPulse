from __future__ import annotations

from datetime import UTC, datetime

from openpulse.collectors.base import CollectorHTTPError, fetch_json
from openpulse.config import Settings
from openpulse.models import CollectorResult, Record


def collect_github_releases(settings: Settings) -> CollectorResult:
    records: list[Record] = []
    errors: list[str] = []
    collected_at = datetime.now(UTC).isoformat()

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "openpulse/0.1",
    }

    for repo in settings.github_release_watchlist:
        url = f"{settings.github_api_base}/repos/{repo}/releases"
        try:
            releases = fetch_json(url, settings, headers=headers, params={"per_page": 5, "page": 1})
            for release in releases:
                tag = release.get("tag_name")
                if not tag:
                    continue

                records.append(
                    {
                        "id": f"{repo}:{tag}",
                        "source": "GITHUB_RELEASES",
                        "category": "devops",
                        "repository": repo,
                        "version": tag,
                        "release_name": release.get("name"),
                        "published_at": release.get("published_at"),
                        "release_url": release.get("html_url"),
                        "is_prerelease": bool(release.get("prerelease")),
                        "is_draft": bool(release.get("draft")),
                        "release_notes": release.get("body"),
                        "collected_at": collected_at,
                    }
                )
        except CollectorHTTPError as exc:
            errors.append(f"{repo}: {exc}")

    success = len(errors) == 0
    return CollectorResult(
        source="GITHUB_RELEASES",
        records=records,
        success=success,
        error="; ".join(errors) if errors else None,
    )
