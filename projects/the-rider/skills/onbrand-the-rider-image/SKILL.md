---
name: onbrand-the-rider-image
description: Explicitly invoked workflow for generating or editing Rider Residences campaign imagery from approved assets and returning approval-ready visual candidates.
metadata:
  short-description: Create Rider campaign image candidates
---

# OnBrand Design: The Rider Image Studio

Run this skill only when the user explicitly invokes `$onbrand-the-rider-image` in Codex or `/onbrand-the-rider-image` in Claude Code. Do not infer invocation from an ordinary image or Rider email request.

Use this skill only for Rider Residences campaign imagery that requires generation, editing, compositing, or visual concept options. Simple selection from an approved image library can remain in the main Rider email skill.

This workflow is isolated so image work can focus on visual accuracy, brand-safe generation, and approval candidates without loading the full email HTML system.

## Inputs

Before generating or editing imagery, identify:

- Campaign goal
- Intended module, usually hero
- Base image or approved image folder
- Required visual change
- Whether Rider branding must appear in the image
- Output orientation or approximate crop
- Whether text should be baked into the image or left for HTML
- Number of candidates requested

Ask only for missing details that materially affect image generation.

## Core Rules

- Preserve the real building design when using an approved Rider building image.
- Do not invent architectural changes.
- Do not add people, logos, signage, or claims that the user did not request.
- Use generated visuals as approval candidates before final HTML is built.
- Prefer polished, premium, believable, architectural results.
- Keep image-generation prompts grounded in the supplied campaign and base asset.
- After approval, return the final image file and its provenance details to the email workflow so it can be copied into the campaign distribution package.
- For real Rider environments such as gym, lobby, arrival, exterior, or amenity scenes, start from approved Rider manifest imagery by default. A conceptual environment is allowed only when explicitly approved and labeled conceptual.
- Return provenance in the runtime `image_workflow` shape: image ID, intended module/slot/role, source asset IDs or checksummed scaffold paths, environment keywords, prompt record, output path/checksum/dimensions, placement constraints, approval status, approved by, and approved at.

## Hard Hat Tour Example

For a hard hat tour hero:

- Use an approved Rider building image as the base.
- Add a white or black hard hat with the Rider logo embedded on the hard hat.
- Position the hard hat above or in front of the building as directed.
- Keep the building unchanged.
- Return visual candidates for approval.
- Let the main email skill decide later whether headline text is live HTML or baked into the final hero.

## Runtime Handoff

After the user approves a candidate, provide a local image file and a JSON-ready `image_workflow.items[]` record. Codex ImageGen, Claude-compatible tools, or manual image editing can all fulfill the workflow as long as the record is complete and the output file checksum and dimensions match. The email skill will place the final image with an `image_workflow_id`; rejected or candidate images must not enter runtime builds.

## References

- [references/image-brief.md](references/image-brief.md): intake and prompt construction
- [references/approval.md](references/approval.md): candidate review workflow
- [references/brand-safety.md](references/brand-safety.md): accuracy and brand constraints
