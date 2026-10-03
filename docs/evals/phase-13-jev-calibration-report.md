# Phase 13 Jev Calibration Report

**Date:** 2026-10-03
**Model:** `jev-1.13.0`
**Split:** Calibration only, 17 cases
**Production effect:** None
**Acceptance evidence:** No

## Result

The owner-approved live calibration completed all 17 requests. The candidate policy uses the question set's existing `0.80` high-confidence boundary, sends lower-confidence or internally contradictory answers to human review, preserves approved-reuse precedence, and does not alter deterministic QA.

| Metric | Result |
| --- | ---: |
| Semantic-label agreement | 13/17 (76.5%) |
| Candidate action accuracy | 16/17 (94.1%) |
| Lexical-baseline action accuracy on the same split | 10/17 (58.8%) |
| Candidate improvement on calibration | +6 correct actions |
| Intervention precision | 90.0% |
| Intervention recall | 100.0% |
| False-positive rate | 12.5% |
| False-negative rate | 0.0% |
| Automated coverage | 82.4% |
| Human-review rate | 17.6% |
| Human action overrides | 1 |

Here, an intervention means either `block` or `review`, rather than `allow`.

## Task Results

Copy similarity matched 9/12 semantic labels and 12/12 required actions. Jev correctly blocked the two calibration paraphrases with low lexical overlap, `sim-cal-003` and `sim-cal-009`, that the lexical baseline allowed. Two clearly distinct pairs were labeled `related-distinct`, but both still produced the correct `allow` action. The borderline `sim-cal-012` result fell below the high-confidence boundary and correctly routed to review.

Claim support matched 4/5 labels and 4/5 actions. The proximity case `claim-cal-004` was labeled unsupported rather than insufficient, but its lower confidence correctly routed it to review. `claim-cal-005` was the only action mismatch: Jev selected supported, but low confidence and a companion-answer contradiction conservatively routed an approved claim to review. This is a false positive, not a false allow.

## Decision

The calibration signal is strong enough to justify an untouched holdout evaluation. It is not sufficient to enable Jev in production. The candidate policy was evaluated on the same calibration cases used to select its interpretation, so promotion would overstate the evidence.

Before any production effect:

1. Lock the candidate policy and holdout evaluation procedure.
2. Generate and run the nine untouched holdout requests only after a separate explicit approval.
3. Compare holdout results with the frozen lexical baseline and all Phase 13 acceptance criteria.
4. Record a keep, revise, or remove decision.

## Evidence

- Machine-readable report: `docs/evals/phase-13-jev-calibration-report.v1.json`
- Live receipt: `docs/evals/receipts/phase-13-jev-calibration.live.v1.json`
- Frozen dataset SHA-256: `38df0b4d55c489fa06e4dea1b20ea5ce5b2d90e5969a65f5652c93343e6e8af7`
- Live receipt SHA-256: `032b20c0e77ea9c72cdfcb091c49e0f8095686ccbb8d747ef68b711d673f3c4a`

The receipt stores typed answers, usage, model ID, and hashes. It contains no API key and no raw duplicated campaign state.

The candidate interpretation is locked separately in `docs/evals/config/phase-13-jev-candidate-policy.v1.json` with canonical SHA-256 `bbb7fceaaddc15ed47fee0d177046aa397ceb46dcc8fe5556cce3283e17990fb` before holdout generation or execution.
