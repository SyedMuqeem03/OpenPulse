from __future__ import annotations

from openpulse.models import Record


def validate_records(records: list[Record]) -> list[Record]:
    valid: list[Record] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        if not record.get("id"):
            continue
        if not record.get("source"):
            continue
        if not record.get("category"):
            continue
        valid.append(record)
    return valid
