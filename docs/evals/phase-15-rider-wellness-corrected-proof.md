# Phase 15 Rider Wellness Corrected Proof

**Status:** Branded Composition Preview generated; owner creative approval pending

**Date:** 2026-10-03

## Approved Inputs

- Header and hero configuration: `CFG-05` (`H-01` plus `AI-01`)
- Generated-image candidate: Candidate B, Rider Gym 2
- Source asset: Dropbox `id:31E0v0XEN2IAAAAAAAAAIg`
- Source SHA-256: `705344436a46eefe0108c2fbe70e090cd58cd343ca2eb60d61cc8012ebbfd9c9`
- Candidate SHA-256: `b79df805bb8bc04bf4ec147e3ca1338ce7d27e62bc76fefdfe209d281a02fcb3`
- Candidate dimensions: 1672 x 941
- Text policy: campaign headline and subheading remain live HTML
- Attribution: the source copyright credit remains visibly present in the selected candidate

The decision record is retained in [the source-versus-candidate review](artifacts/phase-15-rider-wellness-grounding-v1/review.json). Candidate A remains non-selected evidence and is not used by the package.

## Composition Result

The corrected proof uses the two-column header, the approved Gym 2 image, the dark-then-light body, Static Block 2, Static Block 1, and the branded footer. The two repeated authority rows inside `B-04` are now independent campaign slots. They contain distinct wellness messages, while Static Block 1 remains the only canonical “From the creators…” statement.

The optional subheading is placed in the first live body text slot immediately after the image because `H-01` exposes one headline slot and a locked logo, but no dedicated subheading slot.

## Package Evidence

- Runtime fixture: `projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-phase15-composition-preview.runtime.json`
- Composition plan: `projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-phase15-composition-plan.json`
- Build mode: `composition-preview`
- Variant count: 1 branded preview
- QA: 90 checks passed, zero failed
- Copy allocation: 27 approved logical owners
- HTML SHA-256: `5c488dc6bb743e48d8a7ec1ad3e236738c9253a73b2c01855b071b8bdd91dcb1`
- ZIP: self-contained package generated successfully; the archive hash is not used as stable evidence because ZIP entry timestamps change on rebuild

The generated package remains local under `campaign-output/` and is not source-controlled.

## Verification

- Full unit-test discovery passes 160 tests.
- Runtime QA confirms the approved CFG-05 plan, grounded image provenance, packaged asset checksums, relative image resolution, and copy-allocation gates.
- Browser inspection confirms the two-column header, selected Gym 2 hero, visible source credit, live subheading, distinct body authority messages, one canonical static authority statement, and branded footer.

## Remaining Approval

This artifact is the corrected creative baseline candidate. Owner approval of the assembled branded email is still required before generating the complete authorized variant matrix or treating it as the Phase 14 real-client test baseline. Gmail, Outlook, and Apple Mail certification remain outside this proof.
