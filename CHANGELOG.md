# Changelog

All notable project changes are recorded here. Governance decisions and operational events belong in `AUDIT_LOG.md`.

## [Unreleased]

### Fixed

- Phase 11 completion-audit defects where Python equality treated JSON booleans as numbers in parity and approval matching. Shared recursive JSON-semantic comparison/hashing now preserves type distinctions, declares finite numeric equivalence, and rejects non-finite values; selection and asset-size boundaries use the same check.
- Added 15 regressions and rebuilt realistic three-adapter parity evidence without changing campaign business logic, approvals, or accepted live invocation limitations.

### Added

- Approved Phase 13 Jev semantic decision pilot specification and LIM-018. The provider remains optional, disabled, and unimplemented pending a labeled Rider evaluation, privacy approval, deterministic fallback tests, and a keep/remove decision.
- Phase 13 evaluation foundation with 26 provisional de-identified cases, a Draft 2020-12 schema, strict standard-library validator, blind review worksheet, baseline evaluator, and machine-readable diagnostic report. No provider integration was added.
- Phase 13 blinded review workflow with dataset-bound response templates, completion validation, independent-reviewer enforcement, and deterministic disagreement reporting.
- Two completed blinded Phase 13 reviews and comparison evidence: 21/26 full agreement, 25/26 semantic-label agreement, and five cases reserved for explicit adjudication.
- Hash-bound adjudication evidence and a separate frozen Phase 13 dataset; all five disputes are resolved without changing holdout text or adding provider behavior.
- Calibration-locked Jev question set version 1, pinned model configuration, privacy field policy, and a label-free 17-case request batch with holdout generation guarded explicitly.

- Phase 11 versioned project/request contracts, manual-only Codex/Claude workspace wrappers, shared dispatch, installer/generator integration, and 13-component blocking parity.
- Realistic three-adapter Rider preview evidence at 100%, checksum-verified real asset transport, and separate live CLI limitations without changing credentials or Phase 7-10 rules.
- Portable canonical frontmatter and accurate shared-core installation boundaries; Phase 12 restricted distribution remains deferred.

- Explicit dependency conditions for all 16 limitation entries and the entry template, plus a dedicated responsive desktop/mobile copy fixture that passes allocation and package QA under one logical owner.

- Phase 10 required approved copy allocation contract, stable content-unit/channel ownership, restricted phrase counts, exact/normalized and near-duplicate checks, declared baked-image text, scoped reuse exemptions, claim-reference gates, and metadata/QA evidence.
- Dedicated allocation reference, 17 positive/negative allocation tests, and committed Composition Preview package-audit evidence.

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
- Approved planning specs for Phase 7 build modes, Phase 8 Composition Preview, Phase 9 grounded image generation, Phase 10 copy allocation QA, Phase 11 cross-platform compatibility, and deferred Phase 12 distribution profiles.
- Compatibility and distribution-security plans documenting canonical-core adapter expectations, planned Claude Code support, and deferred broker/private package separation.
- Rider build-mode contract for Composition Preview, Smoke Test, and Release Build, including explicit representative selection, changed-surface smoke expansion, metadata, QA reporting, and a release-build fixture.
- Rider Composition Preview catalog and approved-plan workflow with stable module codes, isolated preview artifacts, selection-plan fixtures, runtime validation, metadata, and QA reporting.
- Rider grounded-image `image_workflow` contract for generated/edited imagery, including intended slot, approved source assets, prompt record, output checksum/dimensions, placement constraints, approval state, metadata, asset-manifest, and QA reporting.
- The Rider manifest-source config at `projects/the-rider/manifest-source.json`, currently validating the repository local-cache fallback because no stable public manifest URL is configured.
- Wellness Composition Preview pilot fixtures with approved Phase 8 module selection, approved composition plan, grounded gym-image provenance, and a generated hero tied to the Rider gym source plus scaffold logo reference.
- Root `LIMITATIONS.md` register covering evidence-backed Phase 1 through Phase 12 limitations, scoring opportunities, current controls, and closure criteria.

### Changed

- All Rider runtime fixtures include approved allocation plans; internal wellness fixture wording removes the historical repetition pattern retained in negative tests.
- Copy validation blocks all build modes before rendering or asset download and preserves approved wording and the last passing package.
- Phase 10 is implemented for The Rider; LIM-003 is closed and LIM-004 is mitigated, with OCR, truth verification, and similarity calibration still documented.

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
- Roadmap, PRD, status, and versioning records now distinguish approved future specs from implemented runtime features.
- Ordinary Rider smoke fixtures now render one branded representative variant; Release Build preserves the full internal matrix.
- Composition Preview and Release Build now require an approved composition plan; technical Smoke Test remains the explicit diagnostic bypass.
- Generated or edited Rider imagery now enters runtime builds only through explicit `image_workflow_id` provenance records; ordinary `asset_id` image slots remain the approved existing-asset path and do not trigger image generation.

### Validated

- Acceptance-gap follow-up passes 79 tests, including 18 allocation tests; responsive branch duplication counts once while a second owner still fails. Runtime behavior and the audited live pilot remain unchanged.

- Phase 10 full unittest discovery passes 78 tests, including Phase 7-9 regression coverage.
- Live wellness Composition Preview passes 86 QA checks, 26 allocation checks, 23 copy units, 1 branded variant, and 9 assets; its ZIP contains 13 byte-matching files with validated asset checksums and no external or missing image references.

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
- Full unittest discovery passes 49 tests.
- Ordinary Rider smoke passes as `smoke-test` with 1 branded variant, 54 QA checks, 9 packaged assets, no external image references, and a valid ZIP.
- Rider wellness smoke passes as `smoke-test` with 1 branded variant, 55 QA checks, 9 packaged assets, no external image references, and a valid ZIP.
- Rider release-build validation passes with 9 variants, 222 QA checks, 17 packaged assets, Diana Kosov present, Jake Lecce absent, no external image references, and a valid ZIP.
- Full unittest discovery passes 55 tests.
- Composition catalog generation produces 16 selectable non-footer entries plus review Markdown and isolated HTML preview snippets.
- Approved release-build composition plan records 5 selected module codes, 3 required asset slots, 22 editable slots, and passes release-build package QA with 226 checks.
- Full unittest discovery passes 61 tests.
- Manifest-source validation passes for The Rider local-cache fallback with 206 validated manifest assets and no configured public URL.
- Rider wellness Composition Preview pilot passes with 1 branded variant, approved composition plan `rider-wellness-composition-preview`, 1 grounded image workflow item, 59 QA checks, 9 packaged assets, no external or missing image references, and a valid ZIP.

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
