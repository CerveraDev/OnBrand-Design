from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from tools.rider_campaign_runtime.copy_allocation import (
    NEAR_DUPLICATE_BLOCK_THRESHOLD,
    NEAR_DUPLICATE_WARN_THRESHOLD,
    normalize_text,
    similarity_score,
)


class DatasetError(ValueError):
    """Raised when a semantic evaluation dataset violates its contract."""


SCHEMA_VERSION = "1.0"
TASKS = {"copy-similarity", "claim-support"}
SPLITS = {"calibration", "holdout"}
ACTIONS = {"allow", "review", "block"}
RELATIONS = {"distinct", "related-distinct", "equivalent"}
SUPPORT_LABELS = {"supported", "unsupported", "insufficient"}
ADJUDICATION_STATUSES = {"provisional", "reviewed", "adjudicated"}
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+?1[\s.-]*)?(?:\(?\d{3}\)?[\s.-]*)\d{3}[\s.-]*\d{4}")


def load_dataset(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DatasetError(f"Could not load dataset {source}: {exc}") from exc
    validate_dataset(value)
    return value


def validate_dataset(dataset: object) -> dict[str, Any]:
    if not isinstance(dataset, dict):
        raise DatasetError("Dataset must be a JSON object")
    _require_exact_keys(
        dataset,
        {
            "schema_version",
            "dataset_id",
            "project",
            "status",
            "created_at",
            "purpose",
            "deidentification",
            "label_policy",
            "cases",
        },
        "dataset",
    )
    if dataset["schema_version"] != SCHEMA_VERSION:
        raise DatasetError(f"schema_version must be {SCHEMA_VERSION}")
    for key in ("dataset_id", "project", "status", "created_at", "purpose"):
        _require_text(dataset, key, "dataset")
    if dataset["status"] != "provisional":
        raise DatasetError("The seed dataset must remain provisional until human adjudication")
    if not isinstance(dataset["deidentification"], dict) or dataset["deidentification"].get("contains_personal_contact_data") is not False:
        raise DatasetError("deidentification.contains_personal_contact_data must be false")
    policy = dataset["label_policy"]
    if not isinstance(policy, dict):
        raise DatasetError("label_policy must be an object")
    for key in ("copy_similarity", "claim_support", "review_rule"):
        _require_text(policy, key, "label_policy")

    cases = dataset["cases"]
    if not isinstance(cases, list) or len(cases) < 20:
        raise DatasetError("cases must contain at least 20 evaluation cases")
    ids: set[str] = set()
    counts: Counter[tuple[str, str]] = Counter()
    label_counts: Counter[tuple[str, str]] = Counter()
    content_hashes: set[str] = set()
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            raise DatasetError(f"{label} must be an object")
        _require_exact_keys(
            case,
            {"id", "task", "split", "state", "expected", "challenge_tags", "provenance", "adjudication"},
            label,
        )
        case_id = _require_text(case, "id", label)
        if case_id in ids:
            raise DatasetError(f"Duplicate case id: {case_id}")
        ids.add(case_id)
        task = case["task"]
        split = case["split"]
        if task not in TASKS:
            raise DatasetError(f"{case_id} has unsupported task: {task}")
        if split not in SPLITS:
            raise DatasetError(f"{case_id} has unsupported split: {split}")
        counts[(task, split)] += 1
        _validate_case_state(case_id, task, case["state"])
        _validate_expected(case_id, task, case["expected"])
        label_key = case["expected"]["semantic_relation"] if task == "copy-similarity" else case["expected"]["support"]
        label_counts[(task, label_key)] += 1
        tags = case["challenge_tags"]
        if not isinstance(tags, list) or not tags or any(not isinstance(item, str) or not item for item in tags):
            raise DatasetError(f"{case_id} challenge_tags must be a non-empty string array")
        provenance = case["provenance"]
        if not isinstance(provenance, dict):
            raise DatasetError(f"{case_id} provenance must be an object")
        for key in ("kind", "reference", "notes"):
            _require_text(provenance, key, f"{case_id}.provenance")
        adjudication = case["adjudication"]
        if not isinstance(adjudication, dict):
            raise DatasetError(f"{case_id} adjudication must be an object")
        if adjudication.get("status") not in ADJUDICATION_STATUSES:
            raise DatasetError(f"{case_id} adjudication.status is unsupported")
        reviewer_labels = adjudication.get("reviewer_labels")
        if not isinstance(reviewer_labels, list):
            raise DatasetError(f"{case_id} reviewer_labels must be an array")
        if adjudication["status"] == "provisional" and reviewer_labels:
            raise DatasetError(f"{case_id} provisional cases cannot claim reviewer labels")

        serialized_state = json.dumps(case["state"], sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(serialized_state.encode("utf-8")).hexdigest()
        if digest in content_hashes:
            raise DatasetError(f"{case_id} duplicates another case state")
        content_hashes.add(digest)
        if EMAIL_RE.search(serialized_state) or PHONE_RE.search(serialized_state):
            raise DatasetError(f"{case_id} contains email or phone-like personal contact data")

    for task in TASKS:
        for split in SPLITS:
            if counts[(task, split)] < 2:
                raise DatasetError(f"{task} requires at least two {split} cases")
    for relation in RELATIONS:
        if label_counts[("copy-similarity", relation)] < 2:
            raise DatasetError(f"copy-similarity requires at least two {relation} cases")
    for support in SUPPORT_LABELS:
        if label_counts[("claim-support", support)] < 2:
            raise DatasetError(f"claim-support requires at least two {support} cases")
    holdout_count = sum(count for (task, split), count in counts.items() if split == "holdout")
    if holdout_count / len(cases) < 0.25:
        raise DatasetError("At least 25% of cases must remain in the holdout split")

    return {
        "dataset_id": dataset["dataset_id"],
        "case_count": len(cases),
        "counts": {f"{task}:{split}": counts[(task, split)] for task in sorted(TASKS) for split in sorted(SPLITS)},
        "labels": {f"{task}:{label}": count for (task, label), count in sorted(label_counts.items())},
        "status": dataset["status"],
    }


def evaluate_lexical_baseline(dataset: dict[str, Any]) -> dict[str, Any]:
    summary = validate_dataset(dataset)
    results: list[dict[str, Any]] = []
    action_matches = 0
    by_split: Counter[tuple[str, bool]] = Counter()
    by_task: Counter[tuple[str, bool]] = Counter()
    semantic_gap_ids: list[str] = []
    for case in dataset["cases"]:
        expected_action = case["expected"]["action"]
        if case["task"] == "copy-similarity":
            left = normalize_text(case["state"]["left"])
            right = normalize_text(case["state"]["right"])
            score = similarity_score(left, right)
            if case["state"]["approved_reuse"]:
                predicted_action = "allow"
                reason = "approved reuse exemption"
            elif left == right:
                predicted_action = "block"
                reason = "exact normalized match"
            elif score >= NEAR_DUPLICATE_BLOCK_THRESHOLD:
                predicted_action = "block"
                reason = "lexical blocking threshold"
            elif score >= NEAR_DUPLICATE_WARN_THRESHOLD:
                predicted_action = "review"
                reason = "lexical warning threshold"
            else:
                predicted_action = "allow"
                reason = "below lexical warning threshold"
            if case["expected"]["semantic_relation"] == "equivalent" and predicted_action == "allow" and not case["state"]["approved_reuse"]:
                semantic_gap_ids.append(case["id"])
            details = {"lexical_score": round(score, 3), "reason": reason}
        else:
            predicted_action = "review"
            details = {"reason": "current baseline checks reference presence, not semantic support"}
        matched = predicted_action == expected_action
        action_matches += int(matched)
        by_split[(case["split"], matched)] += 1
        by_task[(case["task"], matched)] += 1
        results.append(
            {
                "id": case["id"],
                "task": case["task"],
                "split": case["split"],
                "expected_action": expected_action,
                "predicted_action": predicted_action,
                "matched": matched,
                **details,
            }
        )
    split_metrics = {}
    for split in sorted(SPLITS):
        matched = by_split[(split, True)]
        total = matched + by_split[(split, False)]
        split_metrics[split] = {"matched": matched, "total": total, "accuracy": round(matched / total, 3)}
    task_metrics = {}
    for task in sorted(TASKS):
        matched = by_task[(task, True)]
        total = matched + by_task[(task, False)]
        task_metrics[task] = {"matched": matched, "total": total, "accuracy": round(matched / total, 3)}
    return {
        "dataset_id": summary["dataset_id"],
        "dataset_status": summary["status"],
        "acceptance_evidence": False,
        "baseline": {
            "name": "phase-10-lexical-and-reference-presence",
            "warning_threshold": NEAR_DUPLICATE_WARN_THRESHOLD,
            "blocking_threshold": NEAR_DUPLICATE_BLOCK_THRESHOLD,
        },
        "case_count": summary["case_count"],
        "matched": action_matches,
        "accuracy": round(action_matches / summary["case_count"], 3),
        "split_metrics": split_metrics,
        "task_metrics": task_metrics,
        "semantic_gap_case_ids": semantic_gap_ids,
        "results": results,
    }


def review_markdown(dataset: dict[str, Any]) -> str:
    validate_dataset(dataset)
    lines = [
        "# Phase 13 Rider Dataset Review Worksheet",
        "",
        "This worksheet intentionally omits provisional expected labels. Record independent reviewer judgments before viewing or changing the seed labels in the JSON dataset.",
        "",
        "For copy similarity, use `distinct`, `related-distinct`, or `equivalent`, then choose `allow`, `review`, or `block`. For claim support, use `supported`, `unsupported`, or `insufficient`, then choose an action.",
        "",
    ]
    for case in dataset["cases"]:
        lines.extend([f"## {case['id']}", "", f"- Task: `{case['task']}`", f"- Split: `{case['split']}`"])
        if case["task"] == "copy-similarity":
            lines.extend(
                [
                    f"- Left: {case['state']['left']}",
                    f"- Right: {case['state']['right']}",
                    f"- Context: {case['state']['context']}",
                    f"- Approved reuse: `{str(case['state']['approved_reuse']).lower()}`",
                    "- Reviewer label:",
                    "- Reviewer action:",
                ]
            )
        else:
            lines.extend(
                [
                    f"- Claim: {case['state']['claim']}",
                    f"- Source excerpt: {case['state']['source_excerpt']}",
                    f"- Context: {case['state']['context']}",
                    "- Reviewer support label:",
                    "- Reviewer action:",
                ]
            )
        lines.extend(["- Reviewer notes:", ""])
    return "\n".join(lines).rstrip() + "\n"


def _validate_case_state(case_id: str, task: str, state: object) -> None:
    if not isinstance(state, dict):
        raise DatasetError(f"{case_id} state must be an object")
    if task == "copy-similarity":
        _require_exact_keys(state, {"left", "right", "context", "approved_reuse"}, f"{case_id}.state")
        for key in ("left", "right", "context"):
            _require_text(state, key, f"{case_id}.state")
        if type(state["approved_reuse"]) is not bool:
            raise DatasetError(f"{case_id} approved_reuse must be boolean")
    else:
        _require_exact_keys(state, {"claim", "source_excerpt", "context"}, f"{case_id}.state")
        for key in ("claim", "source_excerpt", "context"):
            _require_text(state, key, f"{case_id}.state")


def _validate_expected(case_id: str, task: str, expected: object) -> None:
    if not isinstance(expected, dict):
        raise DatasetError(f"{case_id} expected must be an object")
    if task == "copy-similarity":
        _require_exact_keys(expected, {"semantic_relation", "action", "intentional_refrain"}, f"{case_id}.expected")
        if expected["semantic_relation"] not in RELATIONS:
            raise DatasetError(f"{case_id} semantic_relation is unsupported")
        if type(expected["intentional_refrain"]) is not bool:
            raise DatasetError(f"{case_id} intentional_refrain must be boolean")
    else:
        _require_exact_keys(expected, {"support", "action"}, f"{case_id}.expected")
        if expected["support"] not in SUPPORT_LABELS:
            raise DatasetError(f"{case_id} support is unsupported")
    if expected["action"] not in ACTIONS:
        raise DatasetError(f"{case_id} action is unsupported")


def _require_exact_keys(value: dict, keys: set[str], label: str) -> None:
    missing = sorted(keys - set(value))
    unknown = sorted(set(value) - keys)
    if missing or unknown:
        raise DatasetError(f"{label} keys invalid; missing={missing}, unknown={unknown}")


def _require_text(value: dict, key: str, label: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise DatasetError(f"{label}.{key} must be non-empty text")
    return item
