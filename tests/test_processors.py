from openpulse.processors.change_detector import detect_changes
from openpulse.processors.deduplicator import deduplicate_records
from openpulse.processors.validator import validate_records


def test_validate_records_filters_invalid() -> None:
    records = [
        {"id": "A", "source": "X", "category": "security"},
        {"id": "", "source": "X", "category": "security"},
        {"source": "X", "category": "security"},
    ]
    valid = validate_records(records)
    assert len(valid) == 1


def test_deduplicate_records_keeps_last() -> None:
    records = [
        {"id": "A", "source": "X", "category": "security", "value": 1},
        {"id": "A", "source": "X", "category": "security", "value": 2},
    ]
    deduped, removed = deduplicate_records(records)
    assert len(deduped) == 1
    assert removed == 1
    assert deduped[0]["value"] == 2


def test_detect_changes_new_and_updated() -> None:
    existing = [{"id": "A", "source": "X", "category": "security", "value": 1}]
    incoming = [
        {"id": "A", "source": "X", "category": "security", "value": 2},
        {"id": "B", "source": "X", "category": "security", "value": 3},
    ]
    new_records, updated_records = detect_changes(existing, incoming)
    assert len(new_records) == 1
    assert len(updated_records) == 1
