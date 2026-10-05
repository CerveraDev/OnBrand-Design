# Phase 16 Parser And Metadata Evidence

**Date:** 2026-10-04

**Status:** Passed; runtime promotion pending

## Scope

This checkpoint validates the corrected Phase 16 Rider scaffold as an authoring document. It does not promote that scaffold into campaign rendering.

## Parser Results

- Beefree rows: 102
- Marker elements: 74
- Row-level modules: 20
- Inline or nested annotations: 17
- Nested annotation relationships: 5
- Conditional row containers: 4, covering leading terms, paragraph payoff, amplified list, and list-style follow-up payoff
- Standalone granular blocks: 1, `body-inline-image-secondary`
- Marker-only rendering: removes all four authoring colors and all `START -` / `END -` text while retaining annotated content rows

`ModuleBoundary` remains backward compatible with the current canonical scaffold. `AnnotationBoundary` records the exact marker elements, containing module, containing annotation, nesting depth, content rows, and enclosed HTML.

## Metadata Results

The checksum-bound metadata file is:

`projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.phase16-block-metadata.json`

It defines:

- 20 modules with stable IDs and codes
- 17 granular fields or blocks with stable IDs
- Dark-only invite behavior
- Dark-default, user-selectable light long-form body behavior
- Header-versus-integrated-header exclusion
- At-most-one static message selection
- Required replacement of the second image placeholder
- Locked, editable, optional, repeating, and generated-copy field distinctions
- Image grounding, crop, campaign, sequence, mobile, and Outlook expectations

The loader binds metadata to the exact scaffold SHA-256 and verifies full source-label, occurrence, and marker-row coverage. It also verifies annotation parent IDs against parsed nesting.

## Validation

- Focused Phase 16 parser/runtime tests: 19 passed
- Full repository test discovery: 179 passed
- Existing canonical scaffold behavior: unchanged
- Phase 16 canonical promotion: not performed

## Next Work

Deterministic slots, composition rules, galleries, and the regenerated branded proof are complete. See [Phase 16 slots and composition evidence](phase-16-slots-and-composition.md) and [the branded proof](phase-16-rider-wellness-branded-proof.md). Remaining work is owner visual approval, reproducible browser-matrix evidence, native email-client review, and the canonical promotion decision.
