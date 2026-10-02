# HTML Email Assembly

## Default Assembly

1. Load the canonical scaffold.
2. Validate row continuity and the 13 marker pairs.
3. Select module content row ranges from [modules.md](modules.md).
4. Preserve the full document head, global CSS, linked fonts, Outlook/VML conditionals, wrapper tables, row classes, and inline styles.
5. Remove marker rows from generated outputs.
6. Populate campaign copy, CTA text, and approved images inside existing scaffold structures.
7. Populate the selected footer variant.
8. Copy every local image used by any variant into the package `images/` directory.
9. Make package-preview HTML reference copied files with portable relative paths such as `../images/hero.jpg`.
10. Record deployment URLs or externally managed assets in the asset manifest.
11. Run QA.

## Footer Assembly

Use scaffold footer modules:

- Branded: rows 62-69.
- Outside-broker customizable: rows 72-79.
- In-house agent: rows 82-89.

The outside-broker customizable footer has a broker personalization area. It is not a branding-free footer.

For in-house variants, load active records from `data/agents/index.json` in `output_order`. Each record must pass `data/agents/agent.schema.json`.

## Output Naming

Use clear variant labels:

- `branded`
- `outside-broker-customizable`
- agent ID, such as `jake-lecce`

Avoid ambiguous labels such as `unbranded`.

## Portability

Do not leave absolute local filesystem paths, temporary paths, or links into the Rider source corpus in delivered HTML. Keep one packaged copy of a shared image even when several HTML variants use it. Do not duplicate or re-encode an image unless the final designs genuinely require different files.

Relative paths make packaged files locally previewable but are not final production hosting URLs. When the deployment platform requires public image URLs, preserve or produce a deployment-ready HTML set only when those URLs are available, and document the mapping in the manifest rather than inventing URLs.
