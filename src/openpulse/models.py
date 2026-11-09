from __future__ import annotations

from dataclasses import dataclass
from typing import Any

Record = dict[str, Any]


@dataclass
class CollectorResult:
    source: str
    records: list[Record]
    success: bool
    error: str | None = None
