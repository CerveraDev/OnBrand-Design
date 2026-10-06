# HTML Email Assembly

## Default Assembly

1. Validate the campaign document against `tools/rider_campaign_runtime/campaign.schema.json`.
2. Load the canonical scaffold and its `rider-scaffolding.slot-map.json` sidecar.
3. Validate row continuity and the 13 marker pairs.
4. Select module content row ranges from [modules.md](modules.md).
5. Preserve the full document head, global CSS, linked fonts, Outlook/VML conditionals, wrapper tables, row classes, and inline styles.
6. Remove marker rows from generated outputs.
7. Populate only declared typed slots; every anchor must resolve exactly as defined or the build fails.
8. Validate the approved composition plan for Composition Preview and Release Build, including stable module codes, static-block decisions, and header/hero compatibility.
9. For every non-repeating cover-style table background, retain the ordinary CSS declaration, add the legacy table `background` attribute, and wrap the table's content cell in an Outlook-only VML `v:rect`/`v:fill`/`v:textbox` fallback. The runtime performs this transform; do not hand-maintain duplicate markup in the scaffold.
10. Resolve the effective variant set from the explicit build mode and populate only those selected footer variants.
11. Copy every image used by any variant into the package `images/` directory.
12. Make package-preview HTML reference copied files with portable relative paths such as `../images/hero.jpg`.
13. Record source identity, checksum, role, and variant usage in the asset manifest.
14. Run blocking QA and create the ZIP only after it passes.

## Footer Assembly

Use scaffold footer modules:

- Branded: rows 62-69.
- Outside-broker customizable: rows 72-79.
- In-house agent: rows 82-89.

The outside-broker customizable footer has a broker personalization area. It is not a branding-free footer.

For in-house variants, load active records from `data/agents/index.json` in `output_order`. Each record must pass `data/agents/agent.schema.json`.

## Build Modes

Use `build.mode` to distinguish output intent:

- `composition-preview`: one representative Design Proof for user review.
- `smoke-test`: one representative technical validation variant unless `variant_policy` explicitly expands it.
- `release-build`: full internal matrix.

The default representative is `branded`. `representative_variant` may also be `outside-broker-customizable` or `agent-<agent-id>`. Use `variant_policy: "changed-surface-expanded"` with a non-empty `changed_surfaces` array when agent roster/data, footer renderer/data, footer asset resolution, or scaffold footer structure changes require full smoke coverage.

## Composition Approval

Use `python3 -m tools.rider_campaign_runtime.cli catalog --output <review-folder>` to produce `module_catalog.json`, `composition-review.md`, and isolated HTML snippets. Stable codes include standalone headers (`H-01`), non-header heroes (`HR-01`), header-bearing heroes (`HH-01`), AI image modules (`AI-01`), bodies (`B-01`), and static blocks (`S-01`).

Use `python3 -m tools.rider_campaign_runtime.cli plan --selection <selection.json> --output <composition-plan.json>` after the user approves exact codes. The plan must be embedded in Composition Preview and Release Build campaign specs.

## Output Naming

Use clear variant labels:

- `branded`
- `outside-broker-customizable`
- agent ID, such as `jake-lecce`

Avoid ambiguous labels such as `unbranded`.

## Portability

Do not leave absolute local filesystem paths, temporary paths, or links into the Rider source corpus in delivered HTML. Keep one packaged copy of a shared image even when several HTML variants use it. Do not duplicate or re-encode an image unless the final designs genuinely require different files.

Relative paths make packaged files locally previewable but are not final production hosting URLs. When the deployment platform requires public image URLs, preserve or produce a deployment-ready HTML set only when those URLs are available, and document the mapping in the manifest rather than inventing URLs.

For native MIME tests, foreground `<img>` files may use CID references. CSS, legacy-attribute, and VML background references must all resolve to the same public HTTPS source from `asset-manifest.json`; never convert those background references to CID.

Run the implementation with `python3 -m tools.rider_campaign_runtime.cli <campaign.json>` from the repository root.
