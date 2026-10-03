# Phase 13 Jev Holdout Report

**Date:** 2026-10-03
**Model:** `jev-1.13.0`
**Split:** Untouched holdout, 9 cases
**Production effect:** None
**Decision:** Revise

## Result

The separately approved holdout run completed all nine requests using the question set and candidate policy committed before holdout generation. No thresholds, mappings, questions, or routing rules were changed after the receipt arrived.

| Metric | Holdout result |
| --- | ---: |
| Semantic-label agreement | 8/9 (88.9%) |
| Candidate action accuracy | 5/9 (55.6%) |
| Lexical-baseline action accuracy on the same split | 4/9 (44.4%) |
| Candidate improvement | +1 correct action |
| Intervention precision | 83.3% |
| Intervention recall | 83.3% |
| False-positive rate | 33.3% |
| False-negative rate | 16.7% |
| Automated coverage | 55.6% |
| Human-review rate | 44.4% |
| Human action overrides | 4 |
| False allows | 1 |

An intervention means `block` or `review`, rather than `allow`.

## Findings

Semantic classification was the strongest part of the pilot. Jev correctly identified all six copy relationships and two of three claim-support relationships. It detected the three low-overlap equivalent copy pairs that the lexical baseline missed: `sim-hold-001`, `sim-hold-003`, and `sim-hold-006`.

The locked action policy did not translate that signal reliably enough:

- `sim-hold-002` was correctly labeled `related-distinct` but incorrectly allowed instead of routed to editorial review. This is the single false allow and fails the locked keep rule.
- `sim-hold-001` and `sim-hold-006` were correctly labeled equivalent but routed to review rather than blocked because confidence or companion-answer contradictions overrode the primary label.
- `sim-hold-005` was correctly labeled distinct but conservatively routed to review because confidence was below `0.80`.
- All three claim-support actions were correct, including review routing for the insufficient-evidence case.

## Decision

**Revise.** Jev provides useful semantic evidence, but the current action policy yields only a small improvement over the lexical baseline, one false allow, and an excessive review rate. It must remain non-production and cannot block, allow, or rewrite campaign content.

The holdout is now spent. A revised policy may use these findings for diagnosis, but this nine-case set cannot establish the revised policy's performance. Any second pilot requires a new versioned dataset with a fresh holdout and a policy locked before evaluation.

## Evidence

- Holdout request batch: `docs/evals/requests/phase-13-jev-holdout.v1.json`
- Live holdout receipt: `docs/evals/receipts/phase-13-jev-holdout.live.v1.json`
- Machine-readable report: `docs/evals/phase-13-jev-holdout-report.v1.json`
- Locked policy: `docs/evals/config/phase-13-jev-candidate-policy.v1.json`
- Request batch SHA-256: `69e3370ed7707d4c4e8510556255a4c6d640e51e4f74fca6bcf45ee1486787ff`
- Live receipt SHA-256: `fb5257ac8cc291b1f3cb92243c8ce850ab83154259a9a80f08fc6aaa6484c9da`
- Report SHA-256: `a90225379e56706c34182dba2a38879edac0084141148dccfddba63fe66c7824`

The receipt contains typed answers, model and usage information, and hashes. It contains no API key or raw duplicated campaign state.
