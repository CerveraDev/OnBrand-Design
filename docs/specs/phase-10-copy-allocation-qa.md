# Phase 10: Copy Allocation And Deduplication QA

**Status:** Implemented for The Rider, 2026-10-03
**Target:** 0.8.0
**Depends on:** Phases 5 and 8

## Goal

Assign every approved copy unit to exactly one owner slot and detect unintended visible repetition before final rendering.

## Non-Goals

- Do not block legitimate responsive fallback markup that duplicates the same visible content for desktop and mobile.
- Do not rewrite legal, footer, or locked static content merely to reduce repetition.
- Do not forbid explicitly approved refrains.

## Requirements

- COPY-ALLOC-001: Produce a content allocation plan before rendering.
- COPY-ALLOC-002: Every campaign copy unit has one owner slot by default.
- COPY-ALLOC-003: Default maximum visible occurrence is 1 for every campaign copy unit.
- COPY-ALLOC-004: Do not duplicate copy to fill extra scaffold slots.
- COPY-ALLOC-005: Static blocks appear at most once.
- COPY-ALLOC-006: QA detects repeated visible campaign copy across modules.
- COPY-ALLOC-007: QA permits known desktop/mobile fallback duplication, footer/legal language, locked static content, and explicitly approved refrains.
- COPY-ALLOC-008: The wellness smoke repetition of "From the creators..." and "Same routine..." is the reference failure case.

## Implemented Data And Contracts

- Required `copy_allocation` version `1.0`: plan ID, approved status, approver/date, and nonempty `content_units`.
- `content_units`: stable ID, exact approved text, source, role, approval status, one channel/owner, reuse policy, maximum occurrence, claim policy, and optional evidence references.
- Channels: `live-html`, `alt-text`, `metadata`, `baked-image-text`, and explicit protected `static`, `legal`, or `footer` declarations.
- Optional `slot_allocation`: module ID, slot name, content unit ID, and rendering type; entries must agree with the authoritative unit owner.
- `restricted_phrases`: stable ID, normalized phrase, reason, and occurrence cap; caps above one require explicit exemption approval.
- `dedupe_exemptions`: ID, reason, narrow scope, named targets, approver/date, and optional evidence. Refrain, required name, metadata, static, footer, and legal policies require explicit records. Occurrence caps always apply.
- Baked-image text requires the matching `image_workflow_id`, workflow `text_policy: "baked-approved"`, and `declared_text_source: "ocr"` or `"creator-declared"`. Every baked-approved workflow must declare its actual copy.
- Claims marked `requires-evidence` fail without `claim_references`. References are retained for human review; factual verification and claim extraction remain external.
- Successful `campaign-metadata.json` and `qa-report.json` retain approved units, owner/source context, claim references, exemption approvals, counts, similarity findings, and thresholds.

The [runtime schema](../../tools/rider_campaign_runtime/campaign.schema.json) and [authoring reference](../../projects/the-rider/skills/onbrand-the-rider-email/references/copy-allocation.md) define the portable JSON/CLI workflow. Codex, shell, and Claude Code callers share this contract; tested Claude Code adapters remain Phase 11 work.

## Workflow

1. Break supplied copy into atomic content units.
2. Map each content unit to one editable slot or approved static block.
3. Mark intentional refrains before rendering.
4. Validate exact owner text, coverage, optional slot links, declared image text, and evidence policy before asset download or rendering.
5. Normalize the logical slot corpus for cross-surface repetition. Responsive fallback HTML branches share one logical owner and do not count twice.
6. Compare occurrences and restricted phrases with approved caps, then report transparent near-duplicate pairs.
7. Block every build mode on failed checks. Present proposed revisions for approval; never silently rewrite approved user copy. Failures leave the last passing package intact.

## Similarity Policy

Normalize HTML to text, lowercase, punctuation/dash/whitespace variants, and remove URLs. Exact normalized matches and bounded restricted phrase counts are deterministic release gates. For pairs of at least four words each, compute `max(token-set Jaccard, (word-bigram Jaccard + character-4-gram Jaccard) / 2)`; character grams omit spaces. Scores >= 0.65 are review signals; >= 0.82 block without an exemption naming both units or their exact pair. These initial thresholds are transparent and test-backed, not calibrated semantic equivalence scores.

## Acceptance Criteria

- Supplied body copy appears in planned slots only.
- Empty or irrelevant scaffold slots are removed, replaced with approved non-campaign content, or omitted by module selection rather than filled with duplicates.
- Static blocks cannot appear more than once.
- QA reports repeated campaign copy with source module and slot context.

## Tests And Evidence

- [Allocation tests](../../tests/test_rider_copy_allocation.py) cover clean plans; exact/normalized and near-duplicate failures; live/baked/alt/metadata overlap; known wellness and authority repetition; refrains; static/legal/footer/required-name exemptions; capped reuse; unsupported/supported claims; stale, unknown, ambiguous and missing owners; stale slot links; missing baked declarations; warning scores; and unchanged approved text.
- Runtime and grounded-image regression tests preserve Phase 7-9 modes, composition, source provenance, locked blocks, responsive branches, and staging/package behavior.
- All four Rider runtime fixtures carry allocation plans. Wellness fixture copy removes the old repeated campaign pattern; negative tests retain that failure case. These are internal non-production examples, not changes to a user's approved campaign.
- Composition Preview pilot and package integrity evidence are recorded in [AUDIT_LOG.md](../../AUDIT_LOG.md), entry AUD-055.

## Dependencies

- Composition plan.
- Slot map.
- HTML text extraction and QA reporting.

## Risks

- HTML email fallback structures may be difficult to distinguish from true repetition.
- Short phrases such as CTA labels may need carefully scoped exemptions.
- Overly aggressive dedupe checks could block intentional campaign rhythm.

## Out Of Scope

- Automated copywriting.
- Legal/footer copy editing.
- Translation/localization.
- Automated OCR, semantic claim extraction, reference retrieval, and factual/legal approval.
- Exhaustive repetition extraction from undeclared bitmap text or all locked scaffold/variant contact strings. Protected declarations are validated against locked sources; existing static/footer contracts remain authoritative.
