# Rider Campaign Runtime

This standard-library Python runtime turns a validated Rider campaign JSON file into a portable review package.

## Run

From the repository root:

```bash
python3 -m tools.rider_campaign_runtime.cli path/to/campaign.json
```

Use `campaign.schema.json` as the machine-readable input contract and `projects/the-rider/skills/onbrand-the-rider-email/examples/smoke-campaign.runtime.json` as a non-production example. Repository-relative `tools/`, `projects/`, and `campaign-output/` paths resolve from the repository root.

Every campaign must declare a `build` object:

- `composition-preview` with `variant_policy: "single"` renders one representative Design Proof for user review.
- `smoke-test` with `variant_policy: "single"` renders one representative technical smoke variant.
- `smoke-test` with `variant_policy: "all"` renders every authorized variant for explicit broad validation.
- `smoke-test` with `variant_policy: "changed-surface-expanded"` renders every authorized variant when `changed_surfaces` names an agent/footer/scaffold-footer change.
- `release-build` with `variant_policy: "all"` renders the full internal matrix: branded, outside-broker customizable, and one variant per active in-house agent.

The default representative is `branded`. A caller can request `outside-broker-customizable` or `agent-<agent-id>` as `representative_variant` without enabling the full matrix.

Every campaign must explicitly decide every scaffold static block and list each included block exactly once in the ordered modules. Module metadata distinguishes standalone headers from heroes; a header-bearing hero cannot be combined with a standalone header.

## Output

On success the runtime writes:

```text
campaign-slug/
|-- html/
|-- images/
|-- documents/ (when selected)
|-- asset-manifest.json
|-- campaign-metadata.json
`-- qa-report.json
campaign-slug.zip
```

The ZIP is created only after blocking QA passes. `relative-review` mode packages image files and rewrites HTML to `../images/...`. `hosted-deployment` mode requires an explicit public asset base URL; the runtime never invents one.

Optional `documents` entries resolve exact manifest IDs, require PDF media approved for body use, and are copied into `documents/` with checksum provenance.

The canonical Rider scaffold remains immutable input. Content changes are constrained by the typed sidecar slot map, locked static blocks are verified before asset localization, and agent headshots must resolve by exact manifest identity with the required path and approval. Builds use a protected staging directory so an interrupted or failed download cannot replace the last passing package.

`campaign-metadata.json` and `qa-report.json` record the requested build mode, representative variant, effective variant scope, changed surfaces, expansion reason, and rendered variants.
