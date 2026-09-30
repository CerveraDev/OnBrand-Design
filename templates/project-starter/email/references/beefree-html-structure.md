# Beefree HTML Structure

Use Beefree as the structural benchmark for cross-compatible HTML email output.

## Provisional Compatibility Rules

Prefer:

- Table-based layout
- Inline CSS
- Presentation tables
- Explicit image dimensions where appropriate
- Stable spacer rows
- Conservative responsive patterns
- Outlook-safe structure
- Flattened images for complex overlays

Avoid:

- Fragile live overlays unless the structure is proven safe
- Complex CSS positioning
- Unsupported CSS that breaks common email clients
- Depending on external stylesheets
- Rebuilding locked Beefree-generated footers from memory

## Calibration Required

When the user provides the Beefree-generated __PROJECT_NAME__ sample, compare this provisional guidance against the real HTML and update this file with observed patterns:

- Wrapper tables
- Row and column structure
- Mobile classes
- Spacer technique
- Button markup
- Image block markup
- Conditional Outlook code
- Footer attachment point
