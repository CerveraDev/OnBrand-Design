# QA

Run QA before delivery.

## General Checks

- Campaign goal is reflected in headline, copy, CTA, and imagery.
- Subject line and preview text are present when requested.
- CTA is clear and consistent.
- No invented phone numbers, email addresses, URLs, deadlines, pricing, or availability.
- Images have appropriate alt text when possible.
- Output variant names are clear.
- Build mode, representative variant, effective variant scope, changed surfaces, and expansion reason are recorded in `campaign-metadata.json` and `qa-report.json`.
- Composition Preview and Release Build record the approved composition plan in `campaign-metadata.json` and `qa-report.json`.
- Generated or edited imagery records the approved image workflow summary in `campaign-metadata.json`, `asset-manifest.json`, and `qa-report.json`.
- Every build records approved `copy_allocation`, including source/owner context, claim references, exemptions, occurrence counts, and similarity results in metadata and QA.
- Composition Preview and ordinary Smoke Test builds render one representative variant; Release Build renders the full internal matrix.
- Package contains both the campaign folder and matching ZIP.
- Asset manifest accounts for every image reference in every delivered HTML file.

## Copy Checks

- Copy passed [copy-quality.md](copy-quality.md) after the campaign direction was selected.
- Copy passed the pre-render [copy allocation gate](copy-allocation.md): every creative owner is allocated, unit text matches exactly, and restricted phrases stay within approved caps across metadata, live HTML, alt text, and declared baked-image text.
- Near-duplicate scores of at least 0.65 are reviewed; scores of at least 0.82 block without a scoped exemption. Exemptions never waive occurrence caps.
- Units marked `requires-evidence` carry approved claim references. Reference presence does not prove factual support or legal compliance.
- Copy fixes were presented for approval; the runtime did not rewrite approved text.
- Subject line, preview text, headline, body, and CTA support one coherent action.
- Preview text adds information instead of repeating the subject line.
- Generic luxury language was replaced with supported project detail where possible.
- Watchlist words were reviewed in context rather than removed mechanically.
- No invented or unsupported facts, urgency, superlatives, quotations, testimonials, statistics, pricing, dates, or availability remain.
- Copy cleanup did not alter supplied legal language, approved terminology, or the intended meaning.
- No internal editing notes, AI-authorship claims, detector scores, or process commentary appear in campaign output.

## Footer Variant Checks

- Full footer/agent validation runs for Release Build and for Smoke Test builds with `variant_policy` set to `all` or `changed-surface-expanded`.
- Branded version uses branded footer.
- Outside-broker customizable version preserves Rider branding/legal content and exposes broker headshot, name, title, phone, and email fields.
- Each in-house agent version uses an active JSON record from `data/agents/index.json`.
- No invented agent or outside-broker contact data appears.
- Every in-house headshot resolves by exact manifest `dropbox_id` to an image under `/20. People/In-house Agents/` approved for `agent-footer`.
- Diego Ojeda likeness references never appear in an agent footer.
- Footer scaffold markup was not rewritten unless requested.

## HTML Checks

- Uses the canonical Beefree scaffold table structure.
- The canonical typo corrections are present: `REQUEST MORE INFORMATION` and `ARTS`.
- No generated output contains marker rows, marker labels, `#55ebb9`, `#ff81fb`, or marker-only `#393d47`.
- Row 1 shared custom CSS, head CSS, linked fonts, Outlook/VML conditionals, outer wrapper, responsive behavior, original row classes, and complete table structures are preserved.
- Avoids fragile CSS where possible.
- Complex overlays are flattened into images unless a safe live structure is known.
- Footer insertion did not break document structure.
- No HTML contains an absolute local path, temporary path, or direct path into the source corpus.
- Every relative local image reference resolves to a file inside the package.
- Shared images are packaged once and referenced consistently across variants.
- Any external image URLs or deployment substitutions are identified in the manifest.
- `qa-report.json` reports every blocking runtime check as passed before the ZIP is created.
- Every scaffold static block has an explicit include/exclude decision.
- Every included static block appears exactly once in the approved order and passed the pre-packaging byte lock.
- Excluded static blocks are absent.
- Asset URL localization is the only permitted packaging transformation inside an included static block.
- No standalone header appears beside a hero classified as including its own header.
- Static marker colors `#ffd675` and `#75edff` never appear in generated output.

## Composition Checks

- Stable module codes resolve to known Rider scaffold modules.
- Selected module codes match the campaign modules in exact order.
- Every static block has exactly one include/exclude decision.
- Included static block codes appear exactly once in the selected module order.
- Excluded static block codes are absent from the selected module order.
- Composition Preview and Release Build fail if the approved composition plan is missing.

## Image Checks

- Approved existing images remain accurate.
- Generated or edited hero images received user approval and have matching `image_workflow` provenance.
- Real Rider environments use approved source assets whose filename, path, or category matches the claimed environment, such as gym, lobby, arrival, exterior, or amenity.
- Source assets are tracked by manifest ID or checksummed local/scaffold path.
- Output checksum, dimensions, intended module/slot, role, crop, focal point, and text policy match the final packaged image.
- Every `baked-approved` workflow has declared text in allocation. Actual bitmap text is reviewed against the declaration; OCR execution remains external.
- Branded objects are used only when requested and approved.
- Rejected and unused image candidates are excluded from the package unless explicitly requested.
