from __future__ import annotations

import json
import logging

from openpulse.automation import build_commit_message, should_commit
from openpulse.collectors import (
    collect_cisa_kev,
    collect_github_releases,
    collect_nvd_cves,
    collect_osv_advisories,
    collect_status_incidents,
)
from openpulse.config import Settings
from openpulse.processors.change_detector import detect_changes
from openpulse.processors.deduplicator import deduplicate_records
from openpulse.processors.normalizer import normalize_records
from openpulse.processors.validator import validate_records
from openpulse.reports.generator import build_json_report, build_markdown_report
from openpulse.storage.history import write_markdown_history
from openpulse.storage.json_store import read_records, write_records

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("openpulse")


def _merge_records(
    existing: list[dict],
    incoming_new: list[dict],
    incoming_updated: list[dict],
) -> list[dict]:
    merged_map = {record["id"]: record for record in existing if record.get("id")}
    for record in incoming_new:
        merged_map[record["id"]] = record
    for record in incoming_updated:
        merged_map[record["id"]] = record
    return sorted(merged_map.values(), key=lambda item: item["id"])


def _process_domain(existing: list[dict], incoming: list[dict]) -> tuple[list[dict], dict]:
    validated = validate_records(incoming)
    normalized = normalize_records(validated)
    deduped, duplicates_removed = deduplicate_records(normalized)
    new_records, updated_records = detect_changes(existing, deduped)
    merged = _merge_records(existing, new_records, updated_records)

    return merged, {
        "new": len(new_records),
        "updated": len(updated_records),
        "duplicates_removed": duplicates_removed,
    }


def _write_report_files(
    settings: Settings,
    summary: dict,
    security_records: list[dict] | None = None,
    devops_records: list[dict] | None = None,
    status_records: list[dict] | None = None,
) -> None:
    markdown_report = build_markdown_report(
        summary,
        security_records=security_records,
        devops_records=devops_records,
        status_records=status_records,
    )
    json_report = build_json_report(summary)

    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    settings.latest_report_md.write_text(markdown_report, encoding="utf-8")
    settings.latest_report_json.write_text(json_report, encoding="utf-8")
    write_markdown_history(settings.history_dir, markdown_report)


def run() -> int:
    settings = Settings()

    logger.info("Starting OpenPulse collection run")

    cisa = collect_cisa_kev(settings)
    nvd = collect_nvd_cves(settings)
    osv = collect_osv_advisories(settings)
    releases = collect_github_releases(settings)
    status = collect_status_incidents(settings)

    collector_results = [cisa, nvd, osv, releases, status]
    successful_collectors = [c.source for c in collector_results if c.success]
    failed_collectors = [c.source for c in collector_results if not c.success]

    security_existing = read_records(settings.security_file)
    devops_existing = read_records(settings.devops_file)
    status_existing = read_records(settings.status_file)

    security_incoming = cisa.records + nvd.records + osv.records
    devops_incoming = releases.records
    status_incoming = status.records

    if security_incoming:
        security_merged, security_stats = _process_domain(security_existing, security_incoming)
        write_records(settings.security_file, security_merged)
    else:
        security_stats = {"new": 0, "updated": 0, "duplicates_removed": 0}

    if devops_incoming:
        devops_merged, devops_stats = _process_domain(devops_existing, devops_incoming)
        write_records(settings.devops_file, devops_merged)
    else:
        devops_stats = {"new": 0, "updated": 0, "duplicates_removed": 0}

    if status_incoming:
        status_merged, status_stats = _process_domain(status_existing, status_incoming)
        write_records(settings.status_file, status_merged)
    else:
        status_stats = {"new": 0, "updated": 0, "duplicates_removed": 0}

    new_total = security_stats["new"] + devops_stats["new"] + status_stats["new"]
    updated_total = security_stats["updated"] + devops_stats["updated"] + status_stats["updated"]

    summary = {
        "successful_collectors": len(successful_collectors),
        "failed_collectors": len(failed_collectors),
        "new_security": security_stats["new"],
        "updated_security": security_stats["updated"],
        "new_devops": devops_stats["new"],
        "updated_devops": devops_stats["updated"],
        "new_status": status_stats["new"],
        "updated_status": status_stats["updated"],
        "duplicates_removed": (
            security_stats["duplicates_removed"]
            + devops_stats["duplicates_removed"]
            + status_stats["duplicates_removed"]
        ),
        "new_total": new_total,
        "updated_total": updated_total,
        "failed_collector_names": failed_collectors,
    }
    summary["should_commit"] = should_commit(summary)
    summary["commit_message"] = build_commit_message(summary)

    # Avoid artificial no-op commits by only updating reports for meaningful data changes.
    if new_total > 0 or updated_total > 0 or not settings.latest_report_md.exists():
        _write_report_files(
            settings,
            summary,
            security_records=security_merged if security_incoming else [],
            devops_records=devops_merged if devops_incoming else [],
            status_records=status_merged if status_incoming else [],
        )
        logger.info("Report files updated")
    else:
        logger.info("No meaningful data changes; skipping report overwrite")

    logger.info("Run summary: %s", json.dumps(summary, ensure_ascii=True))

    if failed_collectors:
        logger.warning("Some collectors failed: %s", ", ".join(failed_collectors))

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
