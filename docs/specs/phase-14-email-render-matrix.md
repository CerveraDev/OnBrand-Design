# Phase 14: Email Render Matrix

**Status:** Tool and contract implemented; representative execution pending on an unrestricted browser host
**Target:** Rider public-release evidence
**Depends on:** Phase 5 HTML variants, Phase 6 package QA, and a passing representative campaign package

## Goal

Create repeatable browser-render evidence for representative OnBrand email HTML without claiming that Chromium reproduces Outlook, Gmail, Apple Mail, or any hosted email-testing service.

## Requirements

- RENDER-001: Render the exact packaged HTML and resolve its packaged relative assets.
- RENDER-002: Cover desktop and mobile viewports in both light and dark preferred-color modes.
- RENDER-003: Record input and screenshot SHA-256 hashes, viewport, color scheme, document dimensions, image counts, request failures, console errors, and horizontal overflow.
- RENDER-004: Fail automated browser-preview QA for broken images, page errors, request failures, empty documents, or horizontal viewport overflow.
- RENDER-005: Keep screenshots and the JSON report reproducible through one repository tool.
- RENDER-006: Generate a visual-review worksheet that distinguishes machine checks from human approval.
- RENDER-007: Never label browser previews as email-client certification.
- RENDER-008: Keep actual Outlook, Gmail, Apple Mail, mobile-client, and hosted-service snapshots as a separate manual or service-backed matrix.
- RENDER-009: Do not modify campaign HTML while rendering it.
- RENDER-010: Treat dark-mode screenshots as browser preference evidence only; client-specific color rewriting remains unverified.

## Initial Matrix

| ID | Viewport | Color scheme | Purpose |
| --- | --- | --- | --- |
| `desktop-light` | 1440 x 1200 | light | Wide browser preview |
| `mobile-light` | 390 x 844 | light | Narrow responsive preview |
| `desktop-dark` | 1440 x 1200 | dark | Wide preferred-color preview |
| `mobile-dark` | 390 x 844 | dark | Narrow preferred-color preview |

## Automated Pass Conditions

Every matrix entry must have:

- A non-empty rendered document.
- No horizontal viewport overflow.
- No broken `<img>` elements.
- No failed resource requests.
- No page or console errors.
- A non-empty screenshot with a recorded digest.

## Human Review

The reviewer inspects screenshots for coherent hierarchy, readable copy, image crops, whitespace, alignment, footer integrity, mobile stacking, and dark-mode regressions. A machine pass does not imply human approval.

## Non-Goals

- Pixel parity with any email client.
- Outlook Word-engine emulation.
- Gmail CSS sanitization emulation.
- Apple Mail or native mobile-client certification.
- Automatic aesthetic, brand, legal, accessibility, or copy approval.

## Evidence Gate

Phase 14 may mitigate LIM-005 after a representative matrix is committed. LIM-005 remains open until the supported client matrix and real client or hosted-service evidence are also recorded.
