# Phase 2: Beefree, Brand, And Template Calibration

**Status:** Implemented for The Rider; waiting on other project assets
**Target:** 0.3.0  
**Depends on:** Phase 0

## Goal

Turn each project's canonical Beefree-generated HTML and locked footer partials into verified brand, module, responsive, and assembly rules.

## Inputs Required

- Canonical Beefree-generated project HTML.
- Branded footer partial.
- Broker-neutral footer partial.
- One footer partial for each in-house agent.
- Referenced logo and footer assets.

## Requirements

- TEMPLATE-001: Preserve source files unchanged as canonical fixtures.
- TEMPLATE-002: Extract colors, typography, widths, spacing, buttons, image blocks, and responsive classes.
- TEMPLATE-003: Identify Outlook conditionals and compatibility patterns.
- TEMPLATE-004: Define the exact body/footer insertion boundary.
- TEMPLATE-005: Document locked versus campaign-editable markup.
- TEMPLATE-006: Replace provisional brand and HTML assumptions with observed rules.
- TEMPLATE-007: Render representative desktop and mobile previews.
- TEMPLATE-008: Preserve every supplied scaffold revision as immutable provenance.
- TEMPLATE-009: Classify headers, heroes, bodies, static blocks, and footers in machine-readable metadata.
- TEMPLATE-010: Treat static blocks as locked optional content with explicit campaign decisions.

## Acceptance Criteria

- Reassembled canonical content matches the source structure without footer breakage.
- Each footer variant can be swapped without modifying the shared body.
- Brand tokens and module rules cite observed source patterns.
- No unsupported CSS or invented design token remains in the calibrated references.
- Header/hero compatibility and all static-block decisions are machine validated.
