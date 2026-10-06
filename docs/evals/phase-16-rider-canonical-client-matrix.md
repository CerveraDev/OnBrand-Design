# Phase 16 Rider Canonical Client Matrix

**Date:** 2026-10-05  
**Campaign:** Rider wellness canonical Composition Preview  
**Variant:** Branded  
**HTML SHA-256:** `b82bcc430806bd174e621f379ee4a5ef132bab59900e50c4af1188700580ea60`  
**Status:** Browser matrix passed; Outlook for Mac and Apple Mail macOS checks passed within the tested scope; Gmail and broader native-client coverage remain pending

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
| Gmail web | Actual recipient mailbox in current Chrome desktop | Pending | The open Gmail session is a different account and exact-subject search returned no match; test the delivered message in the recipient mailbox |
| Outlook web | Current Chrome desktop | Pending | Table layout, images, buttons, footer, links |
| Outlook desktop | Outlook for Mac, macOS | Pass with finding | Core inline images, table layout, hierarchy, copy, and footer rendered; CSS-only background CIDs for the sauna and spacer were also exposed as attachments |
| Outlook desktop | Current Windows Word engine | Pending | VML/background fallback, stacking, spacing, buttons, footer |
| Apple Mail | Apple Mail, macOS | Pass in imported-message scope | Imported RFC 822 message rendered the complete layout and embedded imagery; delivery, dark mode, and responsive/mobile behavior were not tested |
| Gmail mobile | Current iOS or Android | Pending | Mobile stacking, readable copy, tap targets, image crops |
| Apple Mail mobile | Current iOS | Pending | Mobile stacking, automatic dark-mode rewriting, tap targets |

### Native Test Record

On 2026-10-05, a self-contained RFC 822 test message was generated from the exact canonical packaged HTML. The builder changed only local package references from `../images/<name>` to MIME Content-ID references and embedded the eight exact packaged image byte streams. The generated message SHA-256 was `37dec0351a6d80cc92041a164c97904d5a392102c470c20da6b5223873e22d88`.

The message was visually inspected after import into Apple Mail and Outlook for Mac. Outlook then resent the exact message from the owner-specified Cervera mailbox to the owner-specified recipient mailbox. Outlook recorded the sent item at 8:12 PM local time. The local `.eml` and receipt are intentionally ignored because they contain mailbox addresses; the reusable builder and its tests are committed.

The current Chrome Gmail session belongs to a different account than the recipient. An exact-subject search returned no matching message, so Gmail rendering is not claimed and no duplicate message was sent.

### Findings

- Outlook for Mac and Apple Mail on macOS preserved the main table layout, content hierarchy, live copy, footer, and core embedded imagery in light appearance.
- Outlook for Mac exposed the CSS-referenced sauna background and one-pixel spacer as attachments even though the visible email rendered. This is a transport/client presentation defect to address before production-send certification.
- No native dark-mode, Windows Outlook Word-engine, webmail sanitizer, mobile-client, link-click, accessibility, or deployment-platform result is inferred from these checks.

For each client record:

- Client name and exact version
- Operating system and version
- Desktop or viewport dimensions when available
- Light or dark appearance
- Screenshot or hosted-service artifact
- Image, font, link, button, spacing, stacking, and footer result
- Reviewer, date, decision, and notes

## Decision Boundary

The automated and visual browser matrix passes, and the first macOS native-client evidence is now recorded. This narrows but does not close LIM-005: Gmail, Outlook on Windows, native dark mode, mobile clients, accessibility, legal compliance, and production deployment remain uncertified, and the Outlook attachment finding remains open.
