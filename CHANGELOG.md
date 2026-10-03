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
- Strict Rider campaign JSON schema and deterministic scaffold slot map.
- Rider module composer, typed slot renderer, branded/outside-broker/agent footer renderer, used-asset downloader, checksum manifest, blocking QA report, and ZIP generator.
- Non-production Rider runtime smoke fixture and focused runtime regression tests.
- Revised Rider scaffold source, legacy provenance fixture, module metadata catalog, and four nested static-block definitions.
- Diana Kosov verified agent record and seven-agent Rider output order.
- Separate Rider wellness smoke campaign fixture with generated 16:9 hero asset and approved recovery/arrival body imagery.

### Changed

- The Rider email skill and neutral project starter now describe manifest-backed asset selection, shortlist approval, and the boundary between existing assets and the separate image-generation workflow.
- The former unbranded/broker-neutral footer workflow is now the outside-broker customizable footer workflow.
- Rider brand, email design system, module, footer, Beefree structure, HTML assembly, QA, and calibration references are calibrated from the supplied scaffold.
- Agent headshots now use canonical manifest `dropbox_id` references instead of direct URLs, with explicit path, media-type, and `agent-footer` approval requirements.
- The reorganized `20. People` manifest entries distinguish in-house footer headshots from Diego Ojeda likeness references reserved for explicit image generation.
- The Rider email skill now requires the validated runtime path for HTML variants and distribution packages.
- Rider campaign JSON now requires an explicit decision for every static block.
- Header and hero modules are classified separately; incompatible standalone-header/header-bearing-hero combinations are rejected.
- Runtime output is built in a protected staging directory so failed asset downloads cannot replace the last valid package.
- Rider runtime image slots accept safe local generated assets for reproducible fixtures, then package them as relative review assets.

### Validated

- Refresh-token authentication completed a live Dropbox synchronization with no stored access token.
- The refresh-authenticated synchronization preserved all 195 records, including 191 records with curated `category` and `approved_for` values, with zero additions or removals.
- Asset-selection unit tests pass with Python stdlib `unittest`.
- Rider scaffold and agent-data unit tests pass with Python stdlib `unittest`.
- Live Dropbox synchronization found 205 assets: 10 added, zero removed, and 195 preserved.
- Rider runtime unit suite passes 29 tests.
- End-to-end smoke generation passes 221 QA checks and produces eight HTML variants, 17 packaged images, one selected PDF, campaign metadata, an asset manifest, a QA report, and a ZIP.
- Revised-scaffold unit suite passes 35 tests, including preservation of the last passing package after a failed asset download.
- Paulie Hankin replaces Jake Lecce in the active roster; the revised smoke package passes 200 QA checks across eight variants with 15 images, one PDF, and a valid ZIP.
- Dropbox synchronization found 206 assets, added Paulie Hankin's headshot, and preserved the curated arrays of all 205 existing records.
- After Dropbox write authorization was renewed, Jake Lecce's retired headshot was deleted; synchronization removed only his asset and preserved all curated fields across the 205 surviving records.
- Dropbox synchronization found Diana Kosov as the sole addition at `id:31E0v0XEN2IAAAAAAAABlg`; only her new record was curated for `agent-footer`, and all 205 surviving manual `category` and `approved_for` arrays were preserved.
- Full unittest discovery passes 37 tests.
- Existing Rider runtime smoke passes 9 variants after Diana's activation.
- Rider wellness smoke passes 230 QA checks, produces 9 HTML variants, 17 packaged images, no external image references in relative-review mode, and a valid ZIP.

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
