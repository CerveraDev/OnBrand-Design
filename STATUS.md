# Project Status

**Product:** OnBrand Design  
**Owner:** Cervera Real Estate, Inc.  
**Author:** Felix Mendoza  
**Version:** 0.1.0  
**Updated:** 2026-10-03
**Overall status:** Rider runtime through Phase 10 plus Phase 11 deterministic Codex/Claude/CLI adapters and parity; live model invocation remains unverified

## Completed

- Branded the framework as OnBrand Design.
- Established Cervera Real Estate, Inc. ownership and Felix Mendoza authorship.
- Licensed the framework under Apache-2.0.
- Changed the repository from one Rider package to a scalable project registry.
- Assigned collision-safe project-specific skill IDs.
- Added complete The Rider and provisional Cassia project folders.
- Added a reusable starter template and project generator.
- Preserved explicit-only invocation through portable canonical skills and platform-specific workspace wrappers.
- Defined campaign modes, required modules, variants, packaging, and QA foundations.
- Created and live-tested the Dropbox master-manifest synchronizer for The Rider.
- Added local `.env` handling without distributing credentials.
- Documented persistent GitHub SSH authentication, Dropbox refresh credentials, CI secrets, and rotation boundaries.
- Verified live Dropbox manifest synchronization with refresh-token authentication and no stored access token.
- Added a contextual copy-quality pass, audit mode, and evaluation cases.
- Added PRD, phased specs, status, roadmap, audit, changelog, attribution, and versioning.
- Added a dependency-light manifest validator and deterministic asset shortlist selector.
- Wired The Rider email skill and starter references to load the manifest, filter and rank approved candidates, and require approval when top candidates are materially different.
- Preserved the supplied Rider Beefree scaffold as an immutable source copy and added a corrected canonical runtime copy.
- Formalized 13 Rider scaffold module boundaries, marker exclusion rules, brand palette, typography, and footer contracts.
- Added one JSON record per in-house agent, a shared schema, and a deterministic active-agent index for Rider agent variants.
- Renamed the former unbranded footer workflow to outside-broker customizable and preserved Rider/legal footer content.
- Synchronized the reorganized `20. People` Dropbox library, archived former Sales Director Jake Lecce from the active runtime roster, and registered Paulie Hankin's replacement headshot.
- Restricted in-house headshots to `agent-footer` approval and Diego Ojeda likeness references to the explicit image-generation workflow.
- Added the Rider campaign JSON schema, deterministic scaffold slot map, module composer, footer renderer, portable asset downloader, package generator, and blocking QA runtime.
- Completed a non-production smoke build with branded, outside-broker customizable, and six agent variants.
- Verified 221 runtime QA checks, 18 packaged assets (17 images and one PDF), eight HTML files, and a self-contained ZIP.
- Imported the revised 102-row Rider scaffold while preserving the prior source as provenance.
- Added four explicit-decision static blocks and machine-readable header/hero/body/static/footer metadata.
- Added header/hero compatibility checks and static-content locking before portable asset localization.
- Registered Paulie Hankin's manifest headshot as an approved in-house-agent footer asset while preserving all 205 existing curated records.
- Added Paulie Hankin as the verified Sales Director and restored the complete eight-variant smoke package with Paulie replacing Jake Lecce.
- Deleted Jake Lecce's retired headshot from Dropbox and synchronized the manifest from 206 to 205 records without changing any surviving curated arrays.
- Added Diana Kosov as a verified in-house sales agent after manifest synchronization discovered her approved headshot at `id:31E0v0XEN2IAAAAAAAABlg`.
- Recorded the user-confirmed correction that Paulie Hankin is a woman; agent records continue to omit gender and pronouns because footer rendering does not require them.
- Added and validated a separate Rider wellness smoke campaign with generated 16:9 hero art, approved wellness/arrival body assets, branded and outside-broker versions, seven in-house agent variants, a QA report, and a ZIP.
- Recorded approved-but-unimplemented planning specifications for Phases 7 through 11 and a deferred Phase 12 distribution profile plan.
- Added compatibility and distribution-security planning documents that keep Claude Code support and broker-only package claims explicitly unimplemented.
- Implemented Phase 7 build modes for The Rider runtime: Composition Preview, Smoke Test, and Release Build with explicit variant policy, representative selection, metadata, QA reporting, and release-matrix validation.
- Implemented Phase 8 Composition Preview for The Rider runtime with stable module codes, review artifacts, approved selection plans, compatibility validation, and composition metadata/QA reporting.
- Implemented Phase 9 Grounded Image Generation for The Rider runtime with a validated local manifest-cache fallback, structured image workflow provenance, source/output validation, release gating, and QA/manifest reporting.
- Added a root [limitations register](LIMITATIONS.md) so known limitations, scoring opportunities, deferred safeguards, and closure criteria remain discoverable before Phase 10 implementation.
- Implemented Phase 10 approved copy inventory/ownership, cross-surface normalized repetition, transparent near-duplicate scoring, narrow reuse exemptions, claim-reference gating, and metadata/QA reporting without rewriting approved text.
- Implemented Phase 11 versioned contracts, shared dispatch, manual-only wrappers, and 13-component blocking parity. Rider preview builds score 100 using real cached assets; live model invocation is unverified. See [evidence](docs/evals/phase-11-cross-platform-compatibility.md).

## Project Portfolio

| Project | Status | Next requirement |
|---|---|---|
| The Rider | Runtime ready for pilot campaigns | Public manifest/cache configuration and broader client compatibility review |
| Cassia | Scaffold | Cassia brand materials, asset catalog, HTML, and footers |

## Approved Specs, Not Implemented

- Phase 12: Distribution profiles remain deferred until public core, private project packs, and sanitized broker packages are physically separated.

## In Progress

- Perform representative visual and email-client compatibility review beyond structural QA.
- Calibrate copy voice and watchlist exceptions from each project's approved materials.
- Obtain live manual invocation evidence on permitted authenticated hosts; deterministic parity does not establish model behavior.
- Keep [LIMITATIONS.md](LIMITATIONS.md) current when audits, specs, QA runs, or implementation work discover new constraints.

## Waiting On Project Inputs

- Confirmed public URL for The Rider's canonical Dropbox manifest.
- Cassia brand standards, canonical HTML, footers, logos, and asset catalog.

## Release Blockers

- Choose support contact and CODEOWNERS identities.
- Do not claim authenticated live skill invocation or independent model-behavior parity until LIM-017 has evidence; deterministic adapter parity is implemented.
- Do not distribute broker-restricted packages until Phase 12 physical source/package separation is implemented.
- Do not treat generated-image visual faithfulness, email-client rendering, or legal/compliance review as automated approvals until their limitations are closed with committed evidence.

## Next Milestone

Run live manual adapter checks and broader visual/email-client review. Phase 11 deterministic parity is complete; Phase 12 distribution stays deferred.
