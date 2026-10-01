# Project Status

**Product:** OnBrand Design  
**Owner:** Cervera Real Estate, Inc.  
**Author:** Felix Mendoza  
**Version:** 0.1.0  
**Updated:** 2026-09-30  
**Overall status:** Multi-project foundation complete; Rider asset integration in progress

## Completed

- Branded the framework as OnBrand Design.
- Established Cervera Real Estate, Inc. ownership and Felix Mendoza authorship.
- Licensed the framework under Apache-2.0.
- Changed the repository from one Rider package to a scalable project registry.
- Assigned collision-safe project-specific skill IDs.
- Added complete The Rider and provisional Cassia project folders.
- Added a reusable starter template and project generator.
- Preserved explicit-only invocation in Codex and Claude Code.
- Defined campaign modes, required modules, variants, packaging, and QA foundations.
- Created and live-tested the Dropbox master-manifest synchronizer for The Rider.
- Added local `.env` handling without distributing credentials.
- Documented persistent GitHub SSH authentication, Dropbox refresh credentials, CI secrets, and rotation boundaries.
- Added a contextual copy-quality pass, audit mode, and evaluation cases.
- Added PRD, phased specs, status, roadmap, audit, changelog, attribution, and versioning.

## Project Portfolio

| Project | Status | Next requirement |
|---|---|---|
| The Rider | In progress | Runtime asset-manifest integration and canonical HTML/footers |
| Cassia | Scaffold | Cassia brand materials, asset catalog, HTML, and footers |

## In Progress

- Wire The Rider email skill to read its master Dropbox `manifest.json`.
- Define deterministic asset filtering, ranking, preview, and selection.
- Calibrate copy voice and watchlist exceptions from each project's approved materials.

## Waiting On Project Inputs

- The Rider canonical Beefree HTML and locked footer partials.
- Confirmed public URL for The Rider's canonical Dropbox manifest.
- Cassia brand standards, canonical HTML, footers, logos, and asset catalog.

## Release Blockers

- Choose GitHub organization/owner, repository URL, visibility, support contact, and CODEOWNERS identities.

## Next Milestone

Complete The Rider Phase 1 asset-catalog integration, then use the resulting implementation and tests to harden the shared project starter before onboarding additional developments.
