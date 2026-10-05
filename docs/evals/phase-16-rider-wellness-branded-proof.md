# Phase 16 Rider Wellness Branded Proof

**Date:** 2026-10-05

**Status:** Owner approved as the canonical Phase 16 promotion proof

## Approved Inputs

- Sequence: `SEQ-LF-07`
- Header and hero configuration: `CFG-05` (`H-01` plus `AI-01`)
- Generated-image candidate: Candidate B, Rider Gym 2
- Source SHA-256: `705344436a46eefe0108c2fbe70e090cd58cd343ca2eb60d61cc8012ebbfd9c9`
- Candidate SHA-256: `b79df805bb8bc04bf4ec147e3ca1338ce7d27e62bc76fefdfe209d281a02fcb3`
- Candidate dimensions: 1672 x 941
- Attribution: the source copyright credit remains visibly present
- Output scope: one branded Composition Preview

The owner selected `SEQ-LF-07`, approved the refined result as the best proof produced so far, and then accepted the recommendation to promote Phase 16 as the next priority. That decision is recorded as canonical scaffold approval.

## Composition

The proof renders:

1. Two-column dark header with live campaign headline
2. Approved Rider Gym 2 generated hero
3. Default-dark long-form body with live subheading and primary paragraph
4. Approved Rider recovery-spa image
5. Secondary paragraph
6. Three leading terms and one payoff
7. One locked developer-authority block
8. Locked curated-design block with its wellness-relevant sauna rendering
9. Closing pre-footer CTA copy
10. Locked branded footer

Optional eyebrow, amplified list, follow-up list, and secondary image blocks are omitted cleanly. Their scaffold examples do not appear in the proof.

The latest scaffold revision makes the list families row-conditional. This proof supplies the leading-term list and paragraph payoff, so their rows remain. It supplies no amplified list or list-style follow-up payoff, so those complete rows are absent rather than rendered empty.

## Package Evidence

- Canonical runtime fixture: `projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-composition-preview.runtime.json`
- Canonical selection: `projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-composition-selection.json`
- Canonical composition plan: `projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-composition-plan.json`
- Build mode: `composition-preview`
- Variant count: 1 branded preview
- QA: 69 checks passed, zero failed
- Copy allocation: 13 approved logical owners, including two derived locked static owners
- Packaged assets: 8
- HTML SHA-256: `b82bcc430806bd174e621f379ee4a5ef132bab59900e50c4af1188700580ea60`
- ZIP: generated successfully under ignored local `campaign-output/`

## Copy And Marker Verification

The rendered HTML contains exactly one occurrence each of:

- `SAME ROUTINE`
- `SAME MEMBERSHIP`
- `NEW CITY`
- `WITH THE RIDER AT THE CENTER OF IT.`
- The locked developer-authority statement
- `CURATED DESIGN...`
- `KEEP YOUR MIAMI ROUTINE CLOSE TO HOME.`

It contains no `START -` or `END -` authoring markers, no lorem ipsum, and balanced table tags.

## Browser Inspection

The original proof revision was inspected at 748px and 390 x 844. After adding `S-02`, the revised proof was reloaded in a fresh in-app browser tab and inspected at 1280px.

| View | Horizontal overflow | Images loaded | Broken images | Result |
|---|---:|---:|---:|---|
| Revised proof, 1280px | 0px | 6/6 | 0 | Passed |

Visual inspection of the latest full-page proof found coherent stacking, readable live text, retained image attribution, intact CTA hierarchy, the packaged sauna background directly after `S-01`, no empty conditional list rows, and no visible overlap in the header, body, static blocks, pre-footer, or branded footer.

## Static-Block Selection Guidance

- `S-02` is machine-tagged for wellness, sauna, spa, recovery, and amenities. It may be considered for wellness-related emails or invites when the sauna scene supports the narrative.
- `S-04` is machine-tagged for arrival, building entrance, exterior, hospitality, and welcome. It depicts arrival at The Rider and is not a wellness scene.
- `S-01` immediately followed by `S-02` is an approved composition exception. Other combinations within the `rider-static-message` group remain mutually exclusive.

The packaged sauna background resolves to `images/sauna-7957fadc8be8.jpg` through computed CSS. After canonical promotion, the exact proof passed the four-entry Playwright browser matrix and agent-assisted screenshot review at 1440 x 1200 and 390 x 844 under light and dark browser preferences. All images load, horizontal overflow is zero, and no request, page, console, alignment, clipping, or overlap failures were found. See the [canonical client matrix](phase-16-rider-canonical-client-matrix.md). These browser checks are not Gmail, Outlook, Apple Mail, or native-client certification.

## Promotion Result

The Phase 16 scaffold, metadata, slot map, and live fixtures are canonical. A no-override build reproduced this proof with the same HTML SHA-256, 69 passing QA checks, eight packaged assets, and zero authoring-marker leaks. The Phase 15 trio remains archived as regression provenance. Native email-client testing and full release-matrix review remain open.
