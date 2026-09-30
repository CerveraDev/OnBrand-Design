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

## Footer Variant Checks

- Branded version uses branded footer.
- Broker-neutral version removes sales attribution and direct contact ownership.
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
