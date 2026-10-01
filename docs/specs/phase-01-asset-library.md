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
- A local authorization helper obtains, verifies, and stores an offline refresh token without printing it.
- The Rider live synchronization validated 195 assets and preserved 191 curated records.
- Refresh-token authentication completed a second live synchronization with 195 records preserved, zero additions or removals, and no stored access token.
- Shared `tools.asset_selection` validates local master manifests without Dropbox credentials.
- Asset selection rejects malformed `category` or `approved_for` metadata instead of coercing it.
- Candidate filtering supports media type, required `approved_for` values, category overlap, and orientation when available.
- Candidate ranking is deterministic and returns transparent scoring reasons plus a compact shortlist.
- The Rider email skill and neutral project starter now instruct campaign work to run selector-based manifest selection and present materially different top candidates for approval.

## Remaining Requirements

- ASSET-001: Configure a stable public URL or local fallback for each project's master manifest.
- ASSET-006: Download only selected assets into the campaign workspace.
- ASSET-007: Preserve filename provenance and record source identity in campaign output.
- ASSET-008: Define PDF behavior: package/link or render an approved page as an image.
- ASSET-009: Continue gracefully from a validated local cache if the public manifest is unavailable.
- ASSET-010: Keep manifest refresh separate from normal campaign generation unless explicitly requested.
- ASSET-011: Refresh-token authorization must update only the ignored local `.env` after successful Dropbox verification.

## Acceptance Criteria

- A realistic campaign brief returns relevant candidates from the manifest.
- Hero selection never uses an asset lacking the required approval classification.
- Duplicate filenames are distinguished by Dropbox identity/path.
- Selected files download successfully and checksum or size validation catches incomplete transfers. (Pending.)
- The source master manifest is never altered during campaign generation.
- A campaign package contains only final selected assets and records their provenance. (Pending.)

## Risks

- Public Dropbox links may redirect or expire after link changes.
- Sparse or inconsistent categories may weaken ranking.
- PDFs may require rendering libraries and user approval of the chosen page.
- A short-lived access token affects refresh operations but should not affect public-manifest consumption.
