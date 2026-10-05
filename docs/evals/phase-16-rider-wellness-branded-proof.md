# Phase 16 Rider Wellness Branded Proof

**Date:** 2026-10-05

**Status:** Branded Composition Preview generated; owner visual feedback pending

## Approved Inputs

- Sequence: `SEQ-LF-07`
- Header and hero configuration: `CFG-05` (`H-01` plus `AI-01`)
- Generated-image candidate: Candidate B, Rider Gym 2
- Source SHA-256: `705344436a46eefe0108c2fbe70e090cd58cd343ca2eb60d61cc8012ebbfd9c9`
- Candidate SHA-256: `b79df805bb8bc04bf4ec147e3ca1338ce7d27e62bc76fefdfe209d281a02fcb3`
- Candidate dimensions: 1672 x 941
- Attribution: the source copyright credit remains visibly present
- Output scope: one branded Composition Preview

The owner's request to begin the branded proof is recorded as approval to use the proposed `SEQ-LF-07` sequence for this review build. It is not canonical scaffold approval.

## Composition

The proof renders:

1. Two-column dark header with live campaign headline
2. Approved Rider Gym 2 generated hero
3. Default-dark long-form body with live subheading and primary paragraph
4. Approved Rider recovery-spa image
5. Secondary paragraph
6. Three leading terms and one payoff
7. One locked developer-authority block
8. Closing pre-footer CTA copy
9. Locked branded footer

Optional eyebrow, amplified list, follow-up list, and secondary image blocks are omitted cleanly. Their scaffold examples do not appear in the proof.

## Package Evidence

- Runtime fixture: `projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-phase16-composition-preview.runtime.json`
- Selection: `projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-phase16-composition-selection.json`
- Composition plan: `projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-phase16-composition-plan.json`
- Build mode: `composition-preview`
- Variant count: 1 branded preview
- QA: 64 checks passed, zero failed
- Copy allocation: 12 approved logical owners, including the derived locked static owner
- Packaged assets: 7
- HTML SHA-256: `ad40358e05d393925d3a75010af16f30bdd19c57b48b17d7be3a6c2ddcc1914a`
- ZIP: generated successfully under ignored local `campaign-output/`

## Copy And Marker Verification

The rendered HTML contains exactly one occurrence each of:

- `SAME ROUTINE`
- `SAME MEMBERSHIP`
- `NEW CITY`
- `WITH THE RIDER AT THE CENTER OF IT.`
- The locked developer-authority statement
- `KEEP YOUR MIAMI ROUTINE CLOSE TO HOME.`

It contains no `START -` or `END -` authoring markers, no lorem ipsum, and balanced table tags.

## Browser Inspection

The local proof was inspected in the Codex in-app browser at the default 748px viewport and at a temporary 390 x 844 mobile viewport.

| View | Horizontal overflow | Images loaded | Broken images | Result |
|---|---:|---:|---:|---|
| Default browser viewport, 748px | 0px | 6/6 | 0 | Passed |
| Mobile viewport, 390px | 0px | 6/6 | 0 | Passed |

Visual inspection found coherent stacking, readable live text, retained image attribution, intact CTA hierarchy, and no visible overlap in the header, body, pre-footer, or branded footer.

The standalone Playwright render-matrix command remains unavailable inside the managed macOS shell because Chromium cannot register its Mach rendezvous port. No matrix success is claimed. The in-app browser checks are review evidence, not Gmail, Outlook, Apple Mail, or native-client certification.

## Promotion Boundary

The Phase 15 scaffold remains canonical. This Phase 16 proof is open for owner critique and iteration. Canonical promotion, full variant generation, and real-client testing remain blocked until the owner approves the refined composition.
