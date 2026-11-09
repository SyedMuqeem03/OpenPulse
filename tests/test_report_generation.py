from openpulse.reports.generator import build_markdown_report, summarize_findings


def test_summarize_findings_prioritizes_critical_security_records() -> None:
    findings = summarize_findings(
        [
            {
                "id": "CVE-2026-1234",
                "source": "CISA_KEV",
                "severity": "CRITICAL",
                "description": "Remote code execution",
                "source_url": "https://example.com/cve",
            }
        ],
        [
            {
                "repository": "kubernetes/kubernetes",
                "version": "v1.32.0",
                "release_name": "Kubernetes v1.32.0",
                "is_prerelease": False,
            }
        ],
        [
            {"provider": "github", "status": "operational", "name": "GitHub status"}
        ],
    )

    assert findings["critical_security"][0]["id"] == "CVE-2026-1234"
    assert findings["release_highlights"][0]["repository"] == "kubernetes/kubernetes"
    assert findings["status_incidents"][0]["provider"] == "github"


def test_build_markdown_report_includes_top_findings() -> None:
    report = build_markdown_report(
        {
            "new_security": 2,
            "updated_security": 0,
            "new_devops": 1,
            "updated_devops": 0,
            "new_status": 0,
            "updated_status": 1,
            "successful_collectors": 5,
            "failed_collectors": 0,
            "duplicates_removed": 1,
            "new_total": 3,
            "updated_total": 1,
        },
        security_records=[
            {
                "id": "CVE-2026-1234",
                "source": "CISA_KEV",
                "severity": "CRITICAL",
                "description": "Remote code execution",
                "source_url": "https://example.com/cve",
            }
        ],
        devops_records=[
            {
                "repository": "kubernetes/kubernetes",
                "version": "v1.32.0",
                "release_name": "Kubernetes v1.32.0",
                "is_prerelease": False,
            }
        ],
        status_records=[
            {"provider": "github", "status": "operational", "name": "GitHub status"}
        ],
    )

    assert "OpenPulse Daily Intelligence Report" in report
    assert "Critical Security Findings" in report
    assert "CVE-2026-1234" in report
    assert "Kubernetes v1.32.0" in report
