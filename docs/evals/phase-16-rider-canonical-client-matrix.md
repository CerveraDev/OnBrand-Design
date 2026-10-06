# Phase 16 Rider Canonical Client Matrix

**Date:** 2026-10-05  
**Campaign:** Rider wellness canonical Composition Preview  
**Variant:** Branded  
**HTML SHA-256:** `b82bcc430806bd174e621f379ee4a5ef132bab59900e50c4af1188700580ea60`  
**Status:** Browser matrix passed; initial native background approaches failed; dual CSS/VML remediation is implemented and awaits delivery testing

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
| Gmail web | Owner-reviewed delivered message | Fail for v1 background transport | Foreground images and content arrived, but the sauna CSS background did not render |
| Outlook web | Current Chrome desktop | Pending | Table layout, images, buttons, footer, links |
| Outlook desktop | Outlook for Mac, macOS | Fail for v1 background transport | Core inline images, table layout, hierarchy, copy, and footer rendered, but the sauna CSS background did not render in the sent message; CSS-only background CIDs were exposed as attachments |
| Outlook desktop | Current Windows Word engine | Pending | VML/background fallback, stacking, spacing, buttons, footer |
| Apple Mail | Apple Mail, macOS | Pass in imported-message scope | Imported RFC 822 message rendered the complete layout and embedded imagery; delivery, dark mode, and responsive/mobile behavior were not tested |
| Gmail mobile | Current iOS or Android | Pending | Mobile stacking, readable copy, tap targets, image crops |
| Apple Mail mobile | Current iOS | Pending | Mobile stacking, automatic dark-mode rewriting, tap targets |

### Native Test Record

On 2026-10-05, a self-contained RFC 822 test message was generated from the exact canonical packaged HTML. The builder changed only local package references from `../images/<name>` to MIME Content-ID references and embedded the eight exact packaged image byte streams. The generated message SHA-256 was `37dec0351a6d80cc92041a164c97904d5a392102c470c20da6b5223873e22d88`.

The message was visually inspected after import into Apple Mail and Outlook for Mac. Outlook then resent the exact message from the owner-specified Cervera mailbox to the owner-specified recipient mailbox. Outlook recorded the sent item at 8:12 PM local time. The local `.eml` and receipt are intentionally ignored because they contain mailbox addresses; the reusable builder and its tests are committed.

The owner then reviewed the delivered message and reported that the CSS background was absent in Gmail and in the Outlook message body. This confirms that replacing CSS `background-image` URLs with CID references is not a valid cross-client transport, even though ordinary CID-backed `<img>` elements rendered.

The native-message builder was corrected for a second test candidate. It keeps foreground package images embedded by CID, restores CSS backgrounds to their original public HTTPS sources through the checksum-bound asset manifest, and blocks generation when a background lacks a public HTTPS source. The v2 candidate embeds six foreground images, restores two unique hosted backgrounds, contains no local package references or CSS CID backgrounds, and has SHA-256 `f2433c7a1668108cafb519e020629742e33dfd86309fb4013711093cc5945135`.

Before any resend, v2 was opened locally in Outlook for Mac. The sauna background still did not render. Two additional local-only experiments added the legacy HTML `background` attribute with an HTTPS source and then with an embedded CID source; neither rendered the background in Outlook for Mac. These experiments were not sent or committed as supported transport behavior.

The owner chose to preserve the live-text overlay instead of adopting a foreground-image/text-band fallback. The runtime now augments every meaningful non-repeating cover-style table background with a legacy `background` attribute and an Outlook-conditional VML `v:rect`/`v:fill`/`v:textbox` layer. QA accounts for every eligible background. The native-message builder restores the CSS, legacy, and VML references to one manifest-bound public HTTPS source while limiting CID conversion to foreground images. The actual wellness proof resolves to one eligible sauna background and one VML layer at the framed 560px content width. This is implemented structure, not yet delivered-client evidence.

A delegated Microsoft Graph raw-MIME helper now provides the markup-preserving delivery path for the next test. It validates the sender, recipient, HTML body, VML marker count, and absence of CID-backed backgrounds before sending; strips only the local draft header; requires explicit double opt-in for live delivery; and records a secret-free receipt. Entra application registration and delegated authorization remain required before the v5 candidate can be sent.

### Known-Good Beefree Gmail Reference

On 2026-10-06, the owner supplied the original downloaded Gmail message from a flawless Beefree test send. The private EML remains local and ignored; its redacted structural receipt is committed as `beefree-gmail-reference.json`.

The delivered Beefree message is one quoted-printable UTF-8 `text/html` part. It contains no MIME image attachments and no CID references. All 29 foreground images use public HTTPS URLs on Beefree or CloudFront hosts. Its cover backgrounds use the same scaffold pattern already supplied by the owner: inline `background-image: url('https://...')`, `background-repeat: no-repeat`, and `background-size: cover`. The message contains no legacy `background` attributes and no VML rectangles or fills.

This establishes that Gmail can render the scaffold as designed when the delivery path preserves the HTML and every asset is remotely hosted. It also narrows the first Gmail failure to the native v1 transport, which converted CSS backgrounds to CID references. The v5 background path already matches the known-good public-HTTPS pattern. Its remaining transport difference is that ordinary foreground images are embedded by CID because the generated campaign hero does not yet have a public hosted URL.

### Findings

- Outlook for Mac and Apple Mail on macOS preserved the main table layout, content hierarchy, live copy, footer, and core embedded imagery in light appearance during import review.
- The delivered v1 message failed to show the sauna background in both Gmail and Outlook. Outlook also exposed the CSS-referenced sauna and spacer resources as attachments.
- Gmail officially supports `background-image`, and the known-good Beefree delivery confirms that the unmodified scaffold pattern renders there with public HTTPS assets. The first delivered CID-in-CSS form failed because of its transport. Outlook for Mac also rejected public HTTPS CSS, legacy HTTPS, and legacy CID background forms during local import review. The next candidate keeps the Gmail-proven public-HTTPS CSS path and adds Outlook-only VML without flattening or moving the live text.
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

The automated and visual browser matrix passes, but the first delivered-message test and Outlook pre-send retests fail the static block's background-image requirement. LIM-005 remains open. The dual CSS/VML remediation is implemented and requires a new delivered-message test through a path that preserves the authored MIME and HTML. Outlook on Windows, VML fallback behavior, native dark mode, mobile clients, accessibility, legal compliance, and production deployment remain uncertified.
