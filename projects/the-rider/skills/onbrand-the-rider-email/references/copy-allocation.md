# Copy Allocation QA

Every runtime campaign JSON must include an approved `copy_allocation` object. This is the Phase 10 contract that keeps approved copy from being reused accidentally across live HTML, baked image text, alt text, and campaign metadata.

The same versioned JSON and Python CLI work in Codex, a normal shell, or a caller in Claude Code. This portability does not claim a tested Claude Code skill adapter; Phase 11 owns that parity evidence.

## What To Allocate

Create one `content_units[]` entry for each approved campaign copy unit:

- Subject line and preview text as `metadata`.
- Live scaffold slot copy as `live-html`.
- Image alt text as `alt-text`.
- Text intentionally baked into a generated or edited image as `baked-image-text`.
- Legal, footer, or required-name strings only when they need an explicit exemption record. Included locked static blocks are added to the inventory automatically.

Do not allocate deterministic footer/contact/legal strings as campaign creative copy. They are governed by the footer and legal contracts unless a campaign-level exemption is needed.

## Required Fields

Each content unit needs:

- Stable `id`.
- Exact `text` as approved by the user or source.
- `content_role`, such as `subject`, `hero-headline`, `body-copy`, `cta`, `image-alt`, or `baked-image-heading`.
- `source`, such as `user-approved`, `concept-development-approved`, `approved image alt text`, or `locked static block`.
- `approval_status: "approved"`.
- An `owner` with a single channel and owner slot.
- `reuse_policy`, normally `single-use`.
- `max_occurrences`, normally `1`.
- `claim_policy`, normally `none`.

The runtime computes normalized fingerprints; authors should not hand-edit fingerprints.

The plan requires `version: "1.0"`, stable `plan_id`, `status: "approved"`, `approved_by`, and `approved_at`. Optional `slot_allocation[]` entries must agree with their content unit's module, slot, and channel. Unknown, duplicate, stale, or unallocated owners fail before rendering. Every included static block contributes one deterministic locked-copy unit. An optional explicit static declaration must reference an included block and exactly match all visible locked text; partial declarations fail. Legal/footer declarations must match the named scaffold footer. Standard footer/contact/legal rendering remains governed by its existing deterministic contract.

Known desktop/mobile fallback branches may use multiple contextual rendering rules for the same logical slot. Allocate that slot once with `single-use` and `max_occurrences: 1`; the deterministic slot mapping accounts for responsive duplication without a campaign dedupe exemption. A second logical owner is still a separate occurrence and remains subject to the same repetition gate.

## Owner Channels

- `metadata`: use `metadata_field` set to `subject` or `preview_text`.
- `live-html`: use `module_id` and `slot`.
- `alt-text`: use `module_id` and `slot`; include `image_workflow_id` when the image slot uses generated/edited imagery.
- `baked-image-text`: use `image_workflow_id` and add `declared_text_source` as `ocr` or `creator-declared`. The matching `image_workflow` item must use `prompt_record.text_policy: "baked-approved"`.
- `static`: use `static_block_id`.
- `legal` and `footer`: use the named scaffold footer `module_id` and optional string/slot identifier, only for explicit, narrow exemptions of locked text.

## Repeats And Exemptions

The runtime blocks repeated normalized copy and restricted phrases above their approved occurrence caps. Reuse policies other than `single-use` require a named exemption; restricted phrase caps above one also require an exemption. Exemptions never waive the approved cap. Near-duplicate similarity exemptions must name exactly two affected units or the exact pair `left-id+right-id`; a longer list does not exempt every pair within it.

An exemption must include:

- `reason`
- narrow `scope`
- `applies_to`
- `approved_by`
- `approved_at`
- optional `evidence`

Use this for intentional refrains, legal text, locked static brand messages, or required names. Do not use broad exemptions to hide duplicated campaign copy.

## Claim Evidence

Use `claim_policy: "requires-evidence"` when copy makes a factual, authority, pricing, availability, membership, date, or location claim that needs support. Add `claim_references` with the approved source labels or URLs. The runtime blocks required-evidence claims without references.

The runtime does not certify legal compliance. It only enforces that declared claim evidence exists before packaging.

## Near-Duplicate Scoring

Phase 10 reports transparent similarity signals instead of opaque AI-quality scores:

- normalized exact match
- restricted phrase occurrence count
- token overlap
- word bigram overlap
- character 4-gram overlap

Scores at or above `0.65` are reported as review signals. Scores at or above `0.82` are blocking unless an explicit exemption exists.

For pairs with at least four words each, the score is `max(token-set Jaccard, (word-bigram Jaccard + character-4-gram Jaccard) / 2)`. Character grams omit spaces. Normalization strips HTML, lowercases, normalizes punctuation/whitespace, and removes URLs. This heuristic can miss paraphrases or flag legitimate overlap; named findings are available for review. It does not certify prose quality.

## Authoring Rule

The skill may propose cleaner allocation or copy options, but the runtime must never silently rewrite approved user copy. If a user supplies finished copy, preserve it exactly in the target slot or return a reviewable proposed revision.
