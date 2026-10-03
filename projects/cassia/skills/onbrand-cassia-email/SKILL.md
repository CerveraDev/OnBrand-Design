---
name: onbrand-cassia-email
description: Explicitly invoked workflow for creating Cassia email marketing pieces with project-specific copy, modules, Beefree-style HTML structure, locked footer variants, and a complete distribution package.
metadata:
  short-description: Build Cassia email campaigns
---

# OnBrand Design: Cassia

Run this skill only when the user explicitly invokes `$onbrand-cassia-email` in Codex or `/onbrand-cassia-email` in Claude Code. Do not infer invocation from an ordinary request involving Cassia, real estate, email copy, HTML, or images.

Use this skill for Cassia email marketing only. Do not generalize it into a reusable real estate skill. If another property needs the same type of support, create a separate property-specific skill.

This first draft is provisional. The user will later provide a Beefree-generated Cassia HTML sample and locked footer partials. Until those arrive, keep brand, design-system, HTML, and footer details explicit about what is known versus pending.

## Core Workflow

1. Classify the request as either directed build or concept development.
2. Load the relevant references, not the whole skill corpus.
3. Confirm only missing essentials.
4. Draft the campaign strategy, module plan, subject lines, preview text, copy, CTA, and image direction.
5. Run the project-aware copy-quality pass before presenting copy for approval or building HTML.
6. If generated or edited imagery is needed, hand off to `onbrand-cassia-image` before building HTML.
7. Build the email body using Cassia modules and Beefree-style, table-based email structure.
8. Append locked footer partials to produce the required output variants.
9. Assemble the campaign distribution package with all HTML variants and every final image they use.
10. Run QA, create a ZIP archive, and deliver both the package folder and ZIP.

## Intake Modes

Use directed build when the user already provides campaign type, audience, CTA, and output needs. Move quickly from brief to layout and HTML.

Use concept development when the user gives only a broad idea. Before writing final HTML, provide options for campaign angle, headline direction, subject line, preview text, CTA, visual direction, and module plan.

Read [references/intake.md](references/intake.md) for required and optional intake fields.

## Required Modules

Every email must include:

- Hero module
- Footer module

Read [references/modules.md](references/modules.md) before designing modules or deciding whether hero text should be live HTML or baked into an image.

Read [references/footers.md](references/footers.md) before creating final output variants. Footers are locked HTML partials by default.

## Image Handling

Simple selection from approved Cassia assets can stay in this skill. Generated, composited, or edited imagery must be treated as a separate image-generation workflow.

Read [references/asset-selection.md](references/asset-selection.md) for ordinary image choice.

Invoke or follow the separate `onbrand-cassia-image` skill when:

- A new hero image must be generated or edited.
- A real Cassia building image must be preserved accurately.
- A branded object, such as a Cassia-logo hard hat, must be added.
- Multiple visual candidates or an approval checkpoint are needed before HTML is built.

That image skill is also explicit-only. Ask the user to invoke `$onbrand-cassia-image` in Codex or `/onbrand-cassia-image` in Claude Code before beginning generated or edited image work.

## HTML Output

Use Beefree as the structural compatibility benchmark. Prefer conservative HTML email patterns: table-based layout, inline CSS, stable image blocks, spacer rows, Outlook-safe structure, and simple responsive behavior.

Read [references/beefree-html-structure.md](references/beefree-html-structure.md) and [references/html-email.md](references/html-email.md) before producing final HTML.

Read [references/distribution-package.md](references/distribution-package.md) before final delivery. Every completed campaign must be a portable folder plus a matching ZIP containing all HTML variants, the final images used by those files, and an asset manifest. Never move or modify source images in the Cassia corpus; copy them into the campaign package.

After the user provides the Beefree-generated Cassia sample HTML, perform the calibration workflow in [references/calibration.md](references/calibration.md) and update the provisional references.

## Output Variants

Unless the user explicitly narrows the deliverable, a completed Cassia campaign should produce:

- Branded Cassia version
- Broker-neutral outside-agent version
- One in-house agent version for each provided Cassia agent footer

The broker-neutral version does not remove Cassia project identity. It removes sales attribution and direct contact ownership, such as phone numbers, email addresses, web addresses, sales team logos, and agent details that would prevent an outside broker from using the piece.

## References

- [references/workflow.md](references/workflow.md): end-to-end campaign flow
- [references/intake.md](references/intake.md): directed and concept-development intake
- [references/campaign-types.md](references/campaign-types.md): campaign category rules
- [references/copywriting.md](references/copywriting.md): copy, CTA, headline, subject-line rules
- [references/copy-quality.md](references/copy-quality.md): project-aware editorial pass and audit mode
- [references/modules.md](references/modules.md): required and optional email modules
- [references/footers.md](references/footers.md): locked footer variants and output set
- [references/asset-selection.md](references/asset-selection.md): approved image selection rules
- [references/brand.md](references/brand.md): provisional Cassia brand guidance
- [references/email-design-system.md](references/email-design-system.md): provisional visual rules
- [references/beefree-html-structure.md](references/beefree-html-structure.md): Beefree-style compatibility benchmark
- [references/html-email.md](references/html-email.md): final HTML assembly rules
- [references/distribution-package.md](references/distribution-package.md): portable campaign folder and ZIP requirements
- [references/qa.md](references/qa.md): pre-delivery review
- [references/calibration.md](references/calibration.md): future update from supplied Beefree HTML
