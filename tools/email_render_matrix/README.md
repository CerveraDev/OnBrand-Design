# Email Render Matrix

This tool captures deterministic Chromium browser previews for packaged email HTML. It is not an Outlook, Gmail, Apple Mail, or native mobile-client emulator.

Install the pinned dependency when it is not already available:

```bash
cd tools/email_render_matrix
npm install
```

Run from the repository root:

```bash
node tools/email_render_matrix/render_matrix.cjs \
  --input campaign-output/example/example/html/example-branded.html \
  --output docs/evals/render-matrix/example
```

In managed environments with Playwright supplied outside this directory, set `ONBRAND_PLAYWRIGHT_MODULE` to the directory containing the `playwright` package.

The output contains four JPEG screenshots, `render-report.json`, and `visual-review.md`. Automated checks cover browser-level overflow, missing images, failed requests, page errors, and artifact hashes. A human must complete visual review separately, and real email-client evidence remains a separate release requirement.
