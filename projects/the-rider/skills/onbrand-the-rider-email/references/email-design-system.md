# Email Design System

This file is calibrated from the canonical Beefree scaffold.

## Structure

- The production canvas is a centered `600px` email width.
- Rows use Beefree `table class="row row-N"` wrappers and nested `row-content` tables.
- Modules use table-based columns, inline styles, spacer blocks, divider blocks, image blocks, heading blocks, paragraph blocks, and button blocks.
- Responsive behavior is defined in the document head and must travel with every generated document.

## Color System

The Rider email system is primarily black and white:

- `#000000`: primary text, dark backgrounds, dark CTA fills/borders.
- `#ffffff`: contrast text, light backgrounds, white CTA fills/borders.

Neutral utilities:

- `#dddddd`: divider rules.
- `#636565`: legal footer text.
- `#999999` and `#6b6b6b`: muted invite-module divider/text utilities.
- `#f7f7f7`: light neutral background utility.

Exclude marker-only colors from design decisions: `#55ebb9`, `#ff81fb`, and `#393d47`.

## Typography

- Use `'Helvetica Neue', Helvetica, Arial, sans-serif` for body copy, CTA text, agent data, legal text, and sans display settings.
- Use the scaffold serif display stacks only where the existing module uses them.
- Preserve linked font declarations. Do not add new web fonts unless the brand source changes.
- Do not claim `Droid Serif` as an active primary font; it is linked and appears as a fallback in the display stack.

## CTA Pattern

Observed CTA buttons use pill-shaped spans with `border-radius: 60px`, compact vertical padding, and uppercase copy. Button variants invert black and white:

- Dark CTA: black fill/border with white text.
- Light CTA: white fill/border with black text.
- Hover states are defined in the head CSS for selected rows and must be preserved.

## Layout Rhythm

Use the scaffold's existing row groups rather than inventing alternate layouts:

- Header/hero modules create campaign hierarchy.
- Body modules alternate image-rich, dark, light, and editorial sections.
- Footer modules carry fixed legal and branding responsibilities.

Spacing is defined by row-level `col-pad` rules, spacer blocks, and mobile overrides in the head. Preserve those dimensions unless a campaign-specific edit is explicitly requested and tested.

## Design Integrity

Do not create a new visual system for Rider emails. Compose, trim, and populate the canonical scaffold. Preserve:

- The full head and style blocks.
- Outlook/VML conditionals.
- Table structure.
- Original row classes.
- Linked fonts.
- Beefree image and button patterns.
- Footer legal content and marks.
