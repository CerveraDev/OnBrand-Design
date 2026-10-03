from __future__ import annotations

import hashlib
import json
from typing import Any

from .dataset import validate_dataset


class QuestionSetError(ValueError):
    """Raised when a Jev pilot question set or request batch is unsafe."""


QUESTION_SET_VERSION = "1.0"
QUESTION_TYPES = {"choice", "noul", "score"}


def validate_question_set(question_set: object) -> dict[str, Any]:
    if not isinstance(question_set, dict):
        raise QuestionSetError("Question set must be a JSON object")
    keys = {
        "schema_version",
        "question_set_id",
        "status",
        "model",
        "purpose",
        "privacy",
        "confidence_routing",
        "tasks",
    }
    _exact_keys(question_set, keys, "question_set")
    if question_set["schema_version"] != QUESTION_SET_VERSION:
        raise QuestionSetError(f"schema_version must be {QUESTION_SET_VERSION}")
    for key in ("question_set_id", "purpose"):
        _text(question_set, key, "question_set")
    if question_set["status"] != "calibration-locked":
        raise QuestionSetError("question_set.status must be calibration-locked")
    model = _text(question_set, "model", "question_set")
    if model in {"jev-latest", "jev-preview"} or not model.startswith("jev-"):
        raise QuestionSetError("Pilot model must use a pinned Jev version, not an alias")
    privacy = question_set["privacy"]
    if not isinstance(privacy, dict):
        raise QuestionSetError("privacy must be an object")
    _exact_keys(privacy, {"allowed_state_fields", "forbidden_state_fields", "personal_contact_data"}, "privacy")
    for key in ("allowed_state_fields", "forbidden_state_fields"):
        values = privacy[key]
        if not isinstance(values, list) or not values or any(not isinstance(item, str) or not item for item in values):
            raise QuestionSetError(f"privacy.{key} must be a non-empty string array")
    if privacy["personal_contact_data"] != "forbidden":
        raise QuestionSetError("personal contact data must be forbidden")
    routing = question_set["confidence_routing"]
    if not isinstance(routing, dict):
        raise QuestionSetError("confidence_routing must be an object")
    _exact_keys(routing, {"high", "medium", "low", "production_effect"}, "confidence_routing")
    for key in ("high", "medium", "low"):
        value = routing[key]
        if type(value) not in {int, float} or not 0 <= value <= 1:
            raise QuestionSetError(f"confidence_routing.{key} must be between 0 and 1")
    if not routing["high"] > routing["medium"] > routing["low"]:
        raise QuestionSetError("confidence thresholds must descend high > medium > low")
    if routing["production_effect"] != "none":
        raise QuestionSetError("Pilot question sets cannot have production effect")

    tasks = question_set["tasks"]
    if not isinstance(tasks, dict) or set(tasks) != {"copy-similarity", "claim-support"}:
        raise QuestionSetError("tasks must define copy-similarity and claim-support")
    question_ids: set[str] = set()
    for task, config in tasks.items():
        _validate_task(task, config, question_ids)
    return {
        "question_set_id": question_set["question_set_id"],
        "model": model,
        "task_count": len(tasks),
        "question_count": len(question_ids),
        "status": question_set["status"],
    }


