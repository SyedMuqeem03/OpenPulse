# OpenPulse

OpenPulse is a zero-cost, daily automation project that collects and processes public security and DevOps intelligence.

## Scope (Phase 1-4 Baseline)

- Security sources: CISA KEV, NVD, OSV
- DevOps sources: GitHub releases (Docker, Kubernetes, Terraform, Jenkins, Prometheus, Grafana)
- Status sources: GitHub Status, Cloudflare Status
- Data pipeline: validation, normalization, deduplication, change detection, JSON persistence
- Automation: daily GitHub Actions run with commit-only-on-change

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:
   - `python -m pip install --upgrade pip`
   - `pip install -r requirements.txt`
   - `pip install -e .`
3. Run collection:
   - `python -m openpulse.main`

## Output

- Collected data is written under `data/`.
- Daily reports are written to `reports/`.
- Historical snapshots are written to `reports/history/`.

## Safety Guarantees

- No paid cloud infrastructure required.
- No secrets committed to source control.
- No commit is created when no meaningful change exists.
