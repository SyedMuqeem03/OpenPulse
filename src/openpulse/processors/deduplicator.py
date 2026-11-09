from __future__ import annotations

from openpulse.models import Record


def deduplicate_records(records: list[Record]) -> tuple[list[Record], int]:
    deduped_map: dict[str, Record] = {}

    for record in records:
        deduped_map[record["id"]] = record

    deduped = list(deduped_map.values())
    duplicates_removed = len(records) - len(deduped)
    return deduped, duplicates_removed
