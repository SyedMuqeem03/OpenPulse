from __future__ import annotations

import re
from typing import Any


def normalize_version(value: Any) -> tuple[int | str, ...]:
    if value is None:
        return ()

    text = str(value).strip()
    if not text:
        return ()

    cleaned = text[1:] if text.startswith("v") or text.startswith("V") else text
    cleaned = cleaned.replace("_", ".")

    match = re.match(
        r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:[.-]?(alpha|beta|rc|preview|dev))?(?:[.-]?(\d+))?$",
        cleaned.lower(),
    )

    if not match:
        tokens = re.findall(r"\d+|[a-z]+", cleaned.lower())
        normalized: list[int | str] = []
        for token in tokens:
            if token.isdigit():
                normalized.append(int(token))
            else:
                normalized.append(token)
        return tuple(normalized)

    major, minor, patch, suffix, suffix_num = match.groups()
    parts: list[int | str] = []
    for item in (major, minor, patch):
        if item is not None:
            parts.append(int(item))

    if suffix:
        parts.append(suffix)
        if suffix_num is not None:
            parts.append(int(suffix_num))

    return tuple(parts)


def _split_normalized_version(version: tuple[int | str, ...]) -> tuple[tuple[int, ...], str | None, int]:
    core: list[int] = []
    suffix: str | None = None
    suffix_number = 0

    for index, part in enumerate(version):
        if isinstance(part, int):
            core.append(part)
            continue

        suffix = str(part).lower()
        if index + 1 < len(version) and isinstance(version[index + 1], int):
            suffix_number = int(version[index + 1])
        break

    return tuple(core), suffix, suffix_number


def version_compare(current: Any, previous: Any) -> int:
    left = normalize_version(current)
    right = normalize_version(previous)

    if left == right:
        return 0

    return 1


def classify_release_significance(release: dict[str, Any]) -> str:
    if not isinstance(release, dict):
        return "UNKNOWN"

    if release.get("is_prerelease"):
        return "PRE_RELEASE"

    version = normalize_version(release.get("version"))
    if not version:
        return "UNKNOWN"

    core, _, _ = _split_normalized_version(version)
    if not core:
        return "UNKNOWN"
    if core[0] >= 1:
        return "MAJOR"
    return "PATCH"
