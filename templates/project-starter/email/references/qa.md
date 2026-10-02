# QA

Run QA before delivery.

## General Checks

- Campaign goal is reflected in headline, copy, CTA, and imagery.
- Subject line and preview text are present when requested.
- CTA is clear and consistent.
- No invented phone numbers, email addresses, URLs, deadlines, pricing, or availability.
- Images have appropriate alt text when possible.
- Output variant names are clear.
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

- Branded version uses branded footer.
- Outside-broker customizable version preserves project/legal content and uses supplied broker personalization or clear placeholders.
- Each in-house agent version uses the correct agent footer.
- Locked footer HTML was not rewritten unless requested.

## HTML Checks

- Uses Beefree-style table structure.
- Avoids fragile CSS where possible.
- Complex overlays are flattened into images unless a safe live structure is known.
- Footer insertion did not break document structure.
- No HTML contains an absolute local path, temporary path, or direct path into the source corpus.
- Every relative local image reference resolves to a file inside the package.
- Shared images are packaged once and referenced consistently across variants.
- Any external image URLs or deployment substitutions are identified in the manifest.

## Image Checks

- Approved existing images remain accurate.
- Generated or edited hero images received user approval when needed.
- Branded objects are used only when requested and approved.
- Rejected and unused image candidates are excluded from the package unless explicitly requested.
