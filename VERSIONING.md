# Versioning Policy

This project uses Semantic Versioning while it is under active development.

## Version Meaning

- Major: incompatible changes to invocation, manifest schemas, output package contracts, or required user workflows.
- Minor: new capabilities, campaign modules, asset providers, output variants, or supported environments that preserve existing contracts.
- Patch: compatible bug fixes, documentation improvements, validation refinements, and narrow rule corrections.

Versions below `1.0.0` are pre-release. Minor releases may still refine provisional interfaces, but every breaking change must be called out in `CHANGELOG.md` and `AUDIT_LOG.md`.

The root `VERSION` tracks the OnBrand Design framework. Each `project.json` tracks project lifecycle and calibration state. Add independent project versions later only when projects need release cycles separate from the framework.

## Release Requirements

A release must include:

1. Updated `VERSION`.
2. A dated `CHANGELOG.md` entry.
3. Updated phase and project status.
4. Validation of both skill manifests and explicit-only invocation policies.
5. Tests or documented verification proportional to the change.
6. Confirmation that no credentials or private `.env` files are tracked.
7. Validation that project skill IDs remain unique across `projects/registry.json`.

## Planned Milestones

- `0.1.x`: architecture, planning, and Dropbox manifest foundation.
- `0.2.0`: runtime asset-catalog integration.
- `0.3.0`: calibrated Rider brand and Beefree template system.
- `0.4.0`: campaign strategy and copy workflow.
- `0.5.0`: image-generation handoff and approval workflow.
- `0.6.0`: HTML variant assembly and locked footers.
- `0.7.0`: complete campaign packaging and QA automation.
- `0.9.0`: Codex and Claude Code release candidate.
- `1.0.0`: validated team-ready release.
