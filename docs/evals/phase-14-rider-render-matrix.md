# Phase 14 Rider Render Matrix Evidence

**Date:** 2026-10-03
**Campaign:** Rider wellness Composition Preview
**Variant:** Branded
**Automated result:** Pass
**Human approval:** Pending
**Scope:** Chromium browser preview only

**Creative baseline status:** Rejected for creative approval. This is a technical regression fixture with known stale hero-selection, image-grounding, and repeated-copy defects.

## Automated Matrix

| Entry | Viewport | Scheme | Overflow | Images | Errors | Result |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| `desktop-light` | 1440 x 1200 | Light | 0px | 6/6 | 0 | Pass |
| `mobile-light` | 390 x 844 | Light | 0px | 6/6 | 0 | Pass |
| `desktop-dark` | 1440 x 1200 | Dark preference | 0px | 6/6 | 0 | Pass |
| `mobile-dark` | 390 x 844 | Dark preference | 0px | 6/6 | 0 | Pass |

All entries rendered a non-empty document and screenshot. No image, request, page, or console failures were recorded. The input HTML SHA-256 is `fcd0bed5e6ea6c5c2ca46ef76a130ecf0e3fee8c29f80cd8ecd9fcd4b867ad32`.

Light and dark screenshots are byte-identical at each viewport. This proves that Chromium's dark preference does not alter this fixed-palette email; it does not prove that email clients will avoid their own color rewriting.

## Agent-Assisted Visual Inspection

The desktop preview preserves a centered 600px-style email canvas with coherent section ordering, image crops, calls to action, and footer placement. The mobile preview stacks into one column without visible collisions, clipping, or horizontal overflow. Text remains readable and all six image elements render.

Two non-blocking findings remain:

1. The authority message beginning “From the creators…” is visibly repeated across multiple approved/static modules. This is an editorial/static-content decision, not a rendering defect.
2. Browser dark preference produces no alternate styling. Real client dark-mode rewriting remains untested.

This inspection is not creative approval, human approval, accessibility certification, or email-client certification. The fixture must not be used to claim completion of Phase 15 creative-fidelity requirements.

## Supported Client Review Matrix

| Client surface | Target | Status |
| --- | --- | --- |
| Chromium browser preview | Desktop and mobile, light/dark preference | Passed |
| Gmail web | Current Chrome desktop | Pending |
| Outlook web | Current Chrome desktop | Pending |
| Outlook desktop | Current Windows Word rendering engine | Pending |
| Apple Mail | Current macOS | Pending |
| Gmail mobile | Current iOS or Android | Pending |
| Apple Mail mobile | Current iOS | Pending |

## Evidence

- Machine report: `docs/evals/render-matrix/rider-wellness-v1/render-report.json`
- Visual worksheet: `docs/evals/render-matrix/rider-wellness-v1/visual-review.md`
- Screenshots: `desktop-light.jpg`, `mobile-light.jpg`, `desktop-dark.jpg`, and `mobile-dark.jpg`
- Render tool: `tools/email_render_matrix/render_matrix.cjs`

LIM-005 remains open until the pending human decision and real-client matrix are recorded.
