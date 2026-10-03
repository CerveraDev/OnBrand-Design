# Phase 13 Semantic Decision Baseline

**Status:** Dataset version 1 adjudicated and frozen; baseline is diagnostic, not provider acceptance evidence

**Dataset:** `rider-semantic-decision-pilot-v1`

**Date:** 2026-10-03

## Purpose

Establish whether the existing Phase 10 lexical and claim-reference checks leave a measurable semantic decision gap before adding TypeSafe Jev or any other hosted decision provider.

## Dataset

- 26 de-identified cases with no agent contact data or credentials.
- 18 copy-similarity cases: 12 calibration and 6 holdout.
- 8 claim-support cases: 5 calibration and 3 holdout.
- Copy labels cover distinct, related-but-distinct, equivalent, and approved-refrain behavior.
- Claim labels cover supported, unsupported, and insufficient evidence.
- Labels are maintainer-seeded and remain provisional. The blind [review worksheet](phase-13-rider-copy-review-worksheet.md) omits expected labels so reviewers can judge independently.

The original [provisional dataset](data/phase-13-rider-copy-pairs.v1.json), [frozen adjudicated dataset](data/phase-13-rider-copy-pairs.v1.frozen.json), portable [schema](../../tools/semantic_eval/dataset.schema.json), and strict standard-library validator are versioned together. The provisional snapshot remains unchanged so completed reviews continue to validate against its exact hash.

## Baseline

The copy baseline uses the existing Phase 10 exact normalization and lexical score:

`max(token Jaccard, (word-bigram Jaccard + character-4-gram Jaccard) / 2)`

Scores at or above `0.65` request review and scores at or above `0.82` block unless approved reuse applies. The current claim baseline checks that a declared reference exists but does not determine whether that reference semantically supports the claim, so all claim-support cases route to review.

## Results

| Slice | Matched | Total | Exact action agreement |
| --- | ---: | ---: | ---: |
| All provisional cases | 14 | 26 | 53.8% |
| Copy similarity | 12 | 18 | 66.7% |
| Claim support | 2 | 8 | 25.0% |
| Calibration split | 10 | 17 | 58.8% |
| Holdout split | 4 | 9 | 44.4% |

Five provisionally equivalent, non-exempt copy pairs fall below the lexical warning threshold:

- `sim-cal-003`: membership continuity paraphrase, lexical score `0.005`.
- `sim-cal-009`: authority-language paraphrase, lexical score `0.118`.
- `sim-hold-001`: relocation/routine paraphrase, lexical score `0.048`.
- `sim-hold-003`: compact membership-continuity taglines, lexical score `0.000`.
- `sim-hold-006`: metaphorical/direct routine-continuity pair, lexical score `0.062`.

The complete machine-readable output is in [phase-13-lexical-baseline.v1.json](phase-13-lexical-baseline.v1.json).

## Interpretation

The seed set contains a real candidate gap for semantic evaluation: literal overlap alone cannot identify several paraphrases that appear to repeat the same campaign idea. The current claim gate correctly avoids pretending that reference presence proves support, but it cannot triage clearly supported and clearly unsupported examples.

These results do not establish Jev quality. They establish only that a semantic pilot has something meaningful to test. No threshold, provider question, or production blocking behavior should be tuned or approved until independent reviewers adjudicate the labels.

## Next Gate

Two blinded reviews agree fully on 21 of 26 cases and agree on the semantic label for 25 of 26. All five disagreements are now explicitly adjudicated in [phase-13-adjudication.v1.json](reviews/phase-13-adjudication.v1.json). Four equivalent, non-exempt copy pairs use the existing single-use policy and resolve to `block`. The headline/alt-text pair resolves to `related-distinct` and `allow` because the surfaces share campaign context but serve different functions.

The frozen baseline remains 14/26 exact action matches. Adjudication changes one semantic taxonomy label but no expected action, and holdout text is unchanged. The frozen machine report is [phase-13-lexical-baseline.frozen.v1.json](phase-13-lexical-baseline.frozen.v1.json).

1. Design atomic Jev questions using calibration cases only.
2. Lock the first question-set version before evaluating the untouched holdout.
3. Compare Jev with this baseline and record precision, recall, false positives, false negatives, review coverage, and overrides.

Review evidence: [Reviewer A](reviews/phase-13-reviewer-a.v1.json), [Reviewer B](reviews/phase-13-reviewer-b.v1.json), and [comparison](reviews/phase-13-review-comparison.v1.json).
