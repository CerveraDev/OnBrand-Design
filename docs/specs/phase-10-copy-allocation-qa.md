# Phase 10: Copy Allocation And Deduplication QA

**Status:** Approved specification, not implemented
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

## Anticipated Data And Contracts

- `content_units`: ID, text, source, owner slot, max occurrence, and approved refrain flag.
- `slot_allocation`: module ID, slot name, content unit ID, and rendering type.
- `dedupe_exemptions`: reason, scope, and evidence for allowed repetition.
- QA report section for copy occurrences and repeated visible strings.

## Workflow

1. Break supplied copy into atomic content units.
2. Map each content unit to one editable slot or approved static block.
3. Mark intentional refrains before rendering.
4. Render the representative variant.
5. Extract visible text while normalizing responsive fallback duplicates.
6. Compare occurrences against the allocation plan.
7. Block release builds on unexplained repetition.

## Acceptance Criteria

- Supplied body copy appears in planned slots only.
- Empty or irrelevant scaffold slots are removed, replaced with approved non-campaign content, or omitted by module selection rather than filled with duplicates.
- Static blocks cannot appear more than once.
- QA reports repeated campaign copy with source module and slot context.

## Tests And Evidence Required

- Unit tests for content-unit occurrence counting.
- Fixtures for allowed desktop/mobile duplication.
- Fixtures for forbidden repeated campaign phrases.
- Copy allocation plan snapshots for representative campaigns.

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
