from __future__ import annotations

from openpulse.models import Record


def detect_changes(
    existing: list[Record],
    incoming: list[Record],
) -> tuple[list[Record], list[Record]]:
    existing_map = {record["id"]: record for record in existing if record.get("id")}

    new_records: list[Record] = []
    updated_records: list[Record] = []

    for record in incoming:
        record_id = record["id"]
        previous = existing_map.get(record_id)
        if previous is None:
            new_records.append(record)
            continue

        prev_copy = dict(previous)
        new_copy = dict(record)

        prev_copy.pop("last_updated_at", None)
        new_copy.pop("last_updated_at", None)

        if prev_copy != new_copy:
            record["first_seen_at"] = previous.get("first_seen_at", record.get("first_seen_at"))
            updated_records.append(record)

    return new_records, updated_records
