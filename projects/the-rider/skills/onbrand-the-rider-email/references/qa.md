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
- Composition Preview and ordinary Smoke Test builds render one representative variant; Release Build renders the full internal matrix.
- Package contains both the campaign folder and matching ZIP.
- Asset manifest accounts for every image reference in every delivered HTML file.

## Copy Checks

- Copy passed [copy-quality.md](copy-quality.md) after the campaign direction was selected.
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

## Image Checks

- Approved existing images remain accurate.
- Generated or edited hero images received user approval when needed.
- Branded objects are used only when requested and approved.
- Rejected and unused image candidates are excluded from the package unless explicitly requested.
