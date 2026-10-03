from __future__ import annotations

import hashlib
import json
from typing import Any


class EvaluationError(ValueError):
    """Raised when live calibration evidence cannot be evaluated safely."""


def document_sha256(document: dict[str, Any]) -> str:
    canonical = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def evaluate_calibration(
    dataset: dict[str, Any],
    receipt: dict[str, Any],
    lexical_baseline: dict[str, Any],
    *,
    high_confidence: float = 0.8,
) -> dict[str, Any]:
    cases = [case for case in dataset.get("cases", []) if case.get("split") == "calibration"]
    expected_ids = {case["id"] for case in cases}
    records = receipt.get("records")
    if dataset.get("status") != "adjudicated":
        raise EvaluationError("Calibration requires an adjudicated dataset")
    if receipt.get("status") != "completed" or receipt.get("split") != "calibration":
        raise EvaluationError("Calibration receipt must be completed and calibration-only")
    if receipt.get("dataset_id") != dataset.get("dataset_id"):
        raise EvaluationError("Receipt dataset_id does not match the frozen dataset")
    if not isinstance(records, list) or {record.get("case_id") for record in records} != expected_ids:
        raise EvaluationError("Receipt records must match the complete calibration split exactly")
    if not 0 < high_confidence <= 1:
        raise EvaluationError("high_confidence must be within (0, 1]")

    by_id = {record["case_id"]: record for record in records}
    results = []
    for case in cases:
        record = by_id[case["id"]]
        if record.get("status") != "completed" or record.get("model") != "jev-1.13.0":
            raise EvaluationError(f"{case['id']} is not a completed pinned-model result")
        result = _evaluate_case(case, record, high_confidence)
        results.append(result)

    label_matches = sum(result["label_matched"] for result in results)
    action_matches = sum(result["action_matched"] for result in results)
    expected_positive = [result["expected_action"] != "allow" for result in results]
    predicted_positive = [result["predicted_action"] != "allow" for result in results]
    true_positive = sum(expected and predicted for expected, predicted in zip(expected_positive, predicted_positive))
    false_positive = sum(not expected and predicted for expected, predicted in zip(expected_positive, predicted_positive))
    true_negative = sum(not expected and not predicted for expected, predicted in zip(expected_positive, predicted_positive))
    false_negative = sum(expected and not predicted for expected, predicted in zip(expected_positive, predicted_positive))
    automated = sum(result["predicted_action"] != "review" for result in results)
    reviews = len(results) - automated
    baseline_calibration = lexical_baseline.get("split_metrics", {}).get("calibration", {})
    baseline_matched = baseline_calibration.get("matched")
    baseline_total = baseline_calibration.get("total")
    if baseline_total != len(results) or type(baseline_matched) is not int:
        raise EvaluationError("Lexical baseline does not match the calibration split")

    return {
        "schema_version": "1.0",
        "dataset_id": dataset["dataset_id"],
        "dataset_sha256": document_sha256(dataset),
        "receipt_sha256": document_sha256(receipt),
        "split": "calibration",
        "acceptance_evidence": False,
        "production_effect": "none",
        "policy": {
            "name": "jev-calibration-candidate-v1",
            "model": "jev-1.13.0",
            "high_confidence": high_confidence,
            "low_confidence_action": "review",
            "contradiction_action": "review",
            "approved_reuse_precedence": True,
        },
        "case_count": len(results),
        "metrics": {
            "semantic_label_agreement": _ratio(label_matches, len(results)),
            "semantic_label_matches": label_matches,
            "action_accuracy": _ratio(action_matches, len(results)),
            "action_matches": action_matches,
            "precision_intervention": _ratio(true_positive, true_positive + false_positive),
            "recall_intervention": _ratio(true_positive, true_positive + false_negative),
            "false_positive_rate": _ratio(false_positive, false_positive + true_negative),
            "false_negative_rate": _ratio(false_negative, false_negative + true_positive),
            "coverage": _ratio(automated, len(results)),
            "review_rate": _ratio(reviews, len(results)),
            "human_action_overrides": len(results) - action_matches,
            "confusion": {"tp": true_positive, "fp": false_positive, "tn": true_negative, "fn": false_negative},
        },
        "task_metrics": _task_metrics(results),
        "lexical_baseline_comparison": {
            "calibration_action_matches": baseline_matched,
            "jev_candidate_action_matches": action_matches,
            "match_delta": action_matches - baseline_matched,
            "lexical_accuracy": _ratio(baseline_matched, baseline_total),
            "jev_candidate_accuracy": _ratio(action_matches, len(results)),
        },
        "results": results,
        "conclusion": "Calibration signal only. Keep production disabled until the untouched holdout is evaluated and acceptance criteria pass.",
    }


def _evaluate_case(case: dict[str, Any], record: dict[str, Any], threshold: float) -> dict[str, Any]:
    answers = record["answers"]
    if case["task"] == "copy-similarity":
        primary = answers["copy_relation"]
        predicted_label = primary["choice"]
        expected_label = case["expected"]["semantic_relation"]
        contradiction = _copy_contradiction(predicted_label, answers)
        if primary["confidence"] < threshold or contradiction:
            predicted_action = "review"
        elif predicted_label == "equivalent":
            predicted_action = "allow" if case["state"].get("approved_reuse") else "block"
        else:
            predicted_action = "allow"
    else:
        primary = answers["claim_support_relation"]
        predicted_label = primary["choice"]
        expected_label = case["expected"]["support"]
        contradiction = _claim_contradiction(predicted_label, answers)
        if primary["confidence"] < threshold or contradiction:
            predicted_action = "review"
        else:
            predicted_action = {"supported": "allow", "unsupported": "block", "insufficient": "review"}[predicted_label]
    expected_action = case["expected"]["action"]
    reasons = []
    if primary["confidence"] < threshold:
        reasons.append("below-high-confidence-band")
    if contradiction:
        reasons.append("companion-answer-contradiction")
    return {
        "case_id": case["id"],
        "task": case["task"],
        "expected_label": expected_label,
        "predicted_label": predicted_label,
        "label_matched": predicted_label == expected_label,
        "expected_action": expected_action,
        "predicted_action": predicted_action,
        "action_matched": predicted_action == expected_action,
        "confidence": primary["confidence"],
        "routed_to_review": predicted_action == "review",
        "routing_reasons": reasons,
    }


def _copy_contradiction(label: str, answers: dict[str, Any]) -> bool:
    same = answers["same_core_message"]["noul"] >= 0.5
    adds = answers["second_adds_material_information"]["noul"] >= 0.5
    if label == "equivalent":
        return not same or adds
    return same or not adds


def _claim_contradiction(label: str, answers: dict[str, Any]) -> bool:
    certainty = answers["adds_unstated_certainty"]["noul"] >= 0.5
    scope = answers["adds_unstated_scope_timing_or_ranking"]["noul"] >= 0.5
    if label == "supported":
        return certainty or scope
    if label == "unsupported":
        return not (certainty or scope)
    return False


def _task_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    output = {}
    for task in sorted({result["task"] for result in results}):
        items = [result for result in results if result["task"] == task]
        output[task] = {
            "total": len(items),
            "label_matches": sum(item["label_matched"] for item in items),
            "label_agreement": _ratio(sum(item["label_matched"] for item in items), len(items)),
            "action_matches": sum(item["action_matched"] for item in items),
            "action_accuracy": _ratio(sum(item["action_matched"] for item in items), len(items)),
            "review_count": sum(item["routed_to_review"] for item in items),
        }
    return output


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 3) if denominator else 0.0
