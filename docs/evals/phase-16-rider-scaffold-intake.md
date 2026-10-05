# Phase 16 Rider Scaffold Intake

**Date:** 2026-10-04

**Status:** Latest source preserved, conditional row annotations validated, and canonical promotion pending

## Artifacts

- Latest immutable submitted source: `projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/provenance/rider-scaffolding.source.phase16-2026-10-05.html`
- Prior immutable submitted source: `projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/provenance/rider-scaffolding.source.phase16-2026-10-04.html`
- Corrected intake copy: `projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.phase16-intake.html`
- Latest submitted source SHA-256: `58eb10e777c9af840e2a6fd37ffa13b2de76c59a5b5dd9ea39759e7619ee4e45`
- Corrected intake SHA-256: `4125169e6079965a596f71636c0cb4df3aa336eaf5c101e83a24a73dd4351439`

The latest immutable source hash matches the supplied attachment exactly. The prior source remains preserved as historical provenance.

## Corrections

The corrected intake copy makes only guarded annotation corrections:

1. `END - MAGE BLOCK...` becomes `END - IMAGE BLOCK...`.
2. The pink image-block marker between copy blocks changes from `START` to `END`.
3. `END - LISTS THAT HAS...` becomes `END - LIST THAT HAS...`.
4. The bulleted-list end label receives the same final period as its start label.
5. `AOTHER IMAGE BLOCK...` becomes `ANOTHER IMAGE BLOCK...` at the start.
6. The pink second `AOTHER` marker becomes `END - ANOTHER IMAGE BLOCK...`.
7. `END - FOOTNOTE-` becomes `END - FOOTNOTE -`.
8. Matching `PRECEEDING` text is corrected to `PRECEDING` in both footnote markers.
9. `UNBRANDED FOOTER` becomes `OUTSIDE-BROKER CUSTOMIZABLE FOOTER` at both boundaries.

No campaign content, CSS, layout markup, images, footer content, or legal copy was intentionally changed in the corrected intake copy. The CSS and layout changes made by the owner in the latest submitted source are retained.

## Validation

- Parsed HTML rows: 102
- Start markers: 37
- End markers: 37
- Exact marker pairs: 37
- Unique marker labels: 36
- Label pairing: passed
- Marker-color pairing: passed
- Outside-broker footer pair: passed

The difference between 37 pairs and 36 unique labels is intentional: two conditional list rows share one human annotation. The refined metadata distinguishes them by source occurrence and assigns stable IDs.

The latest source adds four nested row-level conditions inside the long-form body: a leading-term list row, a paragraph-style list-payoff row, an amplified-list row, and a list-style follow-up payoff row. These are content containers, not independently selectable email modules. A container is removed as a complete table row when its owning slot has no approved content.

## Parser Boundary

The shared scaffold parser preserves top-level and nested static module extraction and adds a separate marker-element pass for granular inline and nested annotations. It resolves 20 modules and 17 annotations from the corrected intake, including four conditional row containers, five nested relationships, the nested amplification field, and the standalone second image block.

The corrected intake file still must not replace `rider-scaffolding.canonical.html` until slot-map, composition, preview, proof, and remaining regression work is complete. See [Phase 16 parser and metadata evidence](phase-16-parser-and-metadata.md).
