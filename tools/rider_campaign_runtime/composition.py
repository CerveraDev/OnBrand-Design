from __future__ import annotations

import json
from pathlib import Path

from .scaffold import (
    FOOTER_MODULES,
    Scaffold,
    catalog,
    compose_html,
    module_rows,
)


class CompositionError(ValueError):
    """Raised when a Rider composition catalog or approval plan is invalid."""


CATALOG_VERSION = "1.0"
PLAN_VERSION = "1.0"
APPROVED_STATUS = "approved"


def build_module_catalog(scaffold: Scaffold) -> dict:
    entries = []
    counters: dict[str, int] = {}
    for module_id, rows in catalog(scaffold).items():
        if module_id in FOOTER_MODULES:
            continue
        metadata = scaffold.metadata[module_id]
        prefix = _code_prefix(module_id, metadata.kind, metadata.includes_header)
        counters[prefix] = counters.get(prefix, 0) + 1
        code = f"{prefix}-{counters[prefix]:02d}"
        slots = _slot_summary(scaffold.slot_map.get(module_id, {}))
        entries.append(
            {
                "code": code,
                "scaffold_module_id": module_id,
                "label": metadata.label,
                "module_type": metadata.kind,
                "summary": metadata.summary,
                "content_rows": list(rows),
                "includes_header": metadata.includes_header,
                "locked": metadata.locked,
                "live_text_support": any(slot["slot_type"] in {"text", "rich_text", "url"} for slot in slots),
                "image_required": any(slot["slot_type"] == "image" for slot in slots),
                "image_aspect_ratio": _image_aspect_ratio(metadata.kind, slots),
                "editable_slots": slots,
                "companion_rules": _companion_rules(metadata.kind, metadata.includes_header),
                "preview": {
                    "type": "isolated-html",
                    "path": f"module-previews/{code}.html",
                    "expectation": "Use this isolated scaffold snippet for composition review; final package assets are localized by the runtime.",
                },
            }
        )
    return {"catalog_version": CATALOG_VERSION, "entries": entries}


