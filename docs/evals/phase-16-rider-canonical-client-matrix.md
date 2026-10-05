# Phase 16 Rider Canonical Client Matrix

**Date:** 2026-10-05  
**Campaign:** Rider wellness canonical Composition Preview  
**Variant:** Branded  
**HTML SHA-256:** `b82bcc430806bd174e621f379ee4a5ef132bab59900e50c4af1188700580ea60`  
**Status:** Browser visual review passed; automated Playwright report and native email-client evidence pending

## Browser Visual Review

The exact canonical packaged HTML was inspected in the Codex in-app browser at the ordinary desktop surface and through the committed 390px same-origin iframe harness.

| Surface | Width | Result | Findings |
| --- | ---: | --- | --- |
| Desktop browser | Wide app viewport | Pass | Centered email canvas, coherent hierarchy, readable copy, intact image credits, aligned CTAs, complete footer, and no visible overlaps or clipping. |
| Mobile browser harness | 390px | Pass | Header stacks logo above headline, copy remains readable, images resize cleanly, CTA content stacks vertically, footer columns collapse to one column, and no visible overlaps or horizontal clipping appear. |

The mobile harness is committed at `docs/evals/render-matrix/rider-wellness-phase16-canonical/mobile-review.html`. It loads the exact ignored campaign output and sizes its same-origin iframe to the rendered document height. It is browser-review evidence only.

The email contains an empty `prefers-color-scheme: dark` media query and otherwise uses a fixed palette. Browser dark preference and native-client color rewriting still require the formal matrix; no dark-mode pass is inferred from the light browser review.

## Automated Browser Matrix

The pinned Playwright package and Chromium 151 were installed successfully in isolated local caches. Launching Chromium from the managed Codex shell failed before page creation because macOS denied Chromium's Mach-port rendezvous registration:

`bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer: Permission denied (1100)`

This is an execution-environment restriction, not an email failure. No matrix report or screenshots were fabricated.

Run the exact matrix from an ordinary Terminal at the repository root:

```bash
export npm_config_cache="$PWD/.cache/npm"
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/playwright"
npm --prefix tools/email_render_matrix install
npx --prefix tools/email_render_matrix playwright install chromium
node tools/email_render_matrix/render_matrix.cjs \
  --input campaign-output/rider-wellness-phase16-composition-preview/rider-wellness-phase16-composition-preview/html/rider-wellness-phase16-composition-preview-branded.html \
  --output docs/evals/render-matrix/rider-wellness-phase16-canonical
```

Expected output is four screenshots, `render-report.json`, and `visual-review.md`. The report must pass before the automated browser matrix is marked complete.

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

The desktop and 390px browser visual reviews pass. They do not close LIM-005 or certify Gmail, Outlook, Apple Mail, accessibility, legal compliance, or production deployment. LIM-005 remains open until the automated report and representative native-client evidence are committed.
