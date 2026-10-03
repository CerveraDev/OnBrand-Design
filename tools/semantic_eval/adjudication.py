from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any

from .dataset import ACTIONS, RELATIONS, SUPPORT_LABELS, validate_dataset
from .reviews import compare_reviews, dataset_sha256, validate_review


class AdjudicationError(ValueError):
    """Raised when review disagreements are not explicitly and safely adjudicated."""


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def comparison_sha256(comparison: dict[str, Any]) -> str:
    canonical = json.dumps(comparison, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_adjudication(
    dataset: dict[str, Any],
    left: dict[str, Any],
    right: dict[str, Any],
    adjudication: object,
) -> dict[str, Any]:
    comparison = compare_reviews(dataset, left, right)
    if not isinstance(adjudication, dict):
        raise AdjudicationError("Adjudication must be a JSON object")
    keys = {
        "schema_version",
        "dataset_id",
        "source_dataset_sha256",
        "comparison_sha256",
        "adjudicator_id",
        "adjudicated_at",
        "status",
        "policy",
        "decisions",
    }
    _exact_keys(adjudication, keys, "adjudication")
    if adjudication["schema_version"] != "1.0" or adjudication["status"] != "complete":
        raise AdjudicationError("Adjudication schema_version must be 1.0 and status must be complete")
    if adjudication["dataset_id"] != dataset["dataset_id"]:
        raise AdjudicationError("Adjudication dataset_id does not match")
    if adjudication["source_dataset_sha256"] != dataset_sha256(dataset):
        raise AdjudicationError("Adjudication source_dataset_sha256 does not match")
    if adjudication["comparison_sha256"] != comparison_sha256(comparison):
        raise AdjudicationError("Adjudication comparison_sha256 does not match")
    for key in ("adjudicator_id", "policy"):
        if not isinstance(adjudication[key], str) or not adjudication[key].strip():
            raise AdjudicationError(f"adjudication.{key} must be non-empty")
    if not isinstance(adjudication["adjudicated_at"], str) or not DATE_RE.fullmatch(adjudication["adjudicated_at"]):
        raise AdjudicationError("adjudicated_at must use YYYY-MM-DD")

    case_by_id = {case["id"]: case for case in dataset["cases"]}
    required = {item["case_id"] for item in comparison["cases"] if item["adjudication_required"]}
    decisions = adjudication["decisions"]
    if not isinstance(decisions, list):
        raise AdjudicationError("adjudication.decisions must be an array")
    ids = [item.get("case_id") for item in decisions if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        raise AdjudicationError("Adjudication contains duplicate case IDs")
    if set(ids) != required:
        raise AdjudicationError(f"Adjudication coverage invalid; missing={sorted(required - set(ids))}, extra={sorted(set(ids) - required)}")
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            raise AdjudicationError(f"decisions[{index}] must be an object")
        _exact_keys(decision, {"case_id", "label", "action", "intentional_refrain", "rationale"}, f"decisions[{index}]")
        case = case_by_id[decision["case_id"]]
        if decision["action"] not in ACTIONS or not isinstance(decision["rationale"], str) or not decision["rationale"].strip():
            raise AdjudicationError(f"{decision['case_id']} has invalid action or rationale")
        if case["task"] == "copy-similarity":
            if decision["label"] not in RELATIONS or type(decision["intentional_refrain"]) is not bool:
                raise AdjudicationError(f"{decision['case_id']} has invalid copy decision")
        elif decision["label"] not in SUPPORT_LABELS or decision["intentional_refrain"] != "not-applicable":
            raise AdjudicationError(f"{decision['case_id']} has invalid claim decision")
    return {
        "dataset_id": dataset["dataset_id"],
        "decision_count": len(decisions),
        "required_count": len(required),
        "status": "complete",
    }


def freeze_dataset(
    dataset: dict[str, Any],
    left: dict[str, Any],
    right: dict[str, Any],
    adjudication: dict[str, Any],
) -> dict[str, Any]:
    validate_adjudication(dataset, left, right, adjudication)
    validate_review(left, dataset)
    validate_review(right, dataset)
    comparison = compare_reviews(dataset, left, right)
    left_by_id = {item["case_id"]: item for item in left["labels"]}
    right_by_id = {item["case_id"]: item for item in right["labels"]}
    compared = {item["case_id"]: item for item in comparison["cases"]}
    decisions = {item["case_id"]: item for item in adjudication["decisions"]}
    frozen = copy.deepcopy(dataset)
    frozen["status"] = "adjudicated"
    frozen["purpose"] = dataset["purpose"] + " Labels frozen after two blinded reviews and explicit disagreement adjudication."
    for case in frozen["cases"]:
        case_id = case["id"]
        if compared[case_id]["full_agreement"]:
            final = compared[case_id]["reviewer_a"]
        else:
            final = decisions[case_id]
        if case["task"] == "copy-similarity":
            case["expected"] = {
                "semantic_relation": final["label"],
                "action": final["action"],
                "intentional_refrain": final["intentional_refrain"],
            }
        else:
            case["expected"] = {"support": final["label"], "action": final["action"]}
        case["adjudication"] = {
            "status": "adjudicated",
            "reviewer_labels": [
                {"reviewer_id": left["reviewer_id"], **_decision_fields(left_by_id[case_id])},
                {"reviewer_id": right["reviewer_id"], **_decision_fields(right_by_id[case_id])},
            ],
        }
    validate_dataset(frozen)
    return frozen


def _decision_fields(value: dict[str, Any]) -> dict[str, Any]:
    return {key: value[key] for key in ("label", "action", "intentional_refrain")}


def _exact_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    missing = sorted(keys - set(value))
    unknown = sorted(set(value) - keys)
    if missing or unknown:
        raise AdjudicationError(f"{label} keys invalid; missing={missing}, unknown={unknown}")
