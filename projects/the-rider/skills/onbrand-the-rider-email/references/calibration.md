# Calibration From Supplied HTML

The supplied Beefree scaffold has been calibrated.

## Current Source Truth

- Immutable source copy: `templates/scaffold/rider-scaffolding.source.html`
- Runtime canonical copy: `templates/scaffold/rider-scaffolding.canonical.html`
- Top-level rows: 102
- Catalog entries: 19, consisting of 15 ordinary modules and four nested static blocks
- Module markers: `#55ebb9` start and `#ff81fb` end
- Static-block markers: `#ffd675` start and `#75edff` end
- Runtime typo corrections: `REQUEST MORE INFORMATION` and `ARTS`
- Former unbranded footer terminology: outside-broker customizable footer
- Previous supplied source: `templates/scaffold/provenance/rider-scaffolding.source.legacy-2026-09-30.html`

## Current Extracted References

The current calibration updates:

- `brand.md`
- `email-design-system.md`
- `beefree-html-structure.md`
- `html-email.md`
- `modules.md`
- `footers.md`
- `qa.md`

## Future Recalibration

When a new approved Beefree scaffold is supplied:

1. Preserve the old source and canonical files or archive them with versioned names.
2. Save the new source copy without modification.
3. Create a corrected canonical runtime copy.
4. Re-run scaffold parsing and marker-pair validation.
5. Re-count production colors and typography usage.
6. Update module inventory, footer boundaries, and tests together.

Do not overwrite provenance files casually, and do not claim full HTML generation or campaign packaging unless the runtime assembler and package output have been implemented and verified.
