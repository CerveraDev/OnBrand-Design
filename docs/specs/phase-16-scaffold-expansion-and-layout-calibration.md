# Phase 16: Scaffold Expansion And Layout Calibration

**Status:** Galleries generated from refined runtime rules; owner sequence selection and branded proof pending

**Target:** A larger, better-labeled Rider block corpus whose layout intent can be selected and assembled predictably

**Depends on:** Phases 2, 8, 10, 14, and 15

## Why This Phase Exists

The corrected CFG-05 Rider wellness proof is a substantial improvement over the earlier smoke test, but it is not the final creative baseline. Owner review found that the remaining refinement is primarily about how blocks are selected, ordered, and combined. The current metadata proves technical compatibility, but it does not yet capture enough editorial layout intent to prevent every awkward composition.

The owner will revise the Rider scaffold with additional notes, marker conventions, and more reusable HTML blocks. Those annotations are the authoritative next input for layout calibration.

## Intake Contract

When the revised scaffold arrives:

1. Preserve the supplied file byte-for-byte as a new source artifact.
2. Keep the current scaffold and Phase 15 proof as historical provenance.
3. Inventory every marker color, marker label, block boundary, nested block, and footer boundary.
4. Separate instructions encoded by the owner from ordinary email copy.
5. Ask only about markers whose intended behavior remains ambiguous after inspection.
6. Do not promote the new scaffold to canonical until parsing, boundary, and regression tests pass.

## Block Metadata

Each block must receive:

- Stable project-specific code and human-readable label
- Block family and layout role
- Compatible predecessors and successors
- Header/hero inclusion behavior
- Required and optional content
- Editable slots and locked content
- Image count, aspect ratio, crop, and grounding requirements
- Static-content and copy-collision behavior
- Recommended campaign use cases
- Mobile stacking and Outlook fallback expectations
- Source row boundaries and provenance

## Layout Decisions

Composition Preview must eventually distinguish:

- Technical compatibility: the blocks can be assembled safely
- Content compatibility: the required copy and images fit the block
- Editorial compatibility: the sequence has a coherent narrative role
- Visual compatibility: density, color transitions, alignment, and image rhythm work together

The first three can be increasingly deterministic. Final visual quality remains human-approved.

## Deliverables

- Versioned source and canonical scaffold files
- Updated marker parser rules and boundary tests
- Expanded module metadata and slot map
- Updated static-block and locked-copy inventory
- Regenerated module catalog and labeled preview gallery
- Updated compatible header/hero and body-sequence options
- At least one corrected branded Composition Preview
- Browser render evidence for desktop and mobile
- Updated limitations, audit log, status, roadmap, and changelog

## Acceptance Criteria

- Every owner annotation has a documented interpretation or an explicit unresolved question.
- Every added block is represented in metadata and isolated preview evidence.
- The runtime rejects unsupported or contradictory block sequences.
- No marker rows leak into final email HTML.
- Selected blocks do not duplicate headers, heroes, authority statements, campaign copy, or incompatible CTAs unintentionally.
- The owner approves the assembled block sequence before it becomes the new creative baseline.
- Existing Phase 15 fixtures remain reproducible or are intentionally versioned as superseded evidence.

## Pending Input

- Owner confirmation of any remaining semantic questions discovered during block classification
- Any additional rules about blocks that must, may, or must not appear together beyond the annotations already supplied

## Intake Evidence

The 2026-10-04 scaffold submission is preserved and its corrected working copy passes exact label and color pairing for all 34 marker pairs. See [Phase 16 Rider scaffold intake](../evals/phase-16-rider-scaffold-intake.md).

## Parser And Metadata Checkpoint

The structured parser now separates 20 row-level modules from 14 inline annotations, preserves parent-module and parent-annotation relationships, and recognizes the amplification field nested inside the amplified-list field. A marker-removal path deletes row-level and inline authoring markers without deleting their content rows.

The checksum-bound Phase 16 metadata assigns stable IDs and codes, source occurrences, module families, layout roles, theme rules, header behavior, content and image requirements, campaign use, compatibility, and client behavior. Annotation metadata defines editable value type, optionality, repetition, generation policy, constraints, and placeholder handling. See [Phase 16 parser and metadata evidence](../evals/phase-16-parser-and-metadata.md).

The Phase 16 slot map converts those annotations into required, optional-removable, default-preserving, image, text-list, and amplified-list inputs. Runtime composition now enforces stable codes, compatible campaign types, predecessor/successor rules, exclusion groups, at-most-one static message, invite paths that do not require a hero, and filtered header/hero configurations. See [Phase 16 slots and composition evidence](../evals/phase-16-slots-and-composition.md).

## Visual Gallery Checkpoint

The staged scaffold now generates 18 isolated module previews, 14 compatible header/hero configurations, and eight complete runtime-valid sequences: six long-form and two invite options. The committed galleries have zero missing iframe targets and zero authoring-marker leaks. See [Phase 16 Rider layout gallery](../evals/phase-16-rider-layout-gallery.md).

The gallery is a selection aid, not approval. It uses scaffold sample content, does not perform the optional full light-body color conversion, and does not promote Phase 16 to the canonical runtime. The owner must select or revise one `SEQ-*` option before the new branded proof is assembled.

## Non-Goals

- Automatic approval of visual composition
- Replacing the owner’s scaffold design system with generated design options
- Generating the full internal variant matrix before the updated branded proof is approved
- Treating browser previews as Gmail, Outlook, or Apple Mail certification
