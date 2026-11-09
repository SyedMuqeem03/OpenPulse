from __future__ import annotations

from datetime import UTC, datetime

from openpulse.models import Record


def normalize_records(records: list[Record]) -> list[Record]:
    normalized: list[Record] = []
    now_iso = datetime.now(UTC).isoformat()

    for record in records:
        item = dict(record)
        item["id"] = str(item["id"]).strip()
        item["source"] = str(item["source"]).strip().upper()
        item["category"] = str(item["category"]).strip().lower()

        if "first_seen_at" not in item:
            item["first_seen_at"] = now_iso
        item["last_updated_at"] = now_iso

        normalized.append(item)

    return normalized
