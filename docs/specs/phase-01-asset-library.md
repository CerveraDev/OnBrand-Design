# Phase 1: Dropbox Asset Catalog And Selection

**Status:** In progress  
**Target:** 0.2.0  
**Depends on:** Phase 0

## Goal

Allow each explicitly invoked project email skill to discover, rank, select, and package approved project images and PDFs from its canonical Dropbox-backed master manifest.

## Completed

- Master manifest uses array-valued `category` and `approved_for`.
- Synchronizer handles additions, removals, duplicate filenames, and renames.
- Stable matching preserves curated metadata.
- Atomic writes and `.bak` recovery are implemented.
- Local `.env` configuration is supported.
- The Rider live synchronization validated 195 assets and preserved 191 curated records.

## Remaining Requirements

- ASSET-001: Configure a stable public URL or local fallback for each project's master manifest.
- ASSET-002: Validate manifest schema before selection.
- ASSET-003: Filter by media type, `approved_for`, category overlap, orientation, and campaign needs.
- ASSET-004: Rank candidates and explain recommendations without inventing metadata.
- ASSET-005: Ask for approval when several materially different candidates remain.
- ASSET-006: Download only selected assets into the campaign workspace.
- ASSET-007: Preserve filename provenance and record source identity in campaign output.
- ASSET-008: Define PDF behavior: package/link or render an approved page as an image.
- ASSET-009: Continue gracefully from a validated local cache if the public manifest is unavailable.
- ASSET-010: Keep manifest refresh separate from normal campaign generation unless explicitly requested.

## Acceptance Criteria

- A realistic campaign brief returns relevant candidates from the manifest.
- Hero selection never uses an asset lacking the required approval classification.
- Duplicate filenames are distinguished by Dropbox identity/path.
- Selected files download successfully and checksum or size validation catches incomplete transfers.
- The source master manifest is never altered during campaign generation.
- A campaign package contains only final selected assets and records their provenance.

## Risks

- Public Dropbox links may redirect or expire after link changes.
- Sparse or inconsistent categories may weaken ranking.
- PDFs may require rendering libraries and user approval of the chosen page.
- A short-lived access token affects refresh operations but should not affect public-manifest consumption.
