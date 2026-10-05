# Phase 16 Rider Scaffold Intake

**Date:** 2026-10-04

**Status:** Source preserved and marker corrections validated; canonical promotion pending

## Artifacts

- Immutable submitted source: `projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/provenance/rider-scaffolding.source.phase16-2026-10-04.html`
- Corrected intake copy: `projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.phase16-intake.html`
- Submitted source SHA-256: `51150d774fa12caed409f7f9295c1a6b1d87e7fcd22340dbdd108367b0414748`
- Corrected intake SHA-256: `ff0f570999921f07b6eb47cc97d4dafd5239f1b10c7620be252b46542955fc28`

The immutable source hash matches the supplied attachment exactly.

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

No campaign content, CSS, layout markup, images, footer content, or legal copy was intentionally changed.

## Validation

- Parsed HTML rows: 94
- Start markers: 34
- End markers: 34
- Exact marker pairs: 34
- Unique marker labels: 33
- Label pairing: passed
- Marker-color pairing: passed
- Outside-broker footer pair: passed

The difference between 34 pairs and 33 unique labels is intentional: two static blocks share the same human annotation. The refined metadata distinguishes them by source occurrence and assigns stable IDs and codes.

## Parser Boundary

The shared scaffold parser now preserves top-level module extraction and adds a separate marker-element pass for granular inline and nested annotations. It resolves 20 modules and 14 annotations from the corrected intake, including the nested amplification field and the standalone second image block.

The corrected intake file still must not replace `rider-scaffolding.canonical.html` until slot-map, composition, preview, proof, and remaining regression work is complete. See [Phase 16 parser and metadata evidence](phase-16-parser-and-metadata.md).
