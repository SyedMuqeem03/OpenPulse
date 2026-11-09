from __future__ import annotations


def should_commit(summary: dict) -> bool:
    if not isinstance(summary, dict):
        return False

    new_total = int(summary.get("new_total", 0) or 0)
    updated_total = int(summary.get("updated_total", 0) or 0)
    failed_collectors = int(summary.get("failed_collectors", 0) or 0)

    if failed_collectors > 0:
        return new_total > 0 or updated_total > 0

    return new_total > 0 or updated_total > 0


def build_commit_message(summary: dict) -> str:
    new_security = int(summary.get("new_security", 0) or 0)
    new_devops = int(summary.get("new_devops", 0) or 0)
    updated_total = int(summary.get("updated_total", 0) or 0)

    if new_security > 0 or new_devops > 0:
        parts = []
        if new_security > 0:
            parts.append(f"{new_security} vulnerabilities")
        if new_devops > 0:
            parts.append(f"{new_devops} release updates")
        if updated_total > 0:
            parts.append(f"{updated_total} updated records")

        if not parts:
            return "feat: refresh daily intelligence"
        return f"feat: add {', '.join(parts)} to daily intelligence"

    if updated_total > 0:
        return "chore: refresh daily intelligence"

    return "chore: no meaningful changes"
