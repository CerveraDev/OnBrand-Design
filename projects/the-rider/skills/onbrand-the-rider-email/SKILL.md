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

The canonical Beefree scaffold is available at [templates/scaffold/rider-scaffolding.canonical.html](templates/scaffold/rider-scaffolding.canonical.html). Treat it as the source of structure, module boundaries, brand styling, legal copy, and footer layouts. Keep the immutable provenance copy at [templates/scaffold/rider-scaffolding.source.html](templates/scaffold/rider-scaffolding.source.html) unchanged.

## Core Workflow

1. Classify the request as either directed build or concept development.
2. Load the relevant references, not the whole skill corpus.
3. Confirm only missing essentials.
4. Draft the campaign strategy, module plan, subject lines, preview text, copy, CTA, and image direction.
5. Run the project-aware copy-quality pass before presenting copy for approval or building HTML.
6. For existing imagery, load the configured Rider manifest and run deterministic asset selection before choosing images.
7. If generated or edited imagery is needed, hand off to `onbrand-the-rider-image` before building HTML.
8. Encode the approved campaign as a JSON document that conforms to `tools/rider_campaign_runtime/campaign.schema.json` and uses only slots declared in the Rider scaffold sidecar map.
9. Run `python3 -m tools.rider_campaign_runtime.cli <campaign.json>` from the repository root.
10. Treat a nonzero exit or blocked QA report as a failed build; do not hand-assemble around it or create a ZIP manually.
11. Deliver the generated campaign folder and ZIP only after reviewing the runtime summary and `qa-report.json`.

## Intake Modes

Use directed build when the user already provides campaign type, audience, CTA, and output needs. Move quickly from brief to layout and HTML.

Use concept development when the user gives only a broad idea. Before writing final HTML, provide options for campaign angle, headline direction, subject line, preview text, CTA, visual direction, and module plan.

Read [references/intake.md](references/intake.md) for required and optional intake fields.

## Required Modules

Every email must include:

- Hero module
- Footer module

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

## HTML Output

Use the canonical Beefree scaffold as the structural compatibility benchmark. Prefer conservative HTML email patterns already present in the scaffold: table-based layout, inline CSS, stable image blocks, spacer rows, Outlook-safe structure, and simple responsive behavior.

Read [references/beefree-html-structure.md](references/beefree-html-structure.md) and [references/html-email.md](references/html-email.md) before producing final HTML.

Use [templates/scaffold/rider-scaffolding.slot-map.json](templates/scaffold/rider-scaffolding.slot-map.json) as the deterministic editable-slot contract. Do not add a new slot by searching and replacing arbitrary scaffold text. A new slot requires a unique anchor, a typed operation, and a regression test.

Read [references/distribution-package.md](references/distribution-package.md) before final delivery. Every completed campaign must be a portable folder plus a matching ZIP containing all HTML variants, the final images used by those files, and an asset manifest. Never move or modify source images in the Rider corpus; copy them into the campaign package.

## Output Variants

Unless the user explicitly narrows the deliverable, a completed Rider campaign should produce:

- Branded Rider version
- Outside-broker customizable version
- One in-house agent version for each active Rider agent record

The outside-broker customizable version does not remove Rider project identity, developer/legal content, or the campaign footer framework. It replaces in-house contact ownership with placeholders or supplied outside-broker data for headshot, name, title, phone, and email.

In-house agent variants load factual records from [data/agents](data/agents). Each in-house agent has one JSON record; [data/agents/index.json](data/agents/index.json) defines the active set and deterministic output order. Resolve each `headshot.asset_id` through the validated manifest and require an image under `/20. People/In-house Agents/` approved for `agent-footer`. Do not invent missing agent facts or substitute images by filename.

## Runtime Contract

The runtime is Rider-specific and lives at `tools/rider_campaign_runtime/`. Its strict campaign schema rejects unknown fields and unsafe URL combinations. Its package builder downloads only rendered assets, verifies checksums, records provenance and variant usage, writes machine-readable QA, and creates a ZIP only after blocking checks pass.

Use `projects/the-rider/skills/onbrand-the-rider-email/examples/smoke-campaign.runtime.json` only as an internal non-production example. Replace its sample copy and module selection with approved campaign content; never send or deploy the smoke output.

## References

- [references/workflow.md](references/workflow.md): end-to-end campaign flow
- [references/intake.md](references/intake.md): directed and concept-development intake
- [references/campaign-types.md](references/campaign-types.md): campaign category rules
- [references/copywriting.md](references/copywriting.md): copy, CTA, headline, subject-line rules
- [references/copy-quality.md](references/copy-quality.md): project-aware editorial pass and audit mode
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
