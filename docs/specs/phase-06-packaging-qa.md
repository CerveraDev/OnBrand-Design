# Phase 6: Distribution Packaging And QA

**Status:** Partially specified  
**Target:** 0.7.0  
**Depends on:** Phase 5

## Goal

Deliver a complete, traceable campaign folder and ZIP that the user's team can distribute without searching for source assets.

## Requirements

- PACKAGE-001: Include all required HTML variants under `html/`.
- PACKAGE-002: Include every final used image under `images/` and selected PDFs under `documents/` when applicable.
- PACKAGE-003: Include no unused candidates or corpus-wide asset dump.
- PACKAGE-004: Create valid `asset-manifest.json` with provenance and variant usage.
- PACKAGE-005: Verify all local HTML asset references resolve within the package.
- PACKAGE-006: Identify external URLs and deployment replacements explicitly.
- PACKAGE-007: Open representative HTML files and verify assets render.
- PACKAGE-008: Create the ZIP only after folder validation passes.
- PACKAGE-009: Report limitations rather than calling a package self-contained when external assets remain.

## Acceptance Criteria

- Unzipping on another computer preserves the expected folder structure.
- Every manifest entry maps to a real file or documented external URL.
- No secret, source-corpus path, temporary path, or rejected image is present.
- Branded, outside-broker customizable, and all agent variants pass footer and CTA checks.
