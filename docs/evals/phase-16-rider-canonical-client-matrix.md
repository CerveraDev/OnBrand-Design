# Phase 16 Rider Canonical Client Matrix

**Date:** 2026-10-05  
**Campaign:** Rider wellness canonical Composition Preview  
**Variant:** Branded  
**HTML SHA-256:** `b82bcc430806bd174e621f379ee4a5ef132bab59900e50c4af1188700580ea60`  
**Status:** Automated and visual browser matrix passed; native email-client evidence pending

## Browser Visual Review

The exact canonical packaged HTML was inspected in the Codex in-app browser at the ordinary desktop surface and through the committed 390px same-origin iframe harness.

| Surface | Width | Result | Findings |
| --- | ---: | --- | --- |
| Desktop browser | Wide app viewport | Pass | Centered email canvas, coherent hierarchy, readable copy, intact image credits, aligned CTAs, complete footer, and no visible overlaps or clipping. |
| Mobile browser harness | 390px | Pass | Header stacks logo above headline, copy remains readable, images resize cleanly, CTA content stacks vertically, footer columns collapse to one column, and no visible overlaps or horizontal clipping appear. |

The mobile harness is committed at `docs/evals/render-matrix/rider-wellness-phase16-canonical/mobile-review.html`. It loads the exact ignored campaign output and sizes its same-origin iframe to the rendered document height. It is browser-review evidence only.

The email contains an empty `prefers-color-scheme: dark` media query and otherwise uses a fixed palette. Browser dark preference and native-client color rewriting still require the formal matrix; no dark-mode pass is inferred from the light browser review.

## Automated Browser Matrix

The pinned Playwright package and Chromium 151 were installed successfully. The managed Codex shell could not launch Chromium because macOS denied its Mach-port rendezvous registration, so the exact same versioned command was run from an ordinary Terminal.

The generated machine report is `docs/evals/render-matrix/rider-wellness-phase16-canonical/render-report.json`.

| Entry | Viewport | Scheme | Overflow | Images | Errors | Result |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| `desktop-light` | 1440 x 1200 | Light | 0px | 6/6 | 0 | Pass |
| `mobile-light` | 390 x 844 | Light | 0px | 6/6 | 0 | Pass |
| `desktop-dark` | 1440 x 1200 | Dark preference | 0px | 6/6 | 0 | Pass |
| `mobile-dark` | 390 x 844 | Dark preference | 0px | 6/6 | 0 | Pass |

Every entry has a non-empty document and screenshot, zero horizontal overflow, all images loaded, and no request, page, or console errors. The input hash matches the canonical proof. Desktop light/dark screenshots are byte-identical, as are mobile light/dark screenshots.

The reproducible command remains:

```bash
export npm_config_cache=/tmp/onbrand-npm-cache
export PLAYWRIGHT_BROWSERS_PATH=/tmp/onbrand-playwright
npm --prefix tools/email_render_matrix install
npx --prefix tools/email_render_matrix playwright install chromium
node tools/email_render_matrix/render_matrix.cjs \
  --input campaign-output/rider-wellness-phase16-composition-preview/rider-wellness-phase16-composition-preview/html/rider-wellness-phase16-composition-preview-branded.html \
  --output docs/evals/render-matrix/rider-wellness-phase16-canonical
```

The output includes four committed screenshots, `render-report.json`, and the completed `visual-review.md`.

## Native Client Matrix

Use the exact branded HTML and packaged assets represented by the hash above. Record screenshots or exported evidence without editing the HTML between clients.

| Client surface | Target | Status | Required review |
| --- | --- | --- | --- |
| Gmail web | Current Chrome desktop | Pending | Width, fonts, image loading, buttons, spacing, footer, links |
| Outlook web | Current Chrome desktop | Pending | Table layout, images, buttons, footer, links |
| Outlook desktop | Current Windows Word engine | Pending | VML/background fallback, stacking, spacing, buttons, footer |
| Apple Mail | Current macOS | Pending | Fonts, responsive layout, images, dark mode, footer |
| Gmail mobile | Current iOS or Android | Pending | Mobile stacking, readable copy, tap targets, image crops |
| Apple Mail mobile | Current iOS | Pending | Mobile stacking, automatic dark-mode rewriting, tap targets |

For each client record:

- Client name and exact version
- Operating system and version
- Desktop or viewport dimensions when available
- Light or dark appearance
- Screenshot or hosted-service artifact
- Image, font, link, button, spacing, stacking, and footer result
- Reviewer, date, decision, and notes

## Decision Boundary

The automated and visual browser matrix passes. It does not close LIM-005 or certify Gmail, Outlook, Apple Mail, accessibility, legal compliance, or production deployment. LIM-005 remains open until representative native-client evidence is committed.
