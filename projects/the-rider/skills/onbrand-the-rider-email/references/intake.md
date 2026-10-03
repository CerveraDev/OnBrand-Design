# Intake

## Required When Known

Ask only for missing essentials that materially affect the email.

- Campaign idea or campaign type
- Audience
- Primary goal
- CTA
- Image source: approved library, temporary campaign folder, or generated/edited image
- Output requested: concept only, copy only, layout map, final HTML, or full variant set
- Deployment destination, if known

## Module Decisions

Before building HTML:

- Ask whether the campaign should use a standalone header or a hero that includes its own header.
- Never add a standalone header automatically.
- Present every static block using the summary in `templates/scaffold/rider-scaffolding.module-metadata.json`.
- Record an explicit `include` or `exclude` decision for every static block.
- Ask where each included static block belongs in the ordered module plan.

Do not silently include all static blocks, silently omit them, or rewrite their locked brand copy.

## Directed Prompt Example

```text
Use the Rider Residences email skill to create an eFlyer for a post-event recap of the hard hat walkthrough.

Audience: brokers and interested buyers.
Goal: show strong event momentum and encourage private appointments.
CTA: Schedule a private tour.
Images: use the walkthrough photo folder.
Tone: polished, confident, warm, not too salesy.
Output: final HTML email variants.
```

## Broad Prompt Example

```text
I want to do a Rider Residences campaign around the hard hat walkthrough. Give me a few directions for the email before building it.
```

For broad prompts, produce options before requesting final approval.
