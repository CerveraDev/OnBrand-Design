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

The difference between 34 pairs and 33 unique labels is intentional: two static blocks share the same human annotation. Phase 16 parser calibration must assign stable numbered IDs to repeated static labels.

## Parser Boundary

The existing runtime parser is not yet promoted to this scaffold. It was designed around row-level module markers, while the revised scaffold includes granular inline start/end annotations within content rows and nested annotations such as amplification inside a list. Phase 16 must add a separate nested-annotation pass while preserving top-level module extraction.

The corrected intake file must not replace `rider-scaffolding.canonical.html` until parser, metadata, slot-map, composition, and regression work is complete.
