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

- Treat header/hero layout as a required campaign decision.
- If the prompt names an exact compatible configuration or module combination, confirm and record it without asking the user to choose again.
- If the prompt does not specify one, present compatible labeled `CFG-*` options from the header/hero gallery and ask the user to select or explicitly approve one. Offer a context-based recommendation when useful, but do not treat the recommendation as approval.
- Include hero-only, standalone-header-plus-hero, and integrated-header/hero choices when they are compatible with the campaign type; do not imply that every campaign needs a standalone header.
- Never reuse a prior campaign's selection as a default. In particular, `CFG-05` belongs to the approved wellness proof and is not the Rider-wide default.
- Never add a standalone header automatically.
- Do not invoke generated-image work or build final HTML until the header/hero decision is recorded.
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
