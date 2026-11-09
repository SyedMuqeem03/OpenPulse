from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def write_markdown_history(history_dir: Path, markdown_report: str) -> Path:
    history_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    file_path = history_dir / f"report_{stamp}.md"
    file_path.write_text(markdown_report, encoding="utf-8")
    return file_path
