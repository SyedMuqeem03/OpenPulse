# Changelog

All notable changes to OpenPulse will be documented in this file.

## [Unreleased]

### Added
- richer GitHub workflow status output and collector warnings
- improved run summary visibility in the Actions job log and step summary
- more explicit commit policy messaging for meaningful updates

### Changed
- workflow now emits actionable notices when collectors fail or no meaningful changes are detected
- automation keeps repository updates discreet and low-noise

## [0.1.0] - 2026-11-09

### Added
- initial OpenPulse intelligence pipeline
- CISA KEV, NVD, and OSV vulnerability collection
- GitHub release monitoring for key DevOps projects
- GitHub and Cloudflare service status monitoring
- validation, normalization, deduplication, and change detection layers
- JSON storage and historical report snapshots
- scheduled GitHub Actions collection workflow
- daily markdown and JSON report generation
- commit gating so no meaningless empty commits are created

### Fixed
- corrected OSV query payload handling for valid package-version advisory lookups
- improved validation logic to avoid treating empty or unusable data as outbreak-worthy signals
- refined release and severity classification to keep report summaries useful and consistent

### Security
- kept the project free of paid infrastructure and secret-based configuration
- made automation commit decisions based on actual data change rather than noise
