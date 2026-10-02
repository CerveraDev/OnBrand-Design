# HTML Email Assembly

## Default Assembly

1. Validate the campaign document against `tools/rider_campaign_runtime/campaign.schema.json`.
2. Load the canonical scaffold and its `rider-scaffolding.slot-map.json` sidecar.
3. Validate row continuity and the 13 marker pairs.
4. Select module content row ranges from [modules.md](modules.md).
5. Preserve the full document head, global CSS, linked fonts, Outlook/VML conditionals, wrapper tables, row classes, and inline styles.
6. Remove marker rows from generated outputs.
7. Populate only declared typed slots; every anchor must resolve exactly as defined or the build fails.
8. Populate the selected footer variant.
9. Copy every image used by any variant into the package `images/` directory.
10. Make package-preview HTML reference copied files with portable relative paths such as `../images/hero.jpg`.
11. Record source identity, checksum, role, and variant usage in the asset manifest.
12. Run blocking QA and create the ZIP only after it passes.

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

Run the implementation with `python3 -m tools.rider_campaign_runtime.cli <campaign.json>` from the repository root.
