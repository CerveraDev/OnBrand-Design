---
name: onbrand-the-rider-email
description: Explicitly invoked workflow for creating Rider Residences email marketing pieces with project-specific copy, modules, Beefree-style HTML structure, locked footer variants, and a complete distribution package.
disable-model-invocation: true
metadata:
  short-description: Build Rider Residences email campaigns
---

# OnBrand Design: The Rider

Run this skill only when the user explicitly invokes `$onbrand-the-rider-email` in Codex or `/onbrand-the-rider-email` in Claude Code. Do not infer invocation from an ordinary request involving Rider, real estate, email copy, HTML, or images.

Use this skill for Rider Residences email marketing only. Do not generalize it into a reusable real estate skill. If another property needs the same type of support, create a separate property-specific skill.

The canonical Beefree scaffold is available at [templates/scaffold/rider-scaffolding.canonical.html](templates/scaffold/rider-scaffolding.canonical.html). Treat it as the source of structure, module boundaries, brand styling, legal copy, static blocks, and footer layouts. Keep the latest immutable source at [templates/scaffold/rider-scaffolding.source.html](templates/scaffold/rider-scaffolding.source.html) unchanged; earlier supplied sources remain under `templates/scaffold/provenance/`.

## Core Workflow

1. Classify the request as either directed build or concept development.
2. Load the relevant references, not the whole skill corpus.
3. Confirm only missing essentials.
4. Draft the campaign strategy, module plan, subject lines, preview text, copy, CTA, and image direction.
5. Run the project-aware copy-quality pass before presenting copy for approval or building HTML.
6. For existing imagery, load the configured Rider manifest and run deterministic asset selection before choosing images.
7. Generate the Composition Preview catalog/review artifacts when the user needs to choose modules: `python3 -m tools.rider_campaign_runtime.cli catalog --output <review-folder>`.
8. Ask the user to approve exact module codes, every static-block include/exclude decision, static-block placement in the module order, and representative variant before generated image work or final HTML assembly.
9. Create the approved composition plan with `python3 -m tools.rider_campaign_runtime.cli plan --selection <selection.json> --output <composition-plan.json>`.
10. If generated or edited imagery is needed, hand off to `onbrand-the-rider-image` only after the relevant hero/image module is approved, then require an approved `image_workflow` provenance record before runtime assembly.
11. Choose either a compatible standalone header plus hero or a hero that includes its own header. Never add a header automatically.
12. Create the approved [copy allocation plan](references/copy-allocation.md), including metadata, live copy, alt text, declared baked-image text, claim references, and narrowly scoped reuse approvals. Encode it as `copy_allocation` in the campaign JSON alongside the approved `composition` plan and only slots declared in the Rider scaffold sidecar map.
13. Run `python3 -m tools.rider_campaign_runtime.cli <campaign.json>` from the repository root.
14. Treat a nonzero exit or blocked QA report as a failed build; do not hand-assemble around it or create a ZIP manually.
15. Deliver the generated campaign folder and ZIP only after reviewing the runtime summary and `qa-report.json`.

## Intake Modes

Use directed build when the user already provides campaign type, audience, CTA, and output needs. Move quickly from brief to layout and HTML.

Use concept development when the user gives only a broad idea. Before writing final HTML, provide options for campaign angle, headline direction, subject line, preview text, CTA, visual direction, and module plan.

Read [references/intake.md](references/intake.md) for required and optional intake fields.

## Required Modules

Every email must include:

- Hero module
- Footer module

A standalone header is optional. Some hero modules include their own header and are incompatible with a separate header. Use `templates/scaffold/rider-scaffolding.module-metadata.json` to classify modules and enforce compatibility.

Static blocks are optional locked modules, but the user must make an explicit include/exclude decision for every one. Included static blocks can be placed anywhere in the approved module order. Their copy and structure are not editable slots.

Read [references/modules.md](references/modules.md) before designing modules, selecting scaffold row ranges, or deciding whether hero text should be live HTML or baked into an image.

Read [references/footers.md](references/footers.md) before creating final output variants. Footers are locked HTML partials by default.

## Image Handling

Simple selection from approved Rider assets can stay in this skill. Generated, composited, or edited imagery must be treated as a separate image-generation workflow.

Read [references/asset-selection.md](references/asset-selection.md) for ordinary image choice.

Ordinary image choice must consume a configured, validated master manifest and approved public asset URLs. Do not run `tools/dropbox-manifest/build_manifest.py` during campaign generation unless the user explicitly requests a manifest refresh.

Invoke or follow the separate `onbrand-the-rider-image` skill when:

- A new hero image must be generated or edited.
- A real Rider building image must be preserved accurately.
- A branded object, such as a Rider-logo hard hat, must be added.
- Multiple visual candidates or an approval checkpoint are needed before HTML is built.

That image skill is also explicit-only. Ask the user to invoke `$onbrand-the-rider-image` in Codex or `/onbrand-the-rider-image` in Claude Code before beginning generated or edited image work.

Generated or edited imagery must return a local output file plus an `image_workflow` item for the campaign JSON. The matching image slot must use `src` and `image_workflow_id`; ordinary approved existing-asset selections continue to use `asset_id` and do not need image workflow metadata. Runtime builds reject generated imagery whose workflow item is not approved, whose source assets are missing or unapproved, whose real Rider environment is not grounded in matching manifest metadata, or whose output checksum/dimensions do not match the local file.

