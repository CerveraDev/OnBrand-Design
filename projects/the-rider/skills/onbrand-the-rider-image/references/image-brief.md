# Image Brief

## Required Brief Fields

- Campaign goal
- Image purpose
- Base image or approved image source
- Whether the environment is a real Rider environment or explicitly approved conceptual treatment
- Desired visual edit or generated element
- Brand element requirements
- Crop or placement needs
- Number of candidates
- Whether text should be included in the image

## Prompt Shape

Use prompts that specify:

- What must remain unchanged
- What should be added or altered
- Where new elements should appear
- Overall tone and realism
- Any forbidden changes
- Runtime provenance fields: intended module, intended slot, source asset identity, output dimensions, output checksum, crop, focal point, and text policy

## Example

```text
Use the approved Rider building hero image as the base. Create a campaign hero for the hard hat tour. Add a white or black hard hat with the Rider logo on it, positioned above or in front of the building. Keep the building architecture unchanged. Make the result polished, premium, believable, and architectural. Do not add people or change the facade.
```

For a Rider gym or lobby request, propose approved manifest source assets first and record the selected environment base in `source_assets` before editing. Do not invent a different room when the campaign names a real Rider space.
