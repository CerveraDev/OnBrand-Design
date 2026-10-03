# Phase 13 Jev Holdout Procedure

**Status:** Locked before holdout generation or execution

## Scope

Evaluate the nine untouched holdout cases from the frozen Rider dataset using question set `onbrand-jev-semantic-v1`, model `jev-1.13.0`, and candidate policy `onbrand-jev-candidate-v1`.

## Locked Rules

1. Generate requests only from records whose split is `holdout`.
2. Send only the state fields permitted by the locked question set.
3. Do not include expected labels, reviews, adjudication, contact information, or calibration outcomes.
4. Use the existing pinned model and question set without modification.
5. Interpret answers with the committed candidate policy without changing its `0.80` confidence boundary, action mappings, contradiction routing, or approved-reuse precedence.
6. Persist the provider receipt before loading expected holdout labels into the evaluator.
7. Report all required Phase 13 metrics and compare candidate actions with the frozen lexical baseline on the same holdout cases.
8. Do not rerun, tune, discard, or replace an unfavorable result. Any provider failure is recorded as failure evidence rather than silently retried.
9. Keep production effect set to `none` regardless of outcome.

## Decision Rule

- **Keep:** Holdout action accuracy improves over the lexical baseline, there are no false allows, review routing remains bounded, and all deterministic safeguards remain unchanged.
- **Revise:** Jev shows useful signal but introduces a false allow, fails to improve the baseline, or creates an excessive review burden.
- **Remove:** Jev materially underperforms the baseline, cannot produce stable typed evidence, or requires weakening deterministic or human safeguards.

Calibration performance is context, not part of the holdout score. Production integration requires a separate implementation decision after the report is committed.
