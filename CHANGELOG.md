# Changelog

All notable project changes are recorded here. Governance decisions and operational events belong in `AUDIT_LOG.md`.

## [Unreleased]

### Added

- Project-aware copy-quality pass for the starter, The Rider, and Cassia email skills.
- Audit-only mode that reports evidence without guessing AI authorship.
- Contextual vocabulary watchlist, portability test, email-specific checks, and behavioral evaluation cases.
- Third-party research notices for the public editorial resources that informed the design.
- Credential policy covering persistent GitHub SSH access, Dropbox refresh configuration, CI secrets, team handling, and rotation.
- Secure Dropbox offline-authorization helper that verifies and stores refresh tokens without printing them.
- Dependency-light `tools.asset_selection` manifest validator and deterministic asset candidate selector.
- Focused asset-selection tests for schema strictness, approval exclusion, category overlap, deterministic ordering, duplicate filenames, and missing optional metadata.
- Rider Beefree scaffold source/canonical template files, with canonical typo corrections for `REQUEST MORE INFORMAITON` and `ARTTS`.
- `tools.email_scaffold` parser utilities for row parsing, marker pairing, marker exclusion, canonical text correction, and color analysis.
- Rider agent JSON schema, six-agent active index and factual roster, and neutral future-agent template.
- Focused Rider scaffold and agent-data tests.

### Changed

- The Rider email skill and neutral project starter now describe manifest-backed asset selection, shortlist approval, and the boundary between existing assets and the separate image-generation workflow.
- The former unbranded/broker-neutral footer workflow is now the outside-broker customizable footer workflow.
- Rider brand, email design system, module, footer, Beefree structure, HTML assembly, QA, and calibration references are calibrated from the supplied scaffold.
- Agent headshots now use canonical manifest `dropbox_id` references instead of direct URLs, with explicit path, media-type, and `agent-footer` approval requirements.
- The reorganized `20. People` manifest entries distinguish in-house footer headshots from Diego Ojeda likeness references reserved for explicit image generation.

### Validated

- Refresh-token authentication completed a live Dropbox synchronization with no stored access token.
- The refresh-authenticated synchronization preserved all 195 records, including 191 records with curated `category` and `approved_for` values, with zero additions or removals.
- Asset-selection unit tests pass with Python stdlib `unittest`.
- Rider scaffold and agent-data unit tests pass with Python stdlib `unittest`.
- Live Dropbox synchronization found 205 assets: 10 added, zero removed, and 195 preserved.

## [0.1.0] - 2026-09-30

### Added

- OnBrand Design framework branding.
- Cervera Real Estate, Inc. ownership and Felix Mendoza authorship metadata.
- Apache License 2.0 for the framework and standalone project packages.
- Multi-project repository architecture and project registry.
- Collision-safe technical skill IDs for each development.
- Self-contained The Rider project package.
- Provisional Cassia project package.
- Reusable project starter and project-generation script.
- Project folder contract and isolation checklist.
- Explicit-only project email and image-generation skills.
- Directed-build and concept-development campaign modes.
- Required hero and locked-footer module definitions.
- Branded, broker-neutral, and in-house-agent output variant rules.
- Beefree-compatible provisional HTML guidance.
- Portable campaign folder, asset manifest, and ZIP requirements.
- Dropbox manifest synchronizer with array-valued `category` and `approved_for` fields.
- Stable Dropbox identity matching, rename handling, backups, and atomic writes.
- Local `.env` support with a distributable `.env.example`.
- PRD, phased specifications, roadmap, status, audit, and versioning documents.

### Validated

- Live Dropbox synchronization found 195 assets.
- All 191 previously curated records retained their manual metadata.
- Four genuinely new assets were added.
- Duplicate filenames and three renamed assets were handled safely.
- A temporary third project generated with isolated skill IDs, metadata, and registry state.
- JSON, YAML, Markdown links, placeholders, and explicit-invocation policies passed repository checks.

### Pending

- Cassia-specific brand, asset, HTML, and footer calibration.
- Runtime skill integration with the public master asset manifest.
- Canonical Beefree HTML calibration.
- Locked branded, broker-neutral, and individual agent footer files.
- End-to-end campaign generation and cross-client QA.
