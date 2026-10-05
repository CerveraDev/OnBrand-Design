# Rider Campaign Runtime

This standard-library Python runtime turns a validated Rider campaign JSON file into a portable review package.

## Run

From the repository root:

```bash
python3 -m tools.rider_campaign_runtime.cli path/to/campaign.json
```

Generate Composition Preview review artifacts:

```bash
python3 -m tools.rider_campaign_runtime.cli catalog --output path/to/review-folder
```

To review a staged scaffold without changing the canonical runtime, provide the complete sidecar trio:

```bash
python3 -m tools.rider_campaign_runtime.cli catalog \
  --output path/to/review-folder \
  --scaffold path/to/staged-scaffold.html \
  --slot-map path/to/staged-slot-map.json \
  --metadata path/to/staged-metadata.json
```

Refined staged scaffolds also produce `module-gallery.html`, `sequence-gallery.html`, and machine-readable sequence configurations. The three staged paths must be supplied together. The same flags are available to `plan` and `build`, so an approved staged selection can be converted and rendered without changing canonical defaults.

For a staged build, pass the complete trio with the campaign fixture:

```bash
python3 -m tools.rider_campaign_runtime.cli build path/to/campaign.json \
  --scaffold path/to/staged-scaffold.html \
  --slot-map path/to/staged-slot-map.json \
  --metadata path/to/staged-metadata.json
```

The runtime uses those files only for that invocation. Omitting the flags continues to use the canonical Rider scaffold and sidecars.

Create an approved composition plan from a user-approved selection:

```bash
python3 -m tools.rider_campaign_runtime.cli plan \
  --selection path/to/composition-selection.json \
  --output path/to/composition-plan.json
```

Use `campaign.schema.json` as the machine-readable input contract and `projects/the-rider/skills/onbrand-the-rider-email/examples/smoke-campaign.runtime.json` as a non-production example. Repository-relative `tools/`, `projects/`, and `campaign-output/` paths resolve from the repository root.

Validate The Rider manifest-source configuration:

```bash
python3 -m tools.asset_selection.manifest_source \
  --config projects/the-rider/manifest-source.json \
  --pretty
```

No stable public manifest URL is configured yet. The supported current path is the validated local-cache fallback in `tools/dropbox-manifest/manifest.json`; future public URL support belongs in `projects/the-rider/manifest-source.json`, not in credential files.

Every campaign must declare a `build` object:

- `composition-preview` with `variant_policy: "single"` renders one representative Design Proof for user review.
- `smoke-test` with `variant_policy: "single"` renders one representative technical smoke variant.
- `smoke-test` with `variant_policy: "all"` renders every authorized variant for explicit broad validation.
- `smoke-test` with `variant_policy: "changed-surface-expanded"` renders every authorized variant when `changed_surfaces` names an agent/footer/scaffold-footer change.
- `release-build` with `variant_policy: "all"` renders the full internal matrix: branded, outside-broker customizable, and one variant per active in-house agent.

The default representative is `branded`. A caller can request `outside-broker-customizable` or `agent-<agent-id>` as `representative_variant` without enabling the full matrix.

Composition Preview and Release Build specs must include an approved `composition` plan. Smoke Test specs may omit `composition` only when they are explicit technical smoke runs. The plan records stable module codes, selected scaffold module IDs, static-block decisions, editable slots, required assets, compatibility counts, and approval metadata.

Generated or edited imagery is optional and separate from ordinary asset selection. When used, the campaign must include an approved `image_workflow` record and the image slot must reference it with `image_workflow_id`. Existing approved manifest assets use `asset_id` and require no image workflow record.

Every campaign must explicitly decide every scaffold static block and list each included block exactly once in the ordered modules. Module metadata distinguishes standalone headers from heroes; a header-bearing hero cannot be combined with a standalone header.

## Copy Allocation

All build modes require approved `copy_allocation` version `1.0`, with plan approval fields and stable `content_units` IDs. Each unit records exact approved text, source, content role, one channel/owner, reuse policy, occurrence cap, and claim policy. See the [authoring reference](../../projects/the-rider/skills/onbrand-the-rider-email/references/copy-allocation.md) and the four runtime examples for complete plans. `slot_allocation`, when present, must agree with the unit owners.

Validation runs before rendering or asset download and blocks every mode on missing/stale/ambiguous ownership, unauthorized repetition, missing baked-image declarations, or claims marked `requires-evidence` without references. Subject, preview, live text, alt text, declared baked-image text, and automatically extracted included static copy share the dedupe corpus. Responsive scaffold fallback copies are counted once per logical slot, rather than once per HTML branch. An explicit static unit must exactly match all visible locked text; footer/legal content retains its existing contract.

Normalization strips HTML, lowercases, normalizes punctuation and whitespace, and removes URLs. Similarity is `max(token-set Jaccard, (word-bigram Jaccard + character-4-gram Jaccard) / 2)` for pairs with at least four words each. Character grams omit spaces. Scores >= 0.65 are reported for review; scores >= 0.82 block without a named exemption. These are transparent heuristics, not semantic equivalence or authorship scores. Exact normalized repeats and restricted phrase counts remain authoritative.

Reuse requires a named exemption with reason, scope, approver, and date. Occurrence caps always apply; similarity exemptions identify exactly two units or an exact `left-id+right-id` pair. Longer exemption lists do not waive every pair. Claims retain references for review, but the runtime does not retrieve or verify their truth. A `baked-approved` image workflow requires an OCR or creator declaration; the runtime does not run OCR. No validation step rewrites approved copy. Failed validation exits with named errors before producing a new package; successful builds retain the plan, matched-owner context, and findings in metadata and QA.

The JSON/CLI contract is portable across Codex, Claude Code callers, and shell use without provider APIs. Claude Code adapter parity remains Phase 11 work.

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

Generated or edited image outputs are local files validated by checksum and dimensions before packaging. The runtime rejects unapproved workflow items, missing or unapproved source assets, real Rider environment claims not grounded in source metadata, invalid placement data, and image slots pointing at unknown workflow IDs.

The canonical Rider scaffold remains immutable input. Content changes are constrained by the typed sidecar slot map, locked static blocks are verified before asset localization, and agent headshots must resolve by exact manifest identity with the required path and approval. Builds use a protected staging directory so an interrupted or failed download cannot replace the last passing package.

`campaign-metadata.json` and `qa-report.json` record the requested build mode, representative variant, effective variant scope, changed surfaces, expansion reason, rendered variants, approved composition plan summary, and approved generated-image workflow summary. `asset-manifest.json` records the same image workflow summary plus `image_workflow_id` on packaged generated assets.

Both metadata and QA also record approved copy units, claim references, exemption approvals, occurrence counts, restricted phrase results, similarity pairs, and thresholds under `copy_allocation`.
