from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    request_timeout_seconds: float = 20.0
    max_retries: int = 3
    backoff_seconds: float = 1.5

    cisa_kev_url: str = (
        "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    )
    nvd_cve_url: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    osv_query_url: str = "https://api.osv.dev/v1/query"

    github_api_base: str = "https://api.github.com"
    github_release_watchlist: tuple[str, ...] = (
        "moby/moby",
        "kubernetes/kubernetes",
        "hashicorp/terraform",
        "jenkinsci/jenkins",
        "prometheus/prometheus",
        "grafana/grafana",
    )

    osv_packages: tuple[tuple[str, str, str], ...] = (
        ("PyPI", "requests", "2.31.0"),
        ("PyPI", "django", "4.2.0"),
        ("PyPI", "urllib3", "2.0.0"),
        ("PyPI", "pyyaml", "6.0"),
    )

    github_status_url: str = "https://www.githubstatus.com/api/v2/summary.json"
    cloudflare_status_url: str = "https://www.cloudflarestatus.com/api/v2/summary.json"

    data_dir: Path = Path("data")
    reports_dir: Path = Path("reports")

    security_file: Path = Path("data/security/security_records.json")
    devops_file: Path = Path("data/devops/devops_records.json")
    status_file: Path = Path("data/devops/status_records.json")
    latest_report_md: Path = Path("reports/latest.md")
    latest_report_json: Path = Path("reports/latest.json")
    history_dir: Path = Path("reports/history")


@dataclass
class RunMetadata:
    run_started_at: str
    successful_collectors: list[str] = field(default_factory=list)
    failed_collectors: list[str] = field(default_factory=list)
