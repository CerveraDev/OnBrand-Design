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
8. Generate Composition Preview review artifacts with `python3 -m tools.rider_campaign_runtime.cli catalog --output <review-folder>` when the user needs to choose among scaffold modules.
9. Ask the user to approve exact module codes, every static-block include/exclude decision, static-block placement, and representative variant.
10. Create an approved composition plan with `python3 -m tools.rider_campaign_runtime.cli plan --selection <selection.json> --output <composition-plan.json>`.
11. Build final HTML only after any required copy, creative, composition, or image approvals.
12. Select a compatible header/hero structure; do not combine a standalone header with a hero that includes one.
13. Choose the build mode explicitly: Composition Preview for a user-facing Design Proof, Smoke Test for representative technical validation, or Release Build for the full internal matrix.
14. Write a strict campaign JSON file using the runtime schema, module metadata, Rider slot map, and approved composition plan.
15. Run `python3 -m tools.rider_campaign_runtime.cli <campaign.json>` from the repository root.
16. Inspect the CLI summary and generated `qa-report.json`.
17. Deliver the generated folder and ZIP only when QA passes.

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

A campaign is not complete when only HTML files have been generated. Complete the portable distribution package described in [distribution-package.md](distribution-package.md), including all rendered HTML variants for the selected build mode, final used images, an asset manifest, and a matching ZIP archive.

HTML generation and packaging are implemented by `tools/rider_campaign_runtime/`. Do not claim an end-to-end campaign package exists unless the runtime generated the files, blocking QA passed, and the ZIP exists.

Composition Preview and ordinary Smoke Test builds are complete for their mode when the representative package passes QA. They are not full Release Builds. Release Build is the mode that renders branded, outside-broker customizable, and all active in-house agent variants.

Composition Preview and Release Build require an embedded approved `composition` plan. A technical Smoke Test may omit it only when the user explicitly requested a diagnostic run or the fixture is a known internal smoke.

Smoke Test expands to all authorized variants only when `variant_policy` is `all` or `changed-surface-expanded`. Use `changed_surfaces` values such as `agent-roster`, `agent-data`, `agent-footer-assets`, `footer-renderer`, `footer-data`, or `scaffold-footer-structure` when that broader validation is required.

## Approval Checkpoints

Use approval checkpoints when:

- Generated or edited imagery is proposed.
- The asset selector returns `review_required` or several materially different top candidates.
- The CTA is ambiguous.
- The user asked for options.
- The campaign carries higher brand, broker, or compliance sensitivity.

Do not require approval for every small copy adjustment unless the user asks for that workflow.

## Agent Variant Workflow

For in-house agent variants:

1. Read `data/agents/index.json`.
2. Load each active record in `output_order`.
3. Validate the JSON shape against `data/agents/agent.schema.json`.
4. Resolve `headshot.asset_id` through the validated master manifest.
5. Require an image under `/20. People/In-house Agents/` with `agent-footer` in `approved_for`.
6. Download the resolved headshot into the campaign package and record its manifest identity and source URL.
7. Populate only the agent fields represented in the scaffold footer.
8. Fail clearly if the record or asset is missing, ambiguous, the wrong media type, outside the required folder, or not approved.
9. Do not invent missing headshots, names, titles, phone numbers, or emails.

For outside-broker customizable variants, use supplied outside-broker data when available. Otherwise keep placeholders for the broker headshot, name, title, phone, and email while preserving Rider project branding and legal content.
