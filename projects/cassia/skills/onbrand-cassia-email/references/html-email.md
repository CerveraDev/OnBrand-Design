# HTML Email Assembly

This file is provisional until the sample Beefree HTML is supplied.

## Default Assembly

1. Build the body using approved Cassia modules.
2. Use Beefree-style table-based structure.
3. Keep CSS inline or otherwise compatible with the supplied template.
4. Insert finalized image URLs or placeholders as directed.
5. Append locked footer partials to create output variants.
6. Do not alter footer partials unless explicitly instructed.
7. Copy every local image used by any variant into the package `images/` directory.
8. Make package-preview HTML reference those copied files with portable relative paths such as `../images/hero.jpg`.
9. Record any deployment URLs or externally managed assets in the asset manifest.
10. Run QA.

## Footer Insertion

Footer insertion points must be calibrated from the supplied sample HTML and footer partials. Until then, treat footer attachment as a defined future integration point rather than guessing the exact markup boundary.

## Output Naming

Use clear variant labels:

- branded
- broker-neutral
- agent name or agent number

Avoid ambiguous labels such as "unbranded" in internal filenames when "broker-neutral" is more precise.

## Portability

Do not leave absolute local filesystem paths, temporary paths, or links into the Cassia source corpus in delivered HTML. Keep one packaged copy of a shared image even when several HTML variants use it. Do not duplicate or re-encode an image unless the final designs genuinely require different files.

Relative paths make the packaged files locally previewable but are not final production hosting URLs. When the deployment platform requires public image URLs, preserve or produce a deployment-ready HTML set only when those URLs are available, and document the mapping in the manifest rather than inventing URLs.
