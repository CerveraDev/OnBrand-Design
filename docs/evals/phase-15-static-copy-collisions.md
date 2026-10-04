# Phase 15 Static Copy Collision Evidence

**Status:** Workstream C implemented

**Date:** 2026-10-03

## Result

Every included Rider static block now contributes its complete visible editorial text to the Phase 10 copy inventory automatically. Campaign authors no longer need to remember to declare locked static copy before exact, normalized, restricted-phrase, and near-duplicate checks can see it.

An explicit static content unit remains supported for a narrow owner-approved decision, but its text must exactly match all visible copy in the locked block. Partial declarations are rejected. Similarity exemptions apply only to an exact two-unit pair or an explicit `left-id+right-id` pair; a many-item exemption list cannot silently exempt every pair within it.

Findings retain context:

- Occurrence results include the content unit owner.
- Restricted-phrase results list matched runtime owners.
- Similarity results include left and right owners and whether the exact pair was exempted.

## Regression Cases

- Including `STATIC BLOCK 1` automatically creates `locked-static-block-1-copy` with both the authority statement and `OWN BETTER` lockup.
- Reusing “From the creators of The Bond” in campaign-authored body copy while `STATIC BLOCK 1` is included exceeds the one-owner restricted-phrase cap and blocks.
- Declaring only “From the creators of The Bond” as the static unit fails because it omits the rest of the visible locked copy.
- A three-unit broad exemption does not suppress a blocking similarity finding between two of those units.
- An intentionally approved two-unit refrain remains supported.

Full unit-test discovery passes 158 tests after the Workstream A and C changes.

## Remaining Boundary

The deterministic scorer still cannot prove semantic equivalence for arbitrary paraphrases. Review-band findings remain human-owned, and Jev version 1 remains rejected for production routing. Static extraction and collision enforcement do not rewrite locked or campaign-authored copy.
