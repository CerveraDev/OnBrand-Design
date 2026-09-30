---
name: onbrand-__PROJECT_SLUG__-image
description: Explicitly invoked workflow for generating or editing __PROJECT_NAME__ campaign imagery from approved assets and returning approval-ready visual candidates.
disable-model-invocation: true
metadata:
  short-description: Create __PROJECT_NAME__ campaign image candidates
---

# OnBrand Design: __PROJECT_NAME__ Image Studio

Run this skill only when the user explicitly invokes `$onbrand-__PROJECT_SLUG__-image` in Codex or `/onbrand-__PROJECT_SLUG__-image` in Claude Code. Do not infer invocation from an ordinary image or __PROJECT_NAME__ email request.

Use this skill only for __PROJECT_NAME__ campaign imagery that requires generation, editing, compositing, or visual concept options. Simple selection from an approved image library can remain in the main __PROJECT_NAME__ email skill.

This workflow is isolated so image work can focus on visual accuracy, brand-safe generation, and approval candidates without loading the full email HTML system.

## Inputs

Before generating or editing imagery, identify:

- Campaign goal
- Intended module, usually hero
- Base image or approved image folder
- Required visual change
- Whether __PROJECT_NAME__ branding must appear in the image
- Output orientation or approximate crop
- Whether text should be baked into the image or left for HTML
- Number of candidates requested

Ask only for missing details that materially affect image generation.

## Core Rules

- Preserve the real building design when using an approved __PROJECT_NAME__ building image.
- Do not invent architectural changes.
- Do not add people, logos, signage, or claims that the user did not request.
- Use generated visuals as approval candidates before final HTML is built.
- Prefer polished, premium, believable, architectural results.
- Keep image-generation prompts grounded in the supplied campaign and base asset.
- After approval, return the final image file and its provenance details to the email workflow so it can be copied into the campaign distribution package.

## Generated Image Example

When a campaign needs a new branded visual:

- Use an approved __PROJECT_NAME__ image as the base when one is supplied.
- Add only the object, treatment, or brand element requested in the brief.
- Keep protected architecture and source-image details unchanged.
- Return visual candidates for approval.
- Let the main email skill decide whether headline text is live HTML or baked into the final image.

## References

- [references/image-brief.md](references/image-brief.md): intake and prompt construction
- [references/approval.md](references/approval.md): candidate review workflow
- [references/brand-safety.md](references/brand-safety.md): accuracy and brand constraints
