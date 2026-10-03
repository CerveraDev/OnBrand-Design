# Phase 13 Independent Review Process

## Purpose

Collect two independent judgments for the provisional semantic evaluation cases before designing Jev questions, tuning thresholds, or treating the dataset as acceptance evidence.

The reviewer packet consists only of:

- [Blind worksheet](phase-13-rider-copy-review-worksheet.md)
- One reviewer-specific JSON response form from [reviews](reviews/)

Do not provide reviewers with `data/phase-13-rider-copy-pairs.v1.json`, the lexical baseline report, another reviewer's response, or proposed Jev questions before they finish.

## Reviewer Instructions

1. Read each worksheet case independently.
2. For copy-similarity cases, choose `distinct`, `related-distinct`, or `equivalent`.
3. For claim-support cases, choose `supported`, `unsupported`, or `insufficient`.
4. Choose the corresponding action: `allow`, `review`, or `block`.
5. For copy cases, set `intentional_refrain` to `true` only when the supplied context explicitly says reuse was approved. Claim cases retain `not-applicable`.
6. Add a short note when the decision depends on an ambiguity or boundary.
7. Change the form status from `draft` to `complete` and set `reviewed_at` in `YYYY-MM-DD` format.

Reviewers should not infer whether an LLM wrote the text and should not attempt legal or factual certification. The task is limited to the supplied semantic relationship and action policy.

## Validation

Validate each completed response from the repository root:

```bash
python3 -m tools.semantic_eval.review_dataset validate \
  docs/evals/data/phase-13-rider-copy-pairs.v1.json \
  path/to/completed-review.json
```

Validation requires:

- The exact dataset ID and SHA-256 fingerprint.
- A distinct nonempty reviewer ID.
- One valid response for every case.
- No duplicate, missing, or unknown case IDs.
- A completion date and `complete` status.

## Comparison

After both reviews validate:

```bash
python3 -m tools.semantic_eval.review_dataset compare \
  docs/evals/data/phase-13-rider-copy-pairs.v1.json \
  path/to/reviewer-a.json \
  path/to/reviewer-b.json \
  --output docs/evals/reviews/phase-13-review-comparison.v1.json
```

The comparison reports exact label agreement, full decision agreement, and every case requiring adjudication. It refuses two responses with the same reviewer identity.

## Adjudication Boundary

- Do not average disagreements or silently prefer the provisional seed label.
- Review disputed cases with both rationales visible.
- Record one final label and action through a separately reviewed adjudication change.
- Do not change holdout case text while resolving labels.
- Freeze dataset version 1 only after every case is adjudicated and the resulting evidence is committed.

Provider questions and thresholds may use calibration cases only. The holdout remains untouched until the first provider configuration is locked.
