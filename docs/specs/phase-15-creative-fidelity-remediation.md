# Phase 15: Creative Fidelity Remediation

**Status:** Workstreams A, B, and C implemented; corrected branded proof generated
**Target:** Corrected Rider Composition Preview before real email-client testing
**Depends on:** Phases 8, 9, 10, and 14

## Goal

Close the gap between deterministic runtime validity and the creative workflow the owner approved: visible labeled module selection, image generation grounded in an actual Rider rendering, and composition-time prevention of repeated static or campaign messages.

## Problem Statement

The Phase 14 Rider wellness fixture is technically valid but creatively stale. It renders one previously selected hero, uses an earlier generated environment, and includes repeated locked authority copy. Its screenshots remain useful for responsive regression testing, but they are not creative acceptance evidence.

## Workstream A: Labeled Visual Selection

Implementation evidence: [Rider header and hero gallery](../evals/phase-15-rider-hero-gallery.md). The owner selected `CFG-05`.

- FID-001: Preserve stable module codes from the canonical catalog.
- FID-002: Produce a rendered gallery for every eligible header and hero, not only isolated HTML files.
- FID-003: Every gallery item visibly includes its code, human label, header behavior, live/baked text behavior, image requirement, and compatibility notes outside the email preview.
- FID-004: Group standalone headers, non-header heroes, header-bearing heroes, and AI-image heroes separately.
- FID-005: Do not offer incompatible standalone-header/header-bearing-hero combinations.
- FID-006: Record the exact selected code or compatible header-plus-hero pair before image work begins.
- FID-007: Gallery screenshots are selection aids, not email-client certification.

## Workstream B: Source-Grounded Image Composition

Implementation evidence: [corrected Rider wellness proof](../evals/phase-15-rider-wellness-corrected-proof.md). Candidate B, Rider Gym 2, is the approved source-grounded hero.

- FID-008: A brief that names or implies a Rider room, amenity, facade, or other real environment must select an approved environment-base asset before generation.
- FID-009: Present one or two base-image candidates with asset ID, category, approval, and relevance notes for owner selection.
- FID-010: The generation request must include the approved environment image, not merely its metadata or description.
- FID-011: Record subject, pose, framing, focal point, crop, logo treatment, invariant architectural regions, and prohibited changes.
- FID-012: Tight framing requests must identify the intended subject scale and crop before generation.
- FID-013: Create source-versus-candidate review evidence with hashes and dimensions before approval.
- FID-014: A generated candidate cannot enter HTML until the owner approves visual environment preservation, subject placement, crop, logo fidelity, and text policy.
- FID-015: Metadata grounding alone is insufficient evidence of visual faithfulness.

## Workstream C: Static And Cross-Block Copy Collisions

Implementation evidence: [static copy collision evaluation](../evals/phase-15-static-copy-collisions.md).

- FID-016: Extract visible editorial copy from every selected locked static block and include it in the pre-composition copy inventory.
- FID-017: Compare selected static copy with campaign-authored live, metadata, alt, and declared baked-image copy.
- FID-018: Report exact, normalized, restricted-phrase, and review-band near-duplicate collisions with module context before plan approval.
- FID-019: Locked content remains immutable. Resolution occurs by excluding a block, selecting a different module, or recording a narrow owner-approved keep decision.
- FID-020: A broad static-content exemption may not hide repeated authority or campaign messages across selected blocks.
- FID-021: The “From the creators…” wellness repetition is the required regression case.
- FID-022: Responsive fallback branches continue to count as one logical owner.

## Approval Sequence

1. Generate the labeled header/hero gallery.
2. Owner selects exact module code or compatible pair.
3. Analyze selected static blocks and proposed campaign copy for collisions.
4. Owner resolves every blocking or review collision.
5. Select and approve the real Rider environment base image.
6. Create image candidates from the approved base.
7. Owner approves source-versus-candidate visual evidence.
8. Assemble one branded Composition Preview.
9. Run Phase 14 browser rendering and obtain creative approval.
10. Generate the full authorized variant matrix only after the branded proof is approved.

## Acceptance Criteria

- The owner can identify and select hero/header options visually by stable code.
- The selected generated hero visibly derives from the approved Rider source rendering.
- Source and candidate evidence are retained together with approval.
- Repeated authority copy cannot pass merely because it lives in locked static modules.
- The corrected branded proof contains no accidental repeated campaign or authority message.
- The earlier Phase 14 fixture remains labeled technical-only with known creative defects.

## Tests And Evidence

- Gallery contract tests covering stable codes, groups, labels, and incompatibilities.
- Snapshot or hash-bound rendered gallery evidence.
- Grounded request fixtures proving an environment image is attached and approved before generation.
- Negative tests for metadata-only grounding and unapproved source/candidate pairs.
- Static-copy collision fixtures covering exact and near-duplicate authority language.
- A corrected Rider wellness branded Composition Preview and Phase 14 render matrix.

## Non-Goals

- Automated proof of architectural or likeness fidelity.
- Silent editing of locked scaffold copy.
- Automatic creative approval.
- Full variant generation before branded-proof approval.
- Outlook, Gmail, or Apple Mail certification before the creative baseline is accepted.
