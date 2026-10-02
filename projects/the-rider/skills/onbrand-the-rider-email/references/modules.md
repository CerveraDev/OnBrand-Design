# Modules

The canonical scaffold contains 90 top-level Beefree rows and 13 valid module boundaries. Marker rows are authoring documentation only:

- START marker rows use `#55ebb9`.
- END marker rows use `#ff81fb`.
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
| Hero - dark framed layout | 13-16 | 14-15 | Dark framed hero with image and display heading. |
| Body - light then dark layout | 17-25 | 18-24 | Editorial body sequence that transitions from light to dark. |
| Invite - two-column header - collaboration | 26-29 | 27-28 | Invitation header variant with collaboration framing. |
| Invite - dark body | 30-34 | 31-33 | Dark invitation body with CTA. |
| Hero - full-width with live text heading and logo | 35-37 | 36 | Full-width hero using live text and logo. |
| Hero - light layout - framed | 38-41 | 39-40 | Light framed hero variant. |
| Body - dark then light layout | 42-60 | 43-59 | Extended body sequence with dark-to-light transition and CTAs. |
| Branded footer | 61-70 | 62-69 | Rider footer with project contact, legal, and developer branding. |
| Outside-broker customizable footer | 71-80 | 72-79 | Rider/legal footer with customizable outside-broker placeholder area. |
| In-house agent footer | 81-90 | 82-89 | Rider/legal footer populated from an in-house agent record. |

## Required Module Rules

Every Rider email must include:

- At least one hero/header module appropriate to the campaign.
- One footer module: branded, outside-broker customizable, or in-house agent.

For in-house agent variants, populate the agent area from `data/agents/index.json` and one JSON record per active agent. The active roster contains six user-verified records. Resolve each headshot by canonical manifest `dropbox_id` and enforce the agent-footer approval and folder boundary.

For outside-broker variants, expose customization fields for headshot, name, title, phone, and email. Keep Rider project branding, developer/legal content, Equal Housing Opportunity marks, and footer legal copy intact.
