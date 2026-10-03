from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .dataset import ACTIONS, RELATIONS, SUPPORT_LABELS, validate_dataset


class ReviewError(ValueError):
    """Raised when a blinded semantic evaluation review is invalid."""


REVIEW_SCHEMA_VERSION = "1.0"
REVIEW_STATUSES = {"draft", "complete"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def dataset_sha256(dataset: dict[str, Any]) -> str:
    validate_dataset(dataset)
    canonical = json.dumps(dataset, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def create_review_template(dataset: dict[str, Any], reviewer_id: str) -> dict[str, Any]:
    validate_dataset(dataset)
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ReviewError("reviewer_id must be non-empty")
    labels = []
    for case in dataset["cases"]:
        labels.append(
            {
                "case_id": case["id"],
                "label": None,
                "action": None,
                "intentional_refrain": None if case["task"] == "copy-similarity" else "not-applicable",
                "notes": "",
            }
        )
    return {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "dataset_id": dataset["dataset_id"],
        "dataset_sha256": dataset_sha256(dataset),
        "reviewer_id": reviewer_id,
        "reviewed_at": None,
        "status": "draft",
        "instructions": "Complete independently without consulting provisional expected labels. Set one label and action per case, then change status to complete and add reviewed_at.",
        "labels": labels,
    }


def validate_review(review: object, dataset: dict[str, Any], *, require_complete: bool = True) -> dict[str, Any]:
    validate_dataset(dataset)
    if not isinstance(review, dict):
        raise ReviewError("Review must be a JSON object")
    expected_keys = {
        "schema_version",
        "dataset_id",
        "dataset_sha256",
        "reviewer_id",
        "reviewed_at",
        "status",
        "instructions",
        "labels",
    }
    _exact_keys(review, expected_keys, "review")
    if review["schema_version"] != REVIEW_SCHEMA_VERSION:
        raise ReviewError(f"review.schema_version must be {REVIEW_SCHEMA_VERSION}")
    if review["dataset_id"] != dataset["dataset_id"]:
        raise ReviewError("Review dataset_id does not match the dataset")
    if review["dataset_sha256"] != dataset_sha256(dataset):
        raise ReviewError("Review dataset_sha256 does not match the exact dataset")
    reviewer_id = review["reviewer_id"]
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ReviewError("reviewer_id must be non-empty")
    status = review["status"]
    if status not in REVIEW_STATUSES:
        raise ReviewError(f"Unsupported review status: {status}")
    if require_complete and status != "complete":
        raise ReviewError("Review status must be complete")
    reviewed_at = review["reviewed_at"]
    if status == "complete" and (not isinstance(reviewed_at, str) or not DATE_RE.fullmatch(reviewed_at)):
        raise ReviewError("Complete reviews require reviewed_at in YYYY-MM-DD format")
    if status == "draft" and reviewed_at is not None:
        raise ReviewError("Draft reviews must leave reviewed_at null")
    if not isinstance(review["instructions"], str) or not review["instructions"]:
        raise ReviewError("Review instructions must be non-empty")

    cases = {case["id"]: case for case in dataset["cases"]}
    labels = review["labels"]
    if not isinstance(labels, list):
        raise ReviewError("review.labels must be an array")
    ids = [item.get("case_id") for item in labels if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        raise ReviewError("Review contains duplicate case IDs")
    missing = sorted(set(cases) - set(ids))
    unknown = sorted(set(ids) - set(cases))
    if missing or unknown:
        raise ReviewError(f"Review case coverage invalid; missing={missing}, unknown={unknown}")

    completed = 0
    for index, item in enumerate(labels):
        if not isinstance(item, dict):
            raise ReviewError(f"review.labels[{index}] must be an object")
        _exact_keys(item, {"case_id", "label", "action", "intentional_refrain", "notes"}, f"review.labels[{index}]")
        case_id = item["case_id"]
        case = cases[case_id]
        if not isinstance(item["notes"], str):
            raise ReviewError(f"{case_id} notes must be text")
        if status == "draft" and item["label"] is None and item["action"] is None:
            continue
        completed += 1
        if case["task"] == "copy-similarity":
            if item["label"] not in RELATIONS:
                raise ReviewError(f"{case_id} copy label is unsupported")
            if type(item["intentional_refrain"]) is not bool:
                raise ReviewError(f"{case_id} intentional_refrain must be boolean")
        else:
            if item["label"] not in SUPPORT_LABELS:
                raise ReviewError(f"{case_id} claim label is unsupported")
            if item["intentional_refrain"] != "not-applicable":
                raise ReviewError(f"{case_id} intentional_refrain must be not-applicable")
        if item["action"] not in ACTIONS:
            raise ReviewError(f"{case_id} action is unsupported")
    if status == "complete" and completed != len(cases):
        raise ReviewError("Complete reviews require labels for every case")
    return {
        "reviewer_id": reviewer_id,
        "status": status,
        "case_count": len(cases),
        "completed_count": completed,
        "dataset_sha256": review["dataset_sha256"],
    }


def compare_reviews(dataset: dict[str, Any], left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_summary = validate_review(left, dataset, require_complete=True)
    right_summary = validate_review(right, dataset, require_complete=True)
    if left_summary["reviewer_id"].strip().lower() == right_summary["reviewer_id"].strip().lower():
        raise ReviewError("Independent reviews require different reviewer IDs")
    left_by_id = {item["case_id"]: item for item in left["labels"]}
    right_by_id = {item["case_id"]: item for item in right["labels"]}
    cases = []
    agreement_count = 0
    label_agreement_count = 0
    for case in dataset["cases"]:
        case_id = case["id"]
        left_label = _decision_fields(left_by_id[case_id])
        right_label = _decision_fields(right_by_id[case_id])
        label_agreement = left_label["label"] == right_label["label"]
        full_agreement = left_label == right_label
        label_agreement_count += int(label_agreement)
        agreement_count += int(full_agreement)
        cases.append(
            {
                "case_id": case_id,
                "task": case["task"],
                "split": case["split"],
                "label_agreement": label_agreement,
                "full_agreement": full_agreement,
                "reviewer_a": left_label,
                "reviewer_b": right_label,
                "adjudication_required": not full_agreement,
            }
        )
    total = len(cases)
    return {
        "schema_version": "1.0",
        "dataset_id": dataset["dataset_id"],
        "dataset_sha256": dataset_sha256(dataset),
        "reviewers": [left_summary["reviewer_id"], right_summary["reviewer_id"]],
        "case_count": total,
        "label_agreement_count": label_agreement_count,
        "label_agreement_rate": round(label_agreement_count / total, 3),
        "full_agreement_count": agreement_count,
        "full_agreement_rate": round(agreement_count / total, 3),
        "adjudication_required_count": total - agreement_count,
        "cases": cases,
    }


def _decision_fields(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": item["label"],
        "action": item["action"],
        "intentional_refrain": item["intentional_refrain"],
    }


def _exact_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    missing = sorted(keys - set(value))
    unknown = sorted(set(value) - keys)
    if missing or unknown:
        raise ReviewError(f"{label} keys invalid; missing={missing}, unknown={unknown}")
