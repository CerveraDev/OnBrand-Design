# Brand

This file is calibrated from `templates/scaffold/rider-scaffolding.canonical.html`.

## Brand Boundary

This skill is only for Rider Residences. Do not create generic real estate language when a Rider-specific direction is possible.

Use copy that feels polished, confident, warm, premium, architectural, and clear. Avoid generic luxury cliches, unsupported claims, invented contact details, invented URLs, invented amenities, invented pricing, invented availability, and invented deadlines.

## Production Color Palette

Color counts below come from inline production row styles in the canonical scaffold, excluding authoring marker rows.

| Color | Count | Role |
|---|---:|---|
| `#000000` | 156 | Primary black for body text, dark module backgrounds, button fills, button borders, and wrapper text defaults. |
| `#ffffff` | 102 | Primary white for contrast text, light module backgrounds, button fills, and button borders. |
| `#dddddd` | 6 | Light divider rule used in body and footer sections. |
| `#636565` | 3 | Footer legal text color. |
| `#999999` | 2 | Muted informational text/divider utility in the invite module. |
| `#6b6b6b` | 1 | Muted divider utility in the invite header. |
| `#f7f7f7` | 1 | Light neutral row background utility. |

Do not treat authoring marker colors as brand colors:

- `#55ebb9` marks START rows only.
- `#ff81fb` marks END rows only.
- `#393d47` is marker text color only.

## Typography

Linked fonts in the scaffold head:

- `GFS Didot`
- `Droid Serif`
- `Playfair Display`
- `Cormorant Upright`

Observed `font-family` usage in markup and CSS:

| Stack | Count | Role |
|---|---:|---|
| `'Helvetica Neue', Helvetica, Arial, sans-serif` | 99 | Primary body, CTA, footer, legal, and large sans display stack. |
| `'GFS Didot','Times New Roman','Playfair Display','Droid Serif'` | 6 | Serif display stack for artful positioning and footer display language. |
| `sans-serif` | 6 | Outlook/VML fallback center text. |
| `'Cormorant Upright','Playfair Display'` | 1 | Decorative/live display accent. |
| `'Playfair Display', Georgia, serif` | 1 | Serif display fallback stack. |

`GFS Didot`, `Playfair Display`, and `Cormorant Upright` are linked and used in the scaffold. `Droid Serif` is linked and appears as a fallback in the `GFS Didot` display stack; do not treat it as an active primary face.

## Email-Client Fallback Behavior

Google font links are inside the non-MSO conditional block. Outlook clients that ignore those imports fall back to the local/system fonts in each stack:

- Serif display copy falls back through `Times New Roman`, `Playfair Display`, `Droid Serif`, `Georgia`, and generic `serif` depending on the stack.
- Body and CTA copy fall back through `Helvetica`, `Arial`, and generic `sans-serif`.
- VML button text uses a simple `sans-serif` fallback.
