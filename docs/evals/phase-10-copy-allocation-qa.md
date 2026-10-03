# Phase 10 Copy Allocation Evaluation

Date: 2026-10-03. Internal non-production Rider validation; no campaign was sent or deployed.

The baseline below preserves the initial Phase 10 run. Current acceptance-gap follow-up evidence is recorded separately below.

## Contract And Regression Evidence

Run from the repository root:

```bash
python3 -m unittest discover -s tests
python3 -m tools.rider_campaign_runtime.cli projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-composition-preview.runtime.json
```

Full discovery passes 78 tests, including 17 dedicated [allocation tests](../../tests/test_rider_copy_allocation.py). Coverage includes clean plans, historical wellness/authority repetition, live/baked/alt/metadata overlap, exact/normalized and near-duplicate failures, warning-only similarity, approved refrains and protected strings, capped reuse, claim evidence, stale/unknown/ambiguous/unallocated owners, stale slot links, missing baked declarations, and unchanged approved copy. Runtime integration verifies allocation is retained in metadata/QA and a rejected copy change does not download assets or replace the prior passing HTML/ZIP. Existing build-mode, composition, grounded-image, static-lock, footer, roster, and packaging tests remain passing.

All four Rider runtime JSON fixtures pass structural and semantic allocation validation. The internal wellness fixture copy was revised to remove its historical repeated pattern; negative tests preserve that pattern as rejection evidence. User-approved campaign copy is never rewritten by the runtime.

## Live Composition Preview Pilot

The direct CLI build used the real manifest-backed remote assets and local approved generated hero. An earlier sandbox DNS failure and offline diagnostic package were superseded by this successful live run.

| Measure | Result |
| --- | --- |
| Build | `composition-preview`, `single`, branded |
| Composition plan | `rider-wellness-composition-preview` |
| Copy plan | `rider-wellness-composition-preview-copy-allocation` |
| Approved copy units | 23 |
| Copy checks | 26 passed |
| Similarity pairs >= 0.65 | 0 |
| Total package QA | 86 passed, 0 failed |
| Generated image workflow | 1 approved grounded hero |
| Packaged assets / unique image refs | 9 / 9 |
| ZIP regular files | 13 |
| ZIP size | 13,391,721 bytes |
| ZIP SHA-256 | `3f6ec61261a361e26ed90a964a6200a42611aaa4fbfa099d931e73ea2481620b` |

The ignored local result lives at `campaign-output/rider-wellness-composition-preview/rider-wellness-composition-preview/` with its sibling ZIP. ZIP hashes may vary on regeneration because ZIP timestamps are not normalized.

## Package Integrity Audit

A separate audit parsed metadata, QA, and the asset manifest and asserted:

- QA passes every recorded check and allocation summaries are identical in metadata and QA.
- Every asset's byte length and SHA-256 match the packaged file.
- Every extracted HTML image reference is relative, resolves inside the package, and exists; HTML contains no absolute local paths or `file://` references.
- ZIP CRC validation passes; its regular file names exactly equal the package file set, and every archived payload equals the corresponding package bytes.

Generated packages are ignored and excluded from the implementation commit. JSON/schema parse, fixture validation, local Markdown links, secret patterns, and diff whitespace are checked separately before commit.

Final checks passed: 29 JSON files parsed, all four runtime fixtures validated structurally and semantically, 187 local Markdown links resolved, high-confidence token/private-key patterns absent from tracked and nonignored files, and `git diff --check` clean. The final allocation validator output exactly matches the audited live pilot summary. Python `quick_validate.py` could not run because PyYAML is unavailable; Ruby YAML parsing plus equivalent naming, description, preserved invocation-policy, and placeholder checks passed. The published JSON Schema was parsed; fixture validation used the runtime's standard-library validator rather than the unavailable optional `jsonschema` library.

## Acceptance-Gap Follow-Up

On 2026-10-03, the full suite passed 79 tests, including 18 allocation tests. The new [responsive fallback fixture](../../tests/fixtures/rider-responsive-copy.html) uses two contextual render rules for one approved headline slot. Both branches retain the exact approved text, while allocation counts one logical occurrence with `single-use`, cap 1, and no dedupe exemption. Asset localization, package QA, metadata, and QA-report checks pass. Assigning the same text to a second logical owner still fails the repetition gate.

All 16 limitation entries and the new-entry template now have explicit dependency conditions. IDs, statuses, closure evidence, and original audit history are preserved. No runtime code or scoring behavior changed, so the original live pilot and its package audit remain valid; no rebuild was required. JSON/schema validation, Markdown links, whitespace, and secret-pattern checks were repeated for this follow-up.

## Scoring And Remaining Limits

For pairs with at least four words each, similarity is `max(token-set Jaccard, (word-bigram Jaccard + character-4-gram Jaccard) / 2)`. Warning threshold: 0.65. Blocking threshold: 0.82. Named exemptions can approve similarity overlap; deterministic occurrence caps remain enforced. Normalization strips HTML, lowercases, normalizes punctuation/whitespace, and removes URLs; character grams omit spaces.

The runtime validates declared text and evidence presence. OCR execution, claim extraction, source truth, undeclared image text, implicit protected scaffold/contact repetition, human editorial calibration, and client rendering remain external review tasks. LIM-003 is closed for the implemented campaign inventory contract; LIM-004 remains mitigated. Claude Code adapter parity is still Phase 11.