def write_catalog_artifacts(scaffold: Scaffold, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_dir = output_dir / "module-previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    module_catalog = build_module_catalog(scaffold)
    catalog_path = output_dir / "module_catalog.json"
    catalog_path.write_text(json.dumps(module_catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    code_to_id = {entry["code"]: entry["scaffold_module_id"] for entry in module_catalog["entries"]}
    for code, module_id in sorted(code_to_id.items()):
        html = compose_html(scaffold, module_rows(scaffold, module_id))
        (preview_dir / f"{code}.html").write_text(html, encoding="utf-8")

    review_path = output_dir / "composition-review.md"
    review_path.write_text(_review_markdown(module_catalog), encoding="utf-8")
    return {"catalog": catalog_path, "review": review_path, "preview_dir": preview_dir}


def create_composition_plan(scaffold: Scaffold, selection: dict) -> dict:
    if not isinstance(selection, dict):
        raise CompositionError("Composition selection must be an object")
    unknown = sorted(
        set(selection)
        - {
            "plan_id",
            "status",
            "approved_by",
            "approved_at",
            "representative_variant",
            "selected_module_codes",
            "static_block_decisions",
        }
    )
    if unknown:
        raise CompositionError("Composition selection has unknown field(s): " + ", ".join(unknown))
    plan_id = _require_str(selection, "plan_id", "composition selection")
    status = _require_str(selection, "status", "composition selection")
    if status != APPROVED_STATUS:
        raise CompositionError("composition selection status must be approved")
    approved_by = _require_str(selection, "approved_by", "composition selection")
    approved_at = _require_str(selection, "approved_at", "composition selection")
    representative_variant = _require_str(selection, "representative_variant", "composition selection")
    selected_codes = _require_str_array(selection, "selected_module_codes", "composition selection")
    static_decisions = _require_static_decisions(selection.get("static_block_decisions"), "composition selection")

    module_catalog = build_module_catalog(scaffold)
    entries_by_code = {entry["code"]: entry for entry in module_catalog["entries"]}
    _validate_selected_codes(selected_codes, entries_by_code)
    _validate_static_decisions(selected_codes, static_decisions, entries_by_code)
    _validate_module_compatibility(selected_codes, entries_by_code)

    selected_entries = [entries_by_code[code] for code in selected_codes]
    return {
        "plan_version": PLAN_VERSION,
        "plan_id": plan_id,
        "status": status,
        "approved_by": approved_by,
        "approved_at": approved_at,
        "representative_variant": representative_variant,
        "selected_module_codes": selected_codes,
        "selected_modules": [
            {
                "code": entry["code"],
                "scaffold_module_id": entry["scaffold_module_id"],
                "module_type": entry["module_type"],
                "includes_header": entry["includes_header"],
                "locked": entry["locked"],
            }
            for entry in selected_entries
        ],
        "static_block_decisions": _expanded_static_decisions(static_decisions, entries_by_code),
        "editable_slots": [
            {
                "code": entry["code"],
                "scaffold_module_id": entry["scaffold_module_id"],
                "slot": slot["name"],
                "slot_type": slot["slot_type"],
                "operations": slot["operations"],
                "required_approvals": slot["required_approvals"],
            }
            for entry in selected_entries
            for slot in entry["editable_slots"]
        ],
        "required_assets": [
            {
                "code": entry["code"],
                "scaffold_module_id": entry["scaffold_module_id"],
                "slot": slot["name"],
                "required_approvals": slot["required_approvals"],
                "image_aspect_ratio": entry["image_aspect_ratio"],
            }
            for entry in selected_entries
            for slot in entry["editable_slots"]
            if slot["slot_type"] == "image"
        ],
        "compatibility": {
            "standalone_header_count": sum(1 for entry in selected_entries if entry["module_type"] == "header"),
            "header_bearing_hero_count": sum(
                1 for entry in selected_entries if entry["module_type"] == "hero" and entry["includes_header"]
            ),
            "hero_count": sum(1 for entry in selected_entries if entry["module_type"] == "hero"),
        },
        "approval_required_before": ["image-generation", "html-assembly", "package-generation"],
    }


def validate_composition_contract(spec: dict, scaffold: Scaffold) -> dict | None:
    composition = spec.get("composition")
    if composition is None:
        if spec["build"]["mode"] == "smoke-test":
            return None
        raise CompositionError("composition approval is required for composition-preview and release-build")
    if not isinstance(composition, dict):
        raise CompositionError("composition must be an object")
    if composition.get("status") != APPROVED_STATUS:
        raise CompositionError("composition.status must be approved")
    for field in ("plan_version", "plan_id", "approved_by", "approved_at", "representative_variant"):
        _require_str(composition, field, "composition")
    if composition["plan_version"] != PLAN_VERSION:
        raise CompositionError(f"composition.plan_version must be {PLAN_VERSION}")
    if composition["representative_variant"] != spec["build"].get("representative_variant", "branded"):
        raise CompositionError("composition.representative_variant must match build.representative_variant")

    module_catalog = build_module_catalog(scaffold)
    entries_by_code = {entry["code"]: entry for entry in module_catalog["entries"]}
    selected_codes = _require_str_array(composition, "selected_module_codes", "composition")
    _validate_selected_codes(selected_codes, entries_by_code)
    _validate_static_decisions(
        selected_codes,
        _require_static_decisions(composition.get("static_block_decisions"), "composition"),
        entries_by_code,
    )
    _validate_module_compatibility(selected_codes, entries_by_code)

    expected_module_ids = [entries_by_code[code]["scaffold_module_id"] for code in selected_codes]
    actual_module_ids = [module["id"] for module in spec["modules"]]
    if actual_module_ids != expected_module_ids:
        raise CompositionError("composition.selected_module_codes must match campaign modules in exact order")

    expected_static = {
        entries_by_code[item["code"]]["scaffold_module_id"]: item["decision"]
        for item in composition["static_block_decisions"]
    }
    actual_static = {item["id"]: item["decision"] for item in spec["static_blocks"]}
    if actual_static != expected_static:
        raise CompositionError("composition.static_block_decisions must match campaign static_blocks")
    return _composition_summary(composition)


def _code_prefix(module_id: str, kind: str, includes_header: bool) -> str:
    if kind == "header":
        return "H"
    if kind == "static":
        return "S"
    if kind == "body":
        return "B"
    if kind == "hero" and module_id.startswith("AI GENERATED IMAGE"):
        return "AI"
    if kind == "hero" and includes_header:
        return "HH"
    if kind == "hero":
        return "HR"
    return "M"


def _slot_summary(slots: dict) -> list[dict]:
    summary = []
    for name, rules in sorted(slots.items()):
        operations = sorted({rule["operation"] for rule in rules})
        required = sorted({rule["required_approval"] for rule in rules if "required_approval" in rule})
        summary.append(
            {
                "name": name,
                "slot_type": _slot_type(operations),
                "operations": operations,
                "required_approvals": required,
            }
        )
    return summary


def _slot_type(operations: list[str]) -> str:
    if any(operation in {"replace_image_src", "replace_background_url"} for operation in operations):
        return "image"
    if "replace_href" in operations:
        return "url"
    if any(operation.startswith("replace_text") for operation in operations):
        return "text"
    return "unknown"


def _image_aspect_ratio(kind: str, slots: list[dict]) -> str:
    if not any(slot["slot_type"] == "image" for slot in slots):
        return ""
    if kind == "hero":
        return "module-native hero crop; approve exact crop before image generation"
    return "module-native body crop; approve exact crop before image selection"


def _companion_rules(kind: str, includes_header: bool) -> list[str]:
    if kind == "header":
        return ["May pair with zero or one hero that does not include its own header."]
    if kind == "hero" and includes_header:
        return ["Do not pair with a standalone header."]
    if kind == "hero":
        return ["May pair with zero or one standalone header."]
    if kind == "static":
        return ["Requires an explicit include/exclude decision and appears at most once."]
    return ["Can be selected with a compatible header/hero combination."]


def _validate_selected_codes(selected_codes: list[str], entries_by_code: dict[str, dict]) -> None:
    unknown = sorted(set(selected_codes) - set(entries_by_code))
    if unknown:
        raise CompositionError("Unknown composition module code(s): " + ", ".join(unknown))
    duplicates = sorted({code for code in selected_codes if selected_codes.count(code) > 1})
    if duplicates:
        raise CompositionError("Duplicate composition module code(s): " + ", ".join(duplicates))
    if not any(entries_by_code[code]["module_type"] == "hero" for code in selected_codes):
        raise CompositionError("Composition must include at least one hero module code")


def _validate_module_compatibility(selected_codes: list[str], entries_by_code: dict[str, dict]) -> None:
    headers = [code for code in selected_codes if entries_by_code[code]["module_type"] == "header"]
    header_bearing_heroes = [
        code
        for code in selected_codes
        if entries_by_code[code]["module_type"] == "hero" and entries_by_code[code]["includes_header"]
    ]
    if len(headers) > 1:
        raise CompositionError("Composition may include at most one standalone header")
    if headers and header_bearing_heroes:
        raise CompositionError(
            "Standalone header code(s) are incompatible with header-bearing hero code(s): "
            + ", ".join(headers + header_bearing_heroes)
        )


def _validate_static_decisions(selected_codes: list[str], decisions: list[dict], entries_by_code: dict[str, dict]) -> None:
    static_codes = {code for code, entry in entries_by_code.items() if entry["module_type"] == "static"}
    decision_codes = [item["code"] for item in decisions]
    unknown = sorted(set(decision_codes) - static_codes)
    if unknown:
        raise CompositionError("Unknown static block code(s): " + ", ".join(unknown))
    missing = sorted(static_codes - set(decision_codes))
    if missing:
        raise CompositionError("Missing static block decision(s): " + ", ".join(missing))
    duplicates = sorted({code for code in decision_codes if decision_codes.count(code) > 1})
    if duplicates:
        raise CompositionError("Duplicate static block decision(s): " + ", ".join(duplicates))
    decision_map = {item["code"]: item["decision"] for item in decisions}
    for code, decision in decision_map.items():
        if decision not in {"include", "exclude"}:
            raise CompositionError(f"Static block {code} decision must be include or exclude")
    selected_static = set(selected_codes) & static_codes
    included_static = {code for code, decision in decision_map.items() if decision == "include"}
    if selected_static != included_static:
        raise CompositionError("Selected static block codes must exactly match include decisions")


def _expanded_static_decisions(decisions: list[dict], entries_by_code: dict[str, dict]) -> list[dict]:
    return [
        {
            "code": item["code"],
            "scaffold_module_id": entries_by_code[item["code"]]["scaffold_module_id"],
            "decision": item["decision"],
        }
        for item in decisions
    ]


def _composition_summary(composition: dict) -> dict:
    return {
        "plan_version": composition["plan_version"],
        "plan_id": composition["plan_id"],
        "status": composition["status"],
        "approved_by": composition["approved_by"],
        "approved_at": composition["approved_at"],
        "representative_variant": composition["representative_variant"],
        "selected_module_codes": composition["selected_module_codes"],
        "selected_modules": composition.get("selected_modules", []),
        "static_block_decisions": composition["static_block_decisions"],
        "required_assets": composition.get("required_assets", []),
    }


def _review_markdown(module_catalog: dict) -> str:
    lines = [
        "# Rider Composition Preview Catalog",
        "",
        "Use these stable codes to select a Design Proof composition before image generation or final HTML assembly.",
        "",
        "| Code | Type | Module | Header | Image | Slots | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for entry in module_catalog["entries"]:
        slots = ", ".join(slot["name"] for slot in entry["editable_slots"]) or "locked"
        header = "includes" if entry["includes_header"] else "standalone" if entry["module_type"] == "header" else "none"
        image = "yes" if entry["image_required"] else "no"
        lines.append(
            "| {code} | {module_type} | {label} | {header} | {image} | {slots} | {summary} |".format(
                code=entry["code"],
                module_type=entry["module_type"],
                label=entry["label"],
                header=header,
                image=image,
                slots=slots,
                summary=entry["summary"].replace("|", "\\|"),
            )
        )
    lines.append("")
    lines.append("A standalone header cannot be selected with a hero whose header behavior is `includes`.")
    lines.append("Every static block code must receive an include/exclude decision.")
    return "\n".join(lines) + "\n"


def _require_str(obj: dict, field: str, label: str) -> str:
    value = obj.get(field)
    if not isinstance(value, str) or not value:
        raise CompositionError(f"{label}.{field} must be a non-empty string")
    return value


def _require_str_array(obj: dict, field: str, label: str) -> list[str]:
    value = obj.get(field)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise CompositionError(f"{label}.{field} must be a non-empty array of strings")
    return list(value)


def _require_static_decisions(value, label: str) -> list[dict]:
    if not isinstance(value, list):
        raise CompositionError(f"{label}.static_block_decisions must be an array")
    decisions = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise CompositionError(f"{label}.static_block_decisions[{index}] must be an object")
        unknown = sorted(set(item) - {"code", "scaffold_module_id", "decision"})
        if unknown:
            raise CompositionError(
                f"{label}.static_block_decisions[{index}] has unknown field(s): " + ", ".join(unknown)
            )
        decisions.append(
            {
                "code": _require_str(item, "code", f"{label}.static_block_decisions[{index}]"),
                "decision": _require_str(item, "decision", f"{label}.static_block_decisions[{index}]"),
            }
        )
    return decisions
