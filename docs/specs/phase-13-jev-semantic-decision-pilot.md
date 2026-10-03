# Phase 13: Jev Semantic Decision Pilot

**Status:** Live calibration complete; untouched holdout and acceptance decision pending
**Target:** Post-Phase 11 refinement; independent of deferred Phase 12
**Depends on:** Phase 10 copy allocation QA, versioned runtime contracts, and a labeled Rider evaluation set

## Goal

Measure whether TypeSafe Jev adds reliable semantic judgment to OnBrand Design without replacing deterministic validation, specialized visual measurements, or human approval.

The first pilot evaluates semantic copy similarity and claim-support triage. Later pilots may evaluate asset relevance, composition-option ranking, alt-text quality, and compliance-risk routing only when the first pilot demonstrates measurable value.

## Architecture Decision

Jev is an optional decision provider behind the shared Python runtime. Codex, Claude Code, and CLI adapters consume the same recorded decision result. No platform adapter implements its own Jev prompts or thresholds.

The decision sequence is:

1. Run existing deterministic gates.
2. Compute deterministic or specialist measurements.
3. Send the minimum necessary text/JSON state to Jev for atomic semantic questions.
4. Combine results, thresholds, and hard gates in ordinary code.
5. Route uncertain, sensitive, or high-risk findings to a human.

Deterministic failures cannot be overridden by Jev. Jev unavailability must not corrupt or partially replace the last valid package.

## Initial Pilot

Evaluate pairs of approved copy units that are not already resolved by exact or normalized matching.

Candidate questions:

- Noul: Do these units communicate substantially the same campaign claim?
- Noul: Is the repetition an intentional branded refrain supported by the supplied approval record?
- Score: How much new information does the second unit add, using descriptive levels from fully distinct to effectively duplicated?
- Noul: Does the cited source appear to support the declared claim?

The runtime, not Jev, decides whether a probability or score produces an informational finding, warning, block, or human-review requirement.

## Requirements

- JEV-001: Keep Phase 10 exact, normalized, lexical, ownership, occurrence, and claim-reference checks authoritative.
- JEV-002: Gate all provider calls behind an explicit configuration flag that defaults to disabled.
- JEV-003: Provide deterministic fallback behavior when credentials, network access, quota, or the provider are unavailable.
- JEV-004: Pin the evaluated model version for calibrated runs; aliases are not sufficient acceptance evidence.
- JEV-005: Version every state schema, question, criterion, threshold, and aggregation rule.
- JEV-006: Record model ID, input hash, question-set version, probabilities, confidence, decision, and human override without storing secrets.
- JEV-007: Minimize provider state and exclude credentials and unnecessary personal or agent-contact data.
- JEV-008: Treat confidence as uncertainty evidence, not correctness or compliance proof.
- JEV-009: Keep visual similarity outside Jev. Image, OCR, render, accessibility-math, and pixel measurements must come from specialized tools before any semantic routing.
- JEV-010: Preserve human approval for brand, legal, fair-housing, financial, likeness, generated-image, and client-facing visual judgments.
- JEV-011: Use one canonical provider integration through the shared runtime so Codex, Claude Code, and CLI remain behaviorally aligned.
- JEV-012: Make the provider removable without changing campaign schemas, package formats, or deterministic QA contracts.

## Evaluation Dataset

Build a versioned, de-identified Rider set containing:

- Distinct copy pairs.
- Exact and normalized duplicates.
- Semantic paraphrases with low lexical overlap.
- Approved refrains.
- Repeated authority language.
- Supported and unsupported declared claims.
- Borderline cases labeled independently by at least two reviewers where practical.

Keep training/calibration examples separate from the final holdout set.

The provisional version 1 Rider dataset, JSON Schema, deterministic validator, blind review worksheet, and lexical baseline report are committed. Seed labels are not acceptance evidence until independent review and adjudication are recorded.

## Acceptance Criteria

- Demonstrate improvement over the Phase 10 lexical baseline on the held-out semantic cases.
- Report precision, recall, false-positive rate, false-negative rate, coverage, review rate, and reviewer overrides.
- Establish documented review bands rather than relying on one opaque threshold.
- Confirm deterministic failures remain unchanged with Jev enabled or disabled.
- Confirm provider failure produces the documented fallback and preserves the last passing package.
- Confirm parity across Codex, Claude Code, and CLI using one recorded provider-response fixture before any live-provider parity claim.
- Obtain owner approval for data handling before sending private project material to the hosted API.

No production blocking decision may depend on Jev until these criteria pass and the limitation register is updated with committed evidence.

## Non-Goals

- Generating copy, images, HTML, or campaign strategy.
- Direct image, audio, video, pixel, logo, face, or rendering analysis.
- Numeric calculations, contrast ratios, checksums, schema validation, or package validation.
- Legal, fair-housing, financial, factual, or accessibility certification.
- Distribution-profile security or access control.
- Replacing Composition Preview or human approval.

## Privacy And Operations

- Read `TYPESAFE_API_KEY` from the environment; never commit or package it.
- Keep the provider disabled for consumers who do not configure it.
- Document which fields leave the local runtime and redact unnecessary personal data.
- Review TypeSafe terms, retention, service availability, and any required data-processing agreement before production use.
- Store compact decision receipts and hashes, not raw duplicated campaign state, unless an approved evidence policy requires it.

## Rollout

1. Offline question and rubric design using committed fixtures.
2. Recorded-response adapter and failure-mode tests without network access.
3. Owner-approved live evaluation against the labeled Rider set.
4. Measurement report and keep/remove decision.
5. Optional expansion to asset relevance and claim support.
6. Visual-evidence routing only after specialized image-scoring work under LIM-001 and LIM-014 exists.

## Rollback

Disabling the feature flag restores the existing Phase 10 behavior. Removing the provider adapter must leave campaign inputs, generated packages, QA reports, and platform adapters valid.

## Current Evidence

- [Provisional dataset](../evals/data/phase-13-rider-copy-pairs.v1.json)
- [Blind review worksheet](../evals/phase-13-rider-copy-review-worksheet.md)
- [Independent review process](../evals/phase-13-review-process.md)
- [Baseline evaluation](../evals/phase-13-semantic-decision-baseline.md)
- [Machine-readable baseline](../evals/phase-13-lexical-baseline.v1.json)
- [Dataset validator tests](../../tests/test_semantic_eval.py)
- [Reviewer response schema](../../tools/semantic_eval/review.schema.json)
- [Reviewer comparison](../evals/reviews/phase-13-review-comparison.v1.json)
- [Adjudication record](../evals/reviews/phase-13-adjudication.v1.json)
- [Frozen dataset](../evals/data/phase-13-rider-copy-pairs.v1.frozen.json)
- [Calibration-locked question set](../evals/config/phase-13-jev-questions.v1.json)
- [Calibration request batch](../evals/requests/phase-13-jev-calibration.v1.json)
- [Disabled provider receipt](../evals/receipts/phase-13-jev-calibration.disabled.v1.json)
- [Live calibration receipt](../evals/receipts/phase-13-jev-calibration.live.v1.json)
- [Calibration report](../evals/phase-13-jev-calibration-report.md)
- [Machine-readable calibration report](../evals/phase-13-jev-calibration-report.v1.json)
- [Receipt schema](../../tools/semantic_eval/receipt.schema.json)
