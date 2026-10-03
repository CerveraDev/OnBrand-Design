from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Callable

from .jev_pilot import question_set_sha256, validate_question_set


class ProviderError(RuntimeError):
    """Raised when the optional Jev provider boundary is invalid or unauthorized."""


Transport = Callable[[str, dict[str, str], dict[str, Any], float], dict[str, Any]]
ENDPOINT = "https://api.typesafe.ai/v1/systemone"


def batch_sha256(batch: dict[str, Any]) -> str:
    canonical = json.dumps(batch, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def run_provider_batch(
    batch: dict[str, Any],
    question_set: dict[str, Any],
    *,
    enabled: bool,
    live_authorized: bool,
    api_key: str | None,
    transport: Transport,
    executed_at: str,
    timeout: float = 30.0,
    fail_fast: bool = False,
) -> dict[str, Any]:
    _validate_batch(batch, question_set)
    if enabled and not live_authorized:
        raise ProviderError("Live Jev execution requires explicit authorization")
    if enabled and (not isinstance(api_key, str) or not api_key.strip()):
        raise ProviderError("TYPESAFE_API_KEY is required when Jev execution is enabled")
    if not isinstance(executed_at, str) or not executed_at:
        raise ProviderError("executed_at is required")

    records = []
    if not enabled:
        for item in batch["records"]:
            records.append(_base_record(item, "skipped", error={"type": "disabled", "message": "Jev provider is disabled"}))
        return _receipt(batch, question_set, executed_at, "disabled", records)

    headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
    for item in batch["records"]:
        try:
            response = transport(ENDPOINT, headers, item["request"], timeout)
            validated = validate_system_one_response(response, item["request"])
            records.append(
                {
                    **_base_record(item, "completed"),
                    "model": validated["model"],
                    "answers": validated["answers"],
                    "usage": validated["usage"],
                }
            )
        except Exception as exc:
            if fail_fast:
                raise
            records.append(_base_record(item, "failed", error={"type": type(exc).__name__, "message": str(exc)}))
    statuses = {item["status"] for item in records}
    status = "completed" if statuses == {"completed"} else "failed" if statuses == {"failed"} else "partial"
    return _receipt(batch, question_set, executed_at, status, records)


def validate_system_one_response(response: object, request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise ProviderError("Provider response must be an object")
    if set(response) != {"model", "answers", "usage"}:
        raise ProviderError("Provider response keys do not match the receipt contract")
    if response["model"] != request["model"]:
        raise ProviderError(f"Provider model drift: expected {request['model']}, got {response['model']}")
    answers = response["answers"]
    if not isinstance(answers, dict) or set(answers) != set(request["questions"]):
        raise ProviderError("Provider answer IDs do not match request question IDs")
    validated_answers = {}
    for question_id, question in request["questions"].items():
        answer = answers[question_id]
        if not isinstance(answer, dict) or answer.get("type") != question["type"]:
            raise ProviderError(f"{question_id} answer type does not match")
        if question["type"] == "choice":
            validated_answers[question_id] = _validate_choice(question_id, question, answer)
        elif question["type"] == "noul":
            validated_answers[question_id] = _validate_noul(question_id, answer)
        else:
            validated_answers[question_id] = _validate_score(question_id, answer)
    usage = response["usage"]
    if not isinstance(usage, dict) or set(usage) != {"input_tokens", "output_tokens"}:
        raise ProviderError("Provider usage must contain input_tokens and output_tokens")
    for key, value in usage.items():
        if type(value) is not int or value < 0:
            raise ProviderError(f"Provider usage {key} must be a nonnegative integer")
    return {"model": response["model"], "answers": validated_answers, "usage": usage}


def _validate_batch(batch: object, question_set: dict[str, Any]) -> None:
    summary = validate_question_set(question_set)
    if not isinstance(batch, dict):
        raise ProviderError("Request batch must be an object")
    required = {
        "schema_version",
        "question_set_id",
        "question_set_sha256",
        "dataset_id",
        "dataset_status",
        "split",
        "record_count",
        "production_effect",
        "records",
    }
    if set(batch) != required:
        raise ProviderError("Request batch keys do not match the provider contract")
    if batch["question_set_id"] != summary["question_set_id"] or batch["question_set_sha256"] != question_set_sha256(question_set):
        raise ProviderError("Request batch does not match the locked question set")
    if batch["dataset_status"] != "adjudicated" or batch["production_effect"] != "none":
        raise ProviderError("Request batch must be adjudicated and non-production")
    records = batch["records"]
    if not isinstance(records, list) or len(records) != batch["record_count"] or not records:
        raise ProviderError("Request batch record_count is invalid")
    ids = [item.get("case_id") for item in records if isinstance(item, dict)]
    if len(ids) != len(records) or len(ids) != len(set(ids)):
        raise ProviderError("Request batch case IDs must be unique")
    for item in records:
        if set(item) != {"case_id", "task", "split", "policy_context", "request"}:
            raise ProviderError(f"{item.get('case_id')} request record keys are invalid")
        if item["split"] != batch["split"]:
            raise ProviderError(f"{item['case_id']} split does not match the batch")
        task = item["task"]
        request = item["request"]
        if request.get("model") != question_set["model"] or request.get("questions") != question_set["tasks"][task]["questions"]:
            raise ProviderError(f"{item['case_id']} request drifted from the locked question set")


def _validate_choice(question_id: str, question: dict[str, Any], answer: dict[str, Any]) -> dict[str, Any]:
    if set(answer) != {"type", "choice", "confidence", "probabilities"}:
        raise ProviderError(f"{question_id} choice answer keys are invalid")
    options = set(question["criteria"])
    if answer["choice"] not in options:
        raise ProviderError(f"{question_id} selected an unknown choice")
    probabilities = _probabilities(question_id, answer["probabilities"], options)
    confidence = _probability(question_id, "confidence", answer["confidence"])
    return {"type": "choice", "choice": answer["choice"], "confidence": confidence, "probabilities": probabilities}


def _validate_noul(question_id: str, answer: dict[str, Any]) -> dict[str, Any]:
    if set(answer) != {"type", "noul"}:
        raise ProviderError(f"{question_id} noul answer keys are invalid")
    return {"type": "noul", "noul": _probability(question_id, "noul", answer["noul"])}


def _validate_score(question_id: str, answer: dict[str, Any]) -> dict[str, Any]:
    if set(answer) != {"type", "score", "confidence", "legend", "probabilities"}:
        raise ProviderError(f"{question_id} score answer keys are invalid")
    if type(answer["score"]) not in {int, float} or not math.isfinite(answer["score"]):
        raise ProviderError(f"{question_id} score must be finite")
    legend = answer["legend"]
    if not isinstance(legend, dict) or not legend:
        raise ProviderError(f"{question_id} legend must be non-empty")
    probabilities = _probabilities(question_id, answer["probabilities"], set(legend))
    confidence = _probability(question_id, "confidence", answer["confidence"])
    return {"type": "score", "score": answer["score"], "confidence": confidence, "legend": legend, "probabilities": probabilities}


def _probabilities(question_id: str, value: object, keys: set[str]) -> dict[str, float]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ProviderError(f"{question_id} probability keys are invalid")
    probabilities = {key: _probability(question_id, key, item) for key, item in value.items()}
    if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=0.02):
        raise ProviderError(f"{question_id} probabilities must sum to 1")
    return probabilities


def _probability(question_id: str, field: str, value: object) -> float:
    if type(value) not in {int, float} or not math.isfinite(value) or not 0 <= value <= 1:
        raise ProviderError(f"{question_id} {field} must be a finite probability")
    return float(value)


def _base_record(item: dict[str, Any], status: str, *, error: dict[str, str] | None = None) -> dict[str, Any]:
    record = {
        "case_id": item["case_id"],
        "task": item["task"],
        "request_sha256": hashlib.sha256(
            json.dumps(item["request"], sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "status": status,
    }
    if error is not None:
        record["error"] = error
    return record


def _receipt(
    batch: dict[str, Any],
    question_set: dict[str, Any],
    executed_at: str,
    status: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "provider": "typesafe",
        "endpoint": ENDPOINT,
        "question_set_id": question_set["question_set_id"],
        "question_set_sha256": question_set_sha256(question_set),
        "batch_sha256": batch_sha256(batch),
        "dataset_id": batch["dataset_id"],
        "split": batch["split"],
        "executed_at": executed_at,
        "status": status,
        "production_effect": "none",
        "records": records,
    }