def question_set_sha256(question_set: dict[str, Any]) -> str:
    validate_question_set(question_set)
    canonical = json.dumps(question_set, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_request_batch(
    dataset: dict[str, Any],
    question_set: dict[str, Any],
    *,
    split: str = "calibration",
    allow_holdout: bool = False,
) -> dict[str, Any]:
    dataset_summary = validate_dataset(dataset)
    question_summary = validate_question_set(question_set)
    if dataset["status"] != "adjudicated":
        raise QuestionSetError("Jev request batches require an adjudicated frozen dataset")
    if split not in {"calibration", "holdout"}:
        raise QuestionSetError("split must be calibration or holdout")
    if split == "holdout" and not allow_holdout:
        raise QuestionSetError("Holdout request generation requires explicit allow_holdout=True")

    records = []
    allowed_fields = set(question_set["privacy"]["allowed_state_fields"])
    forbidden_fields = set(question_set["privacy"]["forbidden_state_fields"])
    for case in dataset["cases"]:
        if case["split"] != split:
            continue
        task = case["task"]
        task_config = question_set["tasks"][task]
        state_fields = task_config["state_fields"]
        state = {field: case["state"][field] for field in state_fields}
        if set(state) - allowed_fields or set(state) & forbidden_fields:
            raise QuestionSetError(f"{case['id']} state violates privacy field policy")
        serialized = json.dumps(state, sort_keys=True)
        if any(token in serialized for token in ('"expected"', 'reviewer_labels', 'adjudication')):
            raise QuestionSetError(f"{case['id']} request leaks evaluation labels")
        records.append(
            {
                "case_id": case["id"],
                "task": task,
                "split": split,
                "policy_context": {"approved_reuse": case["state"].get("approved_reuse", False)},
                "request": {
                    "model": question_set["model"],
                    "state": state,
                    "questions": task_config["questions"],
                },
            }
        )
    if not records:
        raise QuestionSetError(f"No {split} cases found")
    return {
        "schema_version": "1.0",
        "question_set_id": question_summary["question_set_id"],
        "question_set_sha256": question_set_sha256(question_set),
        "dataset_id": dataset_summary["dataset_id"],
        "dataset_status": dataset["status"],
        "split": split,
        "record_count": len(records),
        "production_effect": "none",
        "records": records,
    }


def _validate_task(task: str, config: object, question_ids: set[str]) -> None:
    if not isinstance(config, dict):
        raise QuestionSetError(f"tasks.{task} must be an object")
    _exact_keys(config, {"state_fields", "questions", "decision_policy"}, f"tasks.{task}")
    state_fields = config["state_fields"]
    expected_fields = {"left", "right", "context"} if task == "copy-similarity" else {"claim", "source_excerpt", "context"}
    if not isinstance(state_fields, list) or set(state_fields) != expected_fields:
        raise QuestionSetError(f"tasks.{task}.state_fields must be {sorted(expected_fields)}")
    questions = config["questions"]
    if not isinstance(questions, dict) or not questions:
        raise QuestionSetError(f"tasks.{task}.questions must be a non-empty object")
    for question_id, question in questions.items():
        if question_id in question_ids:
            raise QuestionSetError(f"Duplicate question id across tasks: {question_id}")
        question_ids.add(question_id)
        if not isinstance(question, dict):
            raise QuestionSetError(f"Question {question_id} must be an object")
        if question.get("type") not in QUESTION_TYPES:
            raise QuestionSetError(f"Question {question_id} has unsupported type")
        if not isinstance(question.get("instructions"), str) or not question["instructions"].strip():
            raise QuestionSetError(f"Question {question_id} requires instructions")
        criteria = question.get("criteria")
        if question["type"] == "choice" and (not isinstance(criteria, dict) or len(criteria) < 2):
            raise QuestionSetError(f"Choice {question_id} requires at least two criteria")
        if question["type"] == "noul" and criteria is not None and not isinstance(criteria, dict):
            raise QuestionSetError(f"Noul {question_id} criteria must be an object when supplied")
    policy = config["decision_policy"]
    if not isinstance(policy, dict) or policy.get("production_effect") != "none":
        raise QuestionSetError(f"tasks.{task}.decision_policy must declare no production effect")


def _exact_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    missing = sorted(keys - set(value))
    unknown = sorted(set(value) - keys)
    if missing or unknown:
        raise QuestionSetError(f"{label} keys invalid; missing={missing}, unknown={unknown}")


def _text(value: dict[str, Any], key: str, label: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise QuestionSetError(f"{label}.{key} must be non-empty text")
    return item
