# Workflow

## Directed Build

Use this mode when the user already knows the campaign, audience, CTA, and desired output.

1. Confirm campaign type, audience, CTA, and output format.
2. Identify existing-asset needs and whether the image-generation workflow is needed.
3. For existing assets, load the configured master manifest, run [asset-selection.md](asset-selection.md), and present materially different top candidates for approval.
4. Propose a concise module plan.
5. Draft subject lines, preview text, headline, optional subheading, body copy, and CTA language.
6. Run [copy-quality.md](copy-quality.md), preserving approved facts and project voice.
7. Present final copy for approval when the request or campaign sensitivity calls for it.
8. Build final HTML only after any required copy, creative, or image approvals.
9. Generate all required footer variants.
10. Copy every final approved image used into the campaign package.
11. Create the asset manifest, verify the HTML references, and run QA.
12. Deliver the campaign folder and matching ZIP.

## Concept Development

Use this mode when the user gives a broad idea and wants suggestions.

Provide options before building:

- 2-3 campaign angles
- Headline directions
- Subject line options
- Preview text options
- CTA options
- Hero/image direction
- Recommended module plan

After the user chooses or revises a direction, continue as a directed build. Apply the copy-quality pass to the selected direction rather than polishing every discarded option into near-duplicates.

## Completion Deliverable

A campaign is not complete when only HTML files have been generated. Complete the portable distribution package described in [distribution-package.md](distribution-package.md), including all HTML variants, final used images, an asset manifest, and a matching ZIP archive.

If the calibrated project supplies a strict campaign schema and runtime, encode the approved campaign in that schema and require the runtime's blocking QA to pass. Do not substitute manual global replacements for typed project slots.

## Approval Checkpoints

Use approval checkpoints when:

- Generated or edited imagery is proposed.
- The asset selector returns `review_required` or several materially different top candidates.
- The CTA is ambiguous.
- The user asked for options.
- The campaign carries higher brand, broker, or compliance sensitivity.

Do not require approval for every small copy adjustment unless the user asks for that workflow.
