# Phase 16 Parser And Metadata Evidence

**Date:** 2026-10-04

**Status:** Passed; runtime promotion pending

## Scope

This checkpoint validates the corrected Phase 16 Rider scaffold as an authoring document. It does not promote that scaffold into campaign rendering.

## Parser Results

- Beefree rows: 94
- Marker elements: 68
- Row-level modules: 20
- Inline or nested annotations: 14
- Nested annotation relationships: 1, `body-list-amplification` inside `body-amplified-list`
- Standalone granular blocks: 1, `body-inline-image-secondary`
- Marker-only rendering: removes all four authoring colors and all `START -` / `END -` text while retaining annotated content rows

`ModuleBoundary` remains backward compatible with the current canonical scaffold. `AnnotationBoundary` records the exact marker elements, containing module, containing annotation, nesting depth, content rows, and enclosed HTML.

## Metadata Results

The checksum-bound metadata file is:

`projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.phase16-block-metadata.json`

It defines:

- 20 modules with stable IDs and codes
- 14 granular fields or blocks with stable IDs
- Dark-only invite behavior
- Dark-default, user-selectable light long-form body behavior
- Header-versus-integrated-header exclusion
- At-most-one static message selection
- Required replacement of the second image placeholder
- Locked, editable, optional, repeating, and generated-copy field distinctions
- Image grounding, crop, campaign, sequence, mobile, and Outlook expectations

The loader binds metadata to the exact scaffold SHA-256 and verifies full source-label, occurrence, and marker-row coverage. It also verifies annotation parent IDs against parsed nesting.

## Validation

- Focused Phase 16 and legacy scaffold tests: 13 passed
- Full repository test discovery: 166 passed
- Existing canonical scaffold behavior: unchanged
- Phase 16 canonical promotion: not performed

## Next Work

Deterministic slots and composition rules are now complete. See [Phase 16 slots and composition evidence](phase-16-slots-and-composition.md). Remaining work is to generate and inspect isolated previews and sequence options, then produce a new branded proof for owner review before canonical promotion.
