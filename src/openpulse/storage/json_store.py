from __future__ import annotations

import json
from pathlib import Path

from openpulse.models import Record


def read_records(path: Path) -> list[Record]:
    if not path.exists():
        return []

    try:
        content = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(content, list):
            return [item for item in content if isinstance(item, dict)]
        return []
    except json.JSONDecodeError:
        return []


def write_records(path: Path, records: list[Record]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(records, ensure_ascii=True, indent=2, sort_keys=True)
    path.write_text(data + "\n", encoding="utf-8")
