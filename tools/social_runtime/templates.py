"""Social composition templates: slide-sequenced layouts stored as project data."""

from __future__ import annotations

import json
from pathlib import Path
import re


TEMPLATE_VERSION = "1.0"
AUDIENCES = ("in-house", "outside-broker")
SLIDE_ROLES = ("opener", "feature", "detail", "proof", "call-to-action")
TEXT_CHANNELS = ("on-image-text", "slide-text")
TEMPLATE_FIELDS = {
    "schema_version", "code", "label", "kind", "formats", "approval_status",
    "audiences", "min_slides", "max_slides", "sequence",
}
STEP_FIELDS = {"role", "min", "max", "image", "slots", "locked"}
SLOT_FIELDS = {"channel", "required", "max_chars"}


class TemplateError(ValueError):
    """Raised when a social template is malformed, unknown, or does not fit a spec."""


def load_template(templates_dir: Path | str, code: str) -> dict:
    if not isinstance(code, str) or not re.fullmatch(r"[A-Z]{3}-\d{2}", code):
        raise TemplateError(f"Invalid social template code: {code!r}")
    path = Path(templates_dir) / f"{code}.json"
    if not path.is_file():
        raise TemplateError(f"Unknown social template: {code}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise TemplateError(f"Invalid social template JSON ({code}): {err}") from err
    return validate_template(data, code=code)


def validate_template(data: object, *, code: str) -> dict:
    label = f"template {code}"
    if not isinstance(data, dict) or set(data) != TEMPLATE_FIELDS:
        raise TemplateError(f"{label} must define exactly: {', '.join(sorted(TEMPLATE_FIELDS))}")
    if data["schema_version"] != TEMPLATE_VERSION:
        raise TemplateError(f"{label} schema_version must be {TEMPLATE_VERSION}")
    if data["code"] != code:
        raise TemplateError(f"{label} declares a different code: {data['code']!r}")
    if not isinstance(data["label"], str) or not data["label"]:
        raise TemplateError(f"{label} label must be a non-empty string")
    if data["kind"] not in ("post", "carousel"):
        raise TemplateError(f"{label} kind must be post or carousel")
    if data["approval_status"] not in ("draft", "approved"):
        raise TemplateError(f"{label} approval_status must be draft or approved")
    for field, allowed in (("formats", None), ("audiences", AUDIENCES)):
        values = data[field]
        if not isinstance(values, list) or not values or any(not isinstance(v, str) for v in values):
            raise TemplateError(f"{label} {field} must be a non-empty string array")
        if allowed and set(values) - set(allowed):
            raise TemplateError(f"{label} {field} has unknown value(s)")
    sequence = data["sequence"]
    if not isinstance(sequence, list) or not sequence:
        raise TemplateError(f"{label} sequence must be a non-empty array")
    for index, step in enumerate(sequence):
        _validate_step(step, f"{label} sequence[{index}]")
    low = sum(step["min"] for step in sequence)
    high = sum(step["max"] for step in sequence)
    for field in ("min_slides", "max_slides"):
        if type(data[field]) is not int or data[field] < 1:
            raise TemplateError(f"{label} {field} must be a positive integer")
    if not low <= data["min_slides"] <= data["max_slides"] <= high:
        raise TemplateError(f"{label} slide limits are not satisfiable by its sequence")
    return data


def match_slides(template: dict, roles: list[str]) -> list[dict]:
    """Return the sequence step governing each slide, or fail with the first mismatch."""
    code = template["code"]
    if not template["min_slides"] <= len(roles) <= template["max_slides"]:
        raise TemplateError(
            f"Template {code} takes {template['min_slides']}-{template['max_slides']} slides; "
            f"got {len(roles)}"
        )
    steps = []
    position = 0
    for step in template["sequence"]:
        count = 0
        while position < len(roles) and roles[position] == step["role"] and count < step["max"]:
            steps.append(step)
            position += 1
            count += 1
        if count < step["min"]:
            found = roles[position] if position < len(roles) else "end of slides"
            raise TemplateError(
                f"Template {code} expects role '{step['role']}' at slide {position + 1}; found {found}"
            )
    if position != len(roles):
        raise TemplateError(
            f"Template {code} has no place for role '{roles[position]}' at slide {position + 1}"
        )
    return steps


def _validate_step(step: object, label: str) -> None:
    if not isinstance(step, dict) or set(step) != STEP_FIELDS:
        raise TemplateError(f"{label} must define exactly: {', '.join(sorted(STEP_FIELDS))}")
    if step["role"] not in SLIDE_ROLES:
        raise TemplateError(f"{label} role must be one of {', '.join(SLIDE_ROLES)}")
    if type(step["min"]) is not int or type(step["max"]) is not int or not 0 <= step["min"] <= step["max"] or step["max"] < 1:
        raise TemplateError(f"{label} min/max must satisfy 0 <= min <= max and max >= 1")
    if step["image"] != {"count": 1}:
        raise TemplateError(f"{label} image must be {{\"count\": 1}}; multi-image slides are not supported")
    slots = step["slots"]
    if not isinstance(slots, dict):
        raise TemplateError(f"{label} slots must be an object")
    for name, slot in slots.items():
        if not isinstance(slot, dict) or set(slot) != SLOT_FIELDS:
            raise TemplateError(f"{label} slot '{name}' must define exactly: {', '.join(sorted(SLOT_FIELDS))}")
        if slot["channel"] not in TEXT_CHANNELS or type(slot["required"]) is not bool:
            raise TemplateError(f"{label} slot '{name}' has an invalid channel or required flag")
        if type(slot["max_chars"]) is not int or slot["max_chars"] < 1:
            raise TemplateError(f"{label} slot '{name}' max_chars must be a positive integer")
    locked = step["locked"]
    if not isinstance(locked, dict) or any(
        not isinstance(v, str) or not v for v in locked.values()
    ) or set(locked) & set(slots):
        raise TemplateError(f"{label} locked must map names distinct from slots to non-empty strings")
