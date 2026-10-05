# Modules

The canonical scaffold contains 102 top-level Beefree rows, 15 ordinary module boundaries, and four nested static-block boundaries. Marker rows are authoring documentation only:

- START marker rows use `#55ebb9`.
- END marker rows use `#ff81fb`.
- Static-block START marker rows use `#ffd675`.
- Static-block END marker rows use `#75edff`.
- Marker text color `#393d47` is not part of the production palette.
- Generated emails must exclude marker rows.

Use structured HTML parsing for runtime extraction. Do not split the scaffold with regular expressions.

## Composition Contract

1. Load `templates/scaffold/rider-scaffolding.canonical.html`.
2. Preserve the full document head, linked fonts, global CSS, Outlook/VML conditionals, outer wrapper, responsive behavior, row classes, and table structures.
3. Parse top-level Beefree row tables by their `row row-N` classes.
4. Validate marker pairing before composition.
5. Compose selected content rows only; never include the paired marker rows.
6. Preserve row 1 because it contains shared custom CSS used by generated documents.
7. Preserve original row classes rather than renumbering rows.
8. Use scaffold footer modules for footer variants; do not rebuild legal or footer markup from memory.

## Module Inventory

| Module | Marker rows | Content rows | Notes |
|---|---:|---:|---|
| Two-column header | 2-4 | 3 | Header/logo and live heading structure. |
| AI generated image based on prompt | 5-7 | 6 | Single-image visual slot for approved generated imagery. |
| Body - masonry layout | 8-12 | 9-11 | Multi-image body layout. |
| One-column header dark | 13-15 | 14 | Standalone dark header; select only with a hero that does not include a header. |
| Hero - live text heading - dark framed layout | 16-18 | 17 | Dark framed hero without a built-in header. |
| Body - light then dark layout | 19-27 | 20-26 | Editorial body sequence that transitions from light to dark. |
| Invite - two-column header - collaboration | 28-31 | 29-30 | Standalone invitation header with collaboration framing. |
| Invite - dark body | 32-36 | 33-35 | Dark invitation body with CTA. |
| Header & hero - live text heading - full-width | 37-39 | 38 | Full-width hero that includes its own Rider header/logo. |
| One-column header light | 40-42 | 41 | Standalone light header; select only with a hero that does not include a header. |
| Hero - live text heading - light layout - framed | 43-45 | 44 | Light framed hero without a built-in header. |
| Body - dark then light layout | 46-72 | 47-52, 56, 60-61, 68-71 | Extended body sequence; nested static rows are selected separately. |
| Static block 1 | 53-55 | 54 | Locked creator/Own Better brand message. |
| Static block 2 | 57-59 | 58 | Locked curated-design brand message. |
| Static block 3 | 62-64 | 63 | Locked furnished-residence availability and price message. |
| Static block 4 | 65-67 | 66 | Locked opportunity message. |
| Branded footer | 73-82 | 74-81 | Rider footer with project contact, legal, and developer branding. |
| Outside-broker customizable footer | 83-92 | 84-91 | Rider/legal footer with customizable outside-broker placeholder area. |
| In-house agent footer | 93-102 | 94-101 | Rider/legal footer populated from an in-house agent record. |

## Required Module Rules

Every Rider email must include:

- At least one hero module appropriate to the campaign.
- One footer module: branded, outside-broker customizable, or in-house agent.

A standalone header is optional. Do not automatically prepend one. A hero with `includes_header: true` in `rider-scaffolding.module-metadata.json` cannot be combined with a standalone header.

Every static block requires an explicit include/exclude decision. Included static blocks must be listed exactly once in the ordered campaign modules and have no editable slots. Their placement is determined by their position in that list, not by their original nesting inside the scaffold body.

For in-house agent variants, populate the agent area from `data/agents/index.json` and one JSON record per active agent. Resolve each headshot by canonical manifest `dropbox_id` and enforce the agent-footer approval and folder boundary.

For outside-broker variants, expose customization fields for headshot, name, title, phone, and email. Keep Rider project branding, developer/legal content, Equal Housing Opportunity marks, and footer legal copy intact.

## Phase 16 Staged Calibration

The corrected 94-row scaffold, refined metadata, and deterministic slot map are staged beside the current canonical runtime:

- `templates/scaffold/rider-scaffolding.phase16-intake.html`
- `templates/scaffold/rider-scaffolding.phase16-block-metadata.json`
- `templates/scaffold/rider-scaffolding.phase16-slot-map.json`

The shared parser and composition planner can load these files using stable metadata IDs and codes. Optional annotated blocks are removed when omitted; required slots fail before rendering; repeating lists use typed arrays; and compatibility rules enforce campaign type, sequence, and exclusion groups.

Do not treat these staged files as the production source until the Phase 16 galleries and branded proof receive owner approval and the canonical paths are deliberately promoted.