## HTML Output

Use the canonical Beefree scaffold as the structural compatibility benchmark. Prefer conservative HTML email patterns already present in the scaffold: table-based layout, inline CSS, stable image blocks, spacer rows, Outlook-safe structure, and simple responsive behavior.

Read [references/beefree-html-structure.md](references/beefree-html-structure.md) and [references/html-email.md](references/html-email.md) before producing final HTML.

Use [templates/scaffold/rider-scaffolding.slot-map.json](templates/scaffold/rider-scaffolding.slot-map.json) as the deterministic editable-slot contract. Do not add a new slot by searching and replacing arbitrary scaffold text. A new slot requires a unique anchor, a typed operation, and a regression test.

Use [templates/scaffold/rider-scaffolding.module-metadata.json](templates/scaffold/rider-scaffolding.module-metadata.json) for module type, header inclusion, lock state, and the user-facing static-block summaries.

Read [references/distribution-package.md](references/distribution-package.md) before final delivery. Every completed runtime build must be a portable folder plus a matching ZIP containing its rendered HTML variants, the final images used by those files, and an asset manifest. Never move or modify source images in the Rider corpus; copy them into the campaign package.

## Output Variants

Choose a runtime build mode explicitly:

- Composition Preview: user-facing Design Proof for selecting/reviewing a representative version. It renders one variant.
- Smoke Test: automated technical validation. It renders one representative variant unless the campaign explicitly requests all variants or declares a changed surface that requires full footer/agent validation.
- Release Build: final internal output. It renders the full authorized internal matrix.

The default representative variant is `branded`. A caller may choose `outside-broker-customizable` or `agent-<agent-id>` as `representative_variant` without enabling every variant.

A Release Build produces:

- Branded Rider version
- Outside-broker customizable version
- One in-house agent version for each active Rider agent record

The outside-broker customizable version does not remove Rider project identity, developer/legal content, or the campaign footer framework. It replaces in-house contact ownership with placeholders or supplied outside-broker data for headshot, name, title, phone, and email.

In-house agent variants load factual records from [data/agents](data/agents). Each in-house agent has one JSON record; [data/agents/index.json](data/agents/index.json) defines the active set and deterministic output order. Resolve each `headshot.asset_id` through the validated manifest and require an image under `/20. People/In-house Agents/` approved for `agent-footer`. Do not invent missing agent facts or substitute images by filename.

## Runtime Contract

The runtime is Rider-specific and lives at `tools/rider_campaign_runtime/`. Its strict campaign schema rejects unknown fields and unsafe URL combinations. Its package builder downloads only rendered assets, verifies checksums, records provenance and variant usage, writes machine-readable QA, and creates a ZIP only after blocking checks pass.

The runtime also owns the portable Composition Preview and generated-image provenance workflow. `catalog` produces stable module codes and isolated HTML preview artifacts. `plan` consumes an explicit approved selection and writes a composition plan that the build step validates before rendering. `image_workflow` records generated/edited image provenance in the same campaign JSON. This file workflow is usable from Codex, Claude Code, or a normal shell.

Every build mode requires approved `copy_allocation`. Ownership, exact/normalized repetition, restricted phrases, declared image text, and near-duplicate checks run before rendering; failures block packaging. Passing builds retain the approved units, claim references, exemptions, counts, and similarity results in metadata and QA. Proposed copy revisions remain reviewable options; never silently rewrite approved user copy to pass QA. Claude Code can call this portable CLI contract; adapter support still awaits Phase 11 parity validation.

Use `projects/the-rider/skills/onbrand-the-rider-email/examples/smoke-campaign.runtime.json` only as an internal non-production example. Replace its sample copy and module selection with approved campaign content; never send or deploy the smoke output.

## References

- [references/workflow.md](references/workflow.md): end-to-end campaign flow
- [references/intake.md](references/intake.md): directed and concept-development intake
- [references/campaign-types.md](references/campaign-types.md): campaign category rules
- [references/copywriting.md](references/copywriting.md): copy, CTA, headline, subject-line rules
- [references/copy-quality.md](references/copy-quality.md): project-aware editorial pass and audit mode
- [references/copy-allocation.md](references/copy-allocation.md): approved ownership, reuse, claims, and repetition QA
- [references/modules.md](references/modules.md): required and optional email modules
- [references/footers.md](references/footers.md): locked footer variants and output set
- [references/asset-selection.md](references/asset-selection.md): approved image selection rules
- [references/brand.md](references/brand.md): calibrated Rider brand guidance
- [references/email-design-system.md](references/email-design-system.md): calibrated visual rules
- [references/beefree-html-structure.md](references/beefree-html-structure.md): Beefree-style compatibility benchmark
- [references/html-email.md](references/html-email.md): final HTML assembly rules
- [references/distribution-package.md](references/distribution-package.md): portable campaign folder and ZIP requirements
- [references/qa.md](references/qa.md): pre-delivery review
- [references/calibration.md](references/calibration.md): calibration history and future recalibration guidance
