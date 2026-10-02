# Phase 5: HTML Assembly And Footer Variants

**Status:** Planned  
**Target:** 0.6.0  
**Depends on:** Phases 1-4, especially Phase 2

## Goal

Assemble approved content and assets into Beefree-compatible project HTML, then produce every required locked-footer variant from one shared body.

## Requirements

- HTML-001: Use the calibrated Beefree table, inline-style, responsive, and Outlook patterns.
- HTML-002: Produce a required hero with locked logo, headline, hero image, and optional subheading.
- HTML-003: Use flattened visuals when precise live overlays are unsafe.
- HTML-004: Build one canonical campaign body before variant generation.
- HTML-005: Append locked branded, outside-broker customizable, and agent footers without rewriting them.
- HTML-006: Keep project branding and required legal content in outside-broker customizable variants while replacing in-house contact ownership with supplied broker personalization or placeholders.
- HTML-007: Produce deterministic, descriptive filenames.
- HTML-008: Use relative packaged asset paths for review and documented hosted URLs for deployment when available.
- HTML-009: Resolve each in-house agent headshot by exact manifest `dropbox_id` and require an image under the configured in-house-agent path approved for the footer role.

## Acceptance Criteria

- Every variant has identical approved body content unless explicitly requested otherwise.
- Footer markup remains byte-identical to its approved partial where insertion permits.
- HTML contains no absolute local paths or invented destinations.
- Representative desktop/mobile rendering and Outlook-oriented structural checks pass.
- Every active-agent variant resolves exactly one approved headshot; likeness-reference assets cannot enter footer variants.
