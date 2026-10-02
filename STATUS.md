# Project Status

**Product:** OnBrand Design  
**Owner:** Cervera Real Estate, Inc.  
**Author:** Felix Mendoza  
**Version:** 0.1.0  
**Updated:** 2026-10-02
**Overall status:** Multi-project foundation complete; Rider campaign runtime implemented and smoke-tested

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
- Verified live Dropbox manifest synchronization with refresh-token authentication and no stored access token.
- Added a contextual copy-quality pass, audit mode, and evaluation cases.
- Added PRD, phased specs, status, roadmap, audit, changelog, attribution, and versioning.
- Added a dependency-light manifest validator and deterministic asset shortlist selector.
- Wired The Rider email skill and starter references to load the manifest, filter and rank approved candidates, and require approval when top candidates are materially different.
- Preserved the supplied Rider Beefree scaffold as an immutable source copy and added a corrected canonical runtime copy.
- Formalized 13 Rider scaffold module boundaries, marker exclusion rules, brand palette, typography, and footer contracts.
- Added one JSON record per in-house agent, a shared schema, and a deterministic active-agent index for Rider agent variants.
- Renamed the former unbranded footer workflow to outside-broker customizable and preserved Rider/legal footer content.
- Synchronized the reorganized `20. People` Dropbox library and registered all six verified Rider in-house agents with manifest-backed headshots.
- Restricted in-house headshots to `agent-footer` approval and Diego Ojeda likeness references to the explicit image-generation workflow.
- Added the Rider campaign JSON schema, deterministic scaffold slot map, module composer, footer renderer, portable asset downloader, package generator, and blocking QA runtime.
- Completed a non-production smoke build with branded, outside-broker customizable, and six agent variants.
- Verified 221 runtime QA checks, 18 packaged assets (17 images and one PDF), eight HTML files, and a self-contained ZIP.

## Project Portfolio

| Project | Status | Next requirement |
|---|---|---|
| The Rider | Runtime ready for pilot campaigns | Public manifest/cache configuration and human compatibility review |
| Cassia | Scaffold | Cassia brand materials, asset catalog, HTML, and footers |

## In Progress

- Configure The Rider's stable public manifest URL or validated local cache fallback.
- Run the first user-approved campaign through the Rider runtime.
- Perform representative visual and email-client compatibility review beyond structural QA.
- Calibrate copy voice and watchlist exceptions from each project's approved materials.

## Waiting On Project Inputs

- Confirmed public URL for The Rider's canonical Dropbox manifest.
- Cassia brand standards, canonical HTML, footers, logos, and asset catalog.

## Release Blockers

- Choose support contact and CODEOWNERS identities.

## Next Milestone

Pilot the Rider runtime with approved campaign content, then generalize the proven architecture into the shared project starter before onboarding additional developments.
