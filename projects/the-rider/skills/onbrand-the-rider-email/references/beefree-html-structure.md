# Beefree HTML Structure

Use `templates/scaffold/rider-scaffolding.canonical.html` as the canonical Rider compatibility reference.

## Required Preservation

Generated Rider emails must preserve:

- `<!DOCTYPE html>` and root attributes.
- Head metadata.
- Google font links.
- Global CSS and mobile overrides.
- Outlook/VML conditional blocks.
- Outer wrapper tables.
- Beefree `row row-N`, `row-content`, `column`, and `block-N` classes.
- Inline styles on scaffold elements.
- Spacer, divider, image, paragraph, heading, list, and button block structures.

Do not reimplement modules in a separate handcrafted HTML system.

## Row Model

Top-level modules are row-table ranges. A row table is identified by class tokens `row` and `row-N`.

Marker rows use colored backgrounds and text labels to define module boundaries. They are part of the authoring scaffold only and must be removed from generated output.

Runtime extraction must use structured HTML parsing. Regular-expression splitting is not acceptable for production row extraction because it risks breaking nested tables, Outlook conditionals, and Beefree class structure.

## Source Files

- `templates/scaffold/rider-scaffolding.source.html`: immutable provenance copy of the supplied Beefree export.
- `templates/scaffold/rider-scaffolding.canonical.html`: runtime source with typo corrections and outside-broker marker terminology.

The Desktop source file supplied by the user is not modified.
