from __future__ import annotations

import time
from typing import Any

import httpx

from openpulse.config import Settings


class CollectorHTTPError(RuntimeError):
    pass


def fetch_json(
    url: str,
    settings: Settings,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> Any:
    timeout = httpx.Timeout(settings.request_timeout_seconds)
    attempt = 0
    last_error: Exception | None = None

    while attempt < settings.max_retries:
        attempt += 1
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                response = client.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=json_body,
                )

            if response.status_code == 429:
                wait_seconds = settings.backoff_seconds * attempt
                time.sleep(wait_seconds)
                continue

            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            last_error = exc
            if attempt >= settings.max_retries:
                break
            wait_seconds = settings.backoff_seconds * attempt
            time.sleep(wait_seconds)

    raise CollectorHTTPError(f"Failed to fetch {url}: {last_error}")
