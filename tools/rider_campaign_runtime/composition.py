from __future__ import annotations

from html import escape
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
GALLERY_VERSION = "1.0"
SEQUENCE_GALLERY_VERSION = "1.0"
PLAN_VERSION = "1.0"
APPROVED_STATUS = "approved"


def build_module_catalog(scaffold: Scaffold) -> dict:
    entries = []
    counters: dict[str, int] = {}
    for module_id, rows in catalog(scaffold).items():
        metadata = scaffold.metadata[module_id]
        if metadata.kind == "footer" or module_id in FOOTER_MODULES:
            continue
        if metadata.code:
            code = metadata.code
        else:
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
                "module_family": metadata.family or metadata.kind,
                "layout_role": metadata.layout_role or metadata.kind,
                "summary": metadata.summary,
                "content_rows": list(rows),
                "includes_header": metadata.includes_header,
                "locked": metadata.locked,
                "live_text_support": any(slot["slot_type"] in {"text", "rich_text", "url"} for slot in slots),
                "image_required": any(slot["slot_type"] == "image" for slot in slots),
                "image_aspect_ratio": (
                    str((metadata.image or {}).get("aspect_ratio") or "")
                    if metadata.image is not None
                    else _image_aspect_ratio(metadata.kind, slots)
                ),
                "editable_slots": slots,
                "companion_rules": (
                    _metadata_companion_rules(metadata.compatibility)
                    if metadata.compatibility
                    else _companion_rules(metadata.kind, metadata.includes_header)
                ),
                "theme": metadata.theme or {},
                "compatibility": metadata.compatibility or {},
                "campaign_types": list(metadata.campaign_types),
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

    configurations = build_hero_configurations(module_catalog)
    configuration_dir = output_dir / "hero-configurations"
    configuration_dir.mkdir(parents=True, exist_ok=True)
    entries_by_code = {entry["code"]: entry for entry in module_catalog["entries"]}
    for option in configurations["options"]:
        rows = []
        for code in option["selected_module_codes"]:
            rows.extend(module_rows(scaffold, entries_by_code[code]["scaffold_module_id"]))
        (configuration_dir / f"{option['id']}.html").write_text(compose_html(scaffold, rows), encoding="utf-8")
    configuration_path = output_dir / "hero-configurations.json"
    configuration_path.write_text(json.dumps(configurations, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    gallery_path = output_dir / "hero-gallery.html"
    gallery_path.write_text(_gallery_html(configurations), encoding="utf-8")

    module_gallery_path = output_dir / "module-gallery.html"
    module_gallery_path.write_text(_module_gallery_html(module_catalog), encoding="utf-8")

    sequence_path = None
    sequence_gallery_path = None
    sequence_dir = None
    if scaffold.refined:
        sequences = build_sequence_configurations(module_catalog)
        sequence_dir = output_dir / "sequence-configurations"
        sequence_dir.mkdir(parents=True, exist_ok=True)
        for option in sequences["options"]:
            rows = []
            for code in option["selected_module_codes"]:
                rows.extend(module_rows(scaffold, entries_by_code[code]["scaffold_module_id"]))
            (sequence_dir / f"{option['id']}.html").write_text(compose_html(scaffold, rows), encoding="utf-8")
        sequence_path = output_dir / "sequence-configurations.json"
        sequence_path.write_text(json.dumps(sequences, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        sequence_gallery_path = output_dir / "sequence-gallery.html"
        sequence_gallery_path.write_text(_sequence_gallery_html(sequences), encoding="utf-8")

    review_path = output_dir / "composition-review.md"
    review_path.write_text(_review_markdown(module_catalog), encoding="utf-8")
    return {
        "catalog": catalog_path,
        "review": review_path,
        "preview_dir": preview_dir,
        "hero_configurations": configuration_path,
        "hero_gallery": gallery_path,
        "hero_configuration_dir": configuration_dir,
        "module_gallery": module_gallery_path,
        **({"sequence_configurations": sequence_path} if sequence_path else {}),
        **({"sequence_gallery": sequence_gallery_path} if sequence_gallery_path else {}),
        **({"sequence_configuration_dir": sequence_dir} if sequence_dir else {}),
    }


def build_hero_configurations(module_catalog: dict) -> dict:
    entries = module_catalog["entries"]
    headers = [entry for entry in entries if entry["module_type"] == "header"]
    non_header_heroes = [
        entry for entry in entries if entry["module_type"] == "hero" and not entry["includes_header"]
    ]
    header_heroes = [entry for entry in entries if entry["module_type"] == "hero" and entry["includes_header"]]
    candidates = []
    for hero in header_heroes:
        candidates.append((None, hero))
    for hero in non_header_heroes:
        candidates.append((None, hero))
    for header in headers:
        for hero in non_header_heroes:
            if _header_hero_pair_is_compatible(header, hero):
                candidates.append((header, hero))

    options = []
    for index, (header, hero) in enumerate(candidates, start=1):
        codes = [hero["code"]] if header is None else [header["code"], hero["code"]]
        label = hero["label"] if header is None else f"{header['label']} + {hero['label']}"
        if hero["includes_header"]:
            group = "integrated-header"
            group_label = "Integrated Header And Hero"
        elif header is None:
            group = "hero-only"
            group_label = "Hero Only"
        else:
            group = f"header-{header['code']}"
            group_label = header["label"]
        options.append(
            {
                "id": f"CFG-{index:02d}",
                "label": label,
                "group": group,
                "group_label": group_label,
                "selected_module_codes": codes,
                "header_code": header["code"] if header else "",
                "hero_code": hero["code"],
                "includes_header": hero["includes_header"] or header is not None,
                "live_text_support": hero["live_text_support"] or bool(header and header["live_text_support"]),
                "image_required": hero["image_required"],
                "image_aspect_ratio": hero["image_aspect_ratio"],
                "compatibility_notes": list(hero["companion_rules"]),
                "preview_path": f"hero-configurations/CFG-{index:02d}.html",
            }
        )
    return {"gallery_version": GALLERY_VERSION, "option_count": len(options), "options": options}


def build_sequence_configurations(module_catalog: dict) -> dict:
    entries_by_code = {entry["code"]: entry for entry in module_catalog["entries"]}
    presets = [
        {
            "id": "SEQ-LF-01",
            "label": "Dark Framed Editorial",
            "campaign_type": "long-form",
            "theme": "dark",
            "codes": ["H-02", "HR-01", "B-04", "PF-01"],
            "notes": "Compact dark header and framed hero followed by the default dark editorial body.",
        },
        {
            "id": "SEQ-LF-02",
            "label": "Light-Led Editorial Transition",
            "campaign_type": "long-form",
            "theme": "light-to-dark",
            "codes": ["H-04", "HR-02", "B-04", "PF-01"],
            "notes": "Light header and hero transition into the scaffold's default dark editorial body.",
        },
        {
            "id": "SEQ-LF-03",
            "label": "Integrated Hero With Authority Proof",
            "campaign_type": "long-form",
            "theme": "image-led-to-dark",
            "codes": ["HH-01", "B-04", "S-01", "PF-01"],
            "notes": "Integrated header and hero, editorial body, one approved authority message, and closing CTA.",
        },
        {
            "id": "SEQ-LF-04",
            "label": "Editorial With Callout And Specs",
            "campaign_type": "long-form",
            "theme": "dark",
            "codes": ["H-01", "HR-01", "B-04", "C-01", "S-03", "PF-01"],
            "notes": "Two-column headline header, framed hero, editorial body, closing callout, and residence specs.",
        },
        {
            "id": "SEQ-LF-05",
            "label": "Masonry With Design Proof",
            "campaign_type": "long-form",
            "theme": "dark",
            "codes": ["H-02", "HR-01", "B-01", "S-02", "PF-01"],
            "notes": "Image-forward masonry body followed by the single permitted curated-design static message.",
        },
        {
            "id": "SEQ-LF-06",
            "label": "Light-Led Opportunity Close",
            "campaign_type": "long-form",
            "theme": "light-to-dark",
            "codes": ["H-04", "HR-02", "B-04", "S-04", "PF-01"],
            "notes": "Light opening, default dark editorial body, one opportunity message, and closing CTA.",
        },
        {
            "id": "SEQ-LF-07",
            "label": "Approved CFG-05 Continuity",
            "campaign_type": "long-form",
            "theme": "dark",
            "codes": ["H-01", "AI-01", "B-04", "S-01", "PF-01"],
            "notes": "Carries forward the approved two-column header and AI image hero, then adds the refined editorial body, single authority message, and pre-footer.",
        },
        {
            "id": "SEQ-IN-01",
            "label": "Dark Invite",
            "campaign_type": "invite",
            "theme": "dark",
            "codes": ["H-03", "B-03", "PF-01"],
            "notes": "Collaboration header and invite body without an additional hero image.",
        },
        {
            "id": "SEQ-IN-02",
            "label": "Dark Invite With Image Hero",
            "campaign_type": "invite",
            "theme": "dark",
            "codes": ["H-03", "AI-01", "B-03", "PF-01"],
            "notes": "Collaboration header, optional approved image hero, invite body, and closing CTA.",
        },
    ]
    options = []
    for preset in presets:
        if not all(code in entries_by_code for code in preset["codes"]):
            continue
        selected = [entries_by_code[code] for code in preset["codes"]]
        _validate_module_compatibility(preset["codes"], entries_by_code)
        options.append(
            {
                "id": preset["id"],
                "label": preset["label"],
                "campaign_type": preset["campaign_type"],
                "theme": preset["theme"],
                "selected_module_codes": preset["codes"],
                "selected_module_labels": [entry["label"] for entry in selected],
                "notes": preset["notes"],
                "preview_path": f"sequence-configurations/{preset['id']}.html",
            }
        )
    return {
        "gallery_version": SEQUENCE_GALLERY_VERSION,
        "option_count": len(options),
        "options": options,
    }


def _header_hero_pair_is_compatible(header: dict, hero: dict) -> bool:
    if not header.get("compatibility") and not hero.get("compatibility"):
        return True
    header_campaigns = set(header.get("campaign_types", []))
    hero_campaigns = set(hero.get("campaign_types", []))
    if header_campaigns and hero_campaigns and header_campaigns.isdisjoint(hero_campaigns):
        return False
    allowed_successors = set(header.get("compatibility", {}).get("successors", []))
    if allowed_successors and _entry_tokens(hero).isdisjoint(allowed_successors):
        return False
    allowed_predecessors = set(hero.get("compatibility", {}).get("predecessors", []))
    if allowed_predecessors and _entry_tokens(header).isdisjoint(allowed_predecessors):
        return False
    return True


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
            "selected_hero_configuration",
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
    selected_configuration = selection.get("selected_hero_configuration", "")
    if selected_configuration:
        if not isinstance(selected_configuration, str):
            raise CompositionError("composition selection.selected_hero_configuration must be a string")
        _validate_hero_configuration(selected_configuration, selected_codes, module_catalog)

    selected_entries = [entries_by_code[code] for code in selected_codes]
    plan = {
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
                **({"required": slot["required"]} if "required" in slot else {}),
                **({"omit_if_missing": slot["omit_if_missing"]} if "omit_if_missing" in slot else {}),
                **({"annotation_id": slot["annotation_id"]} if slot.get("annotation_id") else {}),
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
    if selected_configuration:
        plan["selected_hero_configuration"] = selected_configuration
    return plan


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
    selected_configuration = composition.get("selected_hero_configuration", "")
    if selected_configuration:
        if not isinstance(selected_configuration, str):
            raise CompositionError("composition.selected_hero_configuration must be a string")
        _validate_hero_configuration(selected_configuration, selected_codes, module_catalog)

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
    for name, definition in sorted(slots.items()):
        rules = definition.get("rules", []) if isinstance(definition, dict) else definition
        operations = sorted({rule["operation"] for rule in rules})
        required = sorted({rule["required_approval"] for rule in rules if "required_approval" in rule})
        allowed_kinds = definition.get("allowed_kinds", []) if isinstance(definition, dict) else []
        item = {
            "name": name,
            "slot_type": allowed_kinds[0] if len(allowed_kinds) == 1 else _slot_type(operations),
            "operations": operations,
            "required_approvals": required,
        }
        if isinstance(definition, dict):
            item.update(
                required=bool(definition.get("required", False)),
                omit_if_missing=bool(definition.get("omit_if_missing", False)),
                annotation_id=definition.get("annotation_id", ""),
            )
        summary.append(item)
    return summary


def _slot_type(operations: list[str]) -> str:
    if any(
        operation in {"replace_image_src", "replace_background_url", "annotation_replace_image"}
        for operation in operations
    ):
        return "image"
    if "annotation_repeat_pairs" in operations:
        return "amplified_list"
    if any(operation in {"annotation_repeat_text", "annotation_replace_list"} for operation in operations):
        return "text_list"
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
    if not any(
        entries_by_code[code]["module_type"] == "hero"
        or entries_by_code[code].get("layout_role") == "invite-body"
        for code in selected_codes
    ):
        raise CompositionError("Composition must include a hero or complete invite body module code")


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
    selected = [entries_by_code[code] for code in selected_codes]
    if any(entry.get("compatibility") for entry in selected):
        _validate_refined_sequence(selected)


def _validate_refined_sequence(selected: list[dict]) -> None:
    campaign_sets = [set(entry.get("campaign_types", [])) for entry in selected if entry.get("campaign_types")]
    if campaign_sets and not set.intersection(*campaign_sets):
        raise CompositionError("Selected modules do not share a compatible campaign type")

    groups: dict[str, list[dict]] = {}
    for entry in selected:
        compatibility = entry.get("compatibility", {})
        group = compatibility.get("exclusion_group")
        if group:
            groups.setdefault(group, []).append(entry)
    for group, entries in groups.items():
        limit = min(entry["compatibility"].get("max_from_group", 1) for entry in entries)
        if len(entries) > limit:
            raise CompositionError(
                f"Composition may include at most {limit} module(s) from {group}: "
                + ", ".join(entry["code"] for entry in entries)
            )

    for index, entry in enumerate(selected):
        compatibility = entry.get("compatibility", {})
        predecessor_tokens = {"start"} if index == 0 else _entry_tokens(selected[index - 1])
        successor_tokens = {"footer", "end"} if index == len(selected) - 1 else _entry_tokens(selected[index + 1])
        allowed_predecessors = set(compatibility.get("predecessors", []))
        allowed_successors = set(compatibility.get("successors", []))
        if allowed_predecessors and predecessor_tokens.isdisjoint(allowed_predecessors):
            raise CompositionError(
                f"{entry['code']} cannot follow {selected[index - 1]['code'] if index else 'start'}"
            )
        if allowed_successors and successor_tokens.isdisjoint(allowed_successors):
            raise CompositionError(
                f"{entry['code']} cannot precede "
                f"{selected[index + 1]['code'] if index + 1 < len(selected) else 'footer'}"
            )


def _entry_tokens(entry: dict) -> set[str]:
    tokens = {
        entry["code"],
        entry["scaffold_module_id"],
        entry["module_type"],
        entry.get("module_family", ""),
        entry.get("layout_role", ""),
    } - {""}
    for value in (entry.get("module_family", ""), entry.get("layout_role", "")):
        tokens.update(part for part in value.split("-") if part)
    return tokens


def _metadata_companion_rules(compatibility: dict) -> list[str]:
    rules = []
    if compatibility.get("predecessors"):
        rules.append("Allowed after: " + ", ".join(compatibility["predecessors"]) + ".")
    if compatibility.get("successors"):
        rules.append("Allowed before: " + ", ".join(compatibility["successors"]) + ".")
    if compatibility.get("exclusion_group"):
        rules.append(
            "At most "
            + str(compatibility.get("max_from_group", 1))
            + " from "
            + compatibility["exclusion_group"]
            + "."
        )
    return rules or ["No additional companion rule."]


def _validate_hero_configuration(configuration_id: str, selected_codes: list[str], module_catalog: dict) -> None:
    options = {option["id"]: option for option in build_hero_configurations(module_catalog)["options"]}
    if configuration_id not in options:
        raise CompositionError(f"Unknown hero configuration: {configuration_id}")
    entries_by_code = {entry["code"]: entry for entry in module_catalog["entries"]}
    selected_header_hero = [
        code for code in selected_codes if entries_by_code[code]["module_type"] in {"header", "hero"}
    ]
    if selected_header_hero != options[configuration_id]["selected_module_codes"]:
        raise CompositionError(
            f"Hero configuration {configuration_id} requires module codes: "
            + ", ".join(options[configuration_id]["selected_module_codes"])
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
        "selected_hero_configuration": composition.get("selected_hero_configuration", ""),
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
    lines.append("Open `hero-gallery.html` to choose a complete labeled `CFG-*` header/hero configuration.")
    lines.append("Open `module-gallery.html` to inspect every selectable block in isolation.")
    lines.append("For refined scaffolds, open `sequence-gallery.html` to review complete `SEQ-*` compositions.")
    return "\n".join(lines) + "\n"


def _module_gallery_html(module_catalog: dict) -> str:
    cards = []
    for entry in module_catalog["entries"]:
        slots = ", ".join(slot["name"] for slot in entry["editable_slots"]) or "Locked content"
        cards.append(
            f"""
            <article class="option" data-module-code="{escape(entry['code'])}">
              <header>
                <div><strong>{escape(entry['code'])}</strong><span>{escape(entry['module_family'])}</span></div>
                <h2>{escape(entry['label'])}</h2>
                <p>{escape(entry['summary'])}</p>
              </header>
              <iframe src="{escape(entry['preview']['path'])}" title="{escape(entry['code'] + ' ' + entry['label'])}"></iframe>
              <dl>
                <div><dt>Role</dt><dd>{escape(entry['layout_role'])}</dd></div>
                <div><dt>Theme</dt><dd>{escape(str(entry['theme'].get('default', 'scaffold-defined')))}</dd></div>
                <div><dt>Editable slots</dt><dd>{escape(slots)}</dd></div>
              </dl>
            </article>"""
        )
    return _review_gallery_shell(
        title="Rider Phase 16 Module Gallery",
        intro="Inspect each selectable block in isolation. Stable codes and slot names are shown outside the email preview.",
        content=f'<div class="options">{"".join(cards)}</div>',
        iframe_height=420,
    )


def _sequence_gallery_html(sequences: dict) -> str:
    sections = []
    campaign_order = (("long-form", "Long-Form Email Sequences"), ("invite", "Invite Sequences"))
    for campaign_type, heading in campaign_order:
        cards = []
        for option in sequences["options"]:
            if option["campaign_type"] != campaign_type:
                continue
            codes = " + ".join(option["selected_module_codes"])
            module_path = " → ".join(option["selected_module_labels"])
            cards.append(
                f"""
                <article class="option sequence" data-sequence-id="{escape(option['id'])}">
                  <header>
                    <div><strong>{escape(option['id'])}</strong><span>{escape(option['theme'])}</span></div>
                    <h2>{escape(option['label'])}</h2>
                    <p class="codes">{escape(codes)}</p>
                  </header>
                  <iframe src="{escape(option['preview_path'])}" title="{escape(option['id'] + ' ' + option['label'])}"></iframe>
                  <dl>
                    <div><dt>Campaign</dt><dd>{escape(option['campaign_type'])}</dd></div>
                    <div><dt>Sequence</dt><dd>{escape(module_path)}</dd></div>
                    <div><dt>Review note</dt><dd>{escape(option['notes'])}</dd></div>
                  </dl>
                </article>"""
            )
        if cards:
            sections.append(f'<section><h2 class="group-title">{escape(heading)}</h2>{"".join(cards)}</section>')
    return _review_gallery_shell(
        title="Rider Phase 16 Sequence Gallery",
        intro="Review complete, runtime-valid block sequences before approving a new creative baseline. Footers are omitted from these layout previews.",
        content="".join(sections),
        iframe_height=860,
        single_column=True,
    )


def _review_gallery_shell(
    *, title: str, intro: str, content: str, iframe_height: int, single_column: bool = False
) -> str:
    columns = "minmax(0, 1fr)" if single_column else "repeat(auto-fit, minmax(360px, 1fr))"
    resize_script = """
  <script>
    function sizePreview(frame) {
      const previewDocument = frame.contentWindow && frame.contentWindow.document;
      if (!previewDocument) return;
      frame.style.height = '1px';
      const documentElement = previewDocument.documentElement;
      const body = previewDocument.body;
      frame.style.height = Math.max(documentElement.scrollHeight, body ? body.scrollHeight : 0) + 'px';
    }
    window.addEventListener('load', () => {
      document.querySelectorAll('iframe').forEach((frame) => {
        frame.addEventListener('load', () => sizePreview(frame));
        sizePreview(frame);
      });
    });
  </script>"""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #f4f4f2; color: #151515; font-family: Arial, sans-serif; }}
    .page-header {{ padding: 28px 32px 20px; background: #151515; color: #fff; }}
    .page-header h1 {{ margin: 0 0 8px; font-size: 26px; letter-spacing: 0; }}
    .page-header p {{ margin: 0; max-width: 820px; font-size: 14px; line-height: 1.5; }}
    main {{ padding: 24px; }}
    section + section {{ margin-top: 32px; }}
    .group-title {{ margin: 0 0 12px; font-size: 19px; letter-spacing: 0; }}
    .options {{ display: grid; grid-template-columns: {columns}; gap: 20px; }}
    section .option + .option {{ margin-top: 20px; }}
    .option {{ min-width: 0; border: 1px solid #c9c9c4; background: #fff; }}
    .option > header {{ padding: 18px 20px; border-bottom: 1px solid #d8d8d2; }}
    .option > header div {{ display: flex; justify-content: space-between; gap: 12px; font-size: 12px; text-transform: uppercase; }}
    .option > header span {{ color: #666; }}
    .option h2 {{ margin: 12px 0 7px; font-size: 17px; line-height: 1.3; letter-spacing: 0; }}
    .option p {{ margin: 0; color: #555; font-size: 12px; line-height: 1.45; }}
    .codes {{ font-family: monospace; }}
    iframe {{ display: block; width: 100%; height: {iframe_height}px; border: 0; background: #eee; }}
    dl {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); margin: 0; border-top: 1px solid #d8d8d2; }}
    dl div {{ min-width: 0; padding: 12px; border-right: 1px solid #d8d8d2; }}
    dl div:last-child {{ border-right: 0; }}
    dt {{ margin-bottom: 5px; color: #666; font-size: 10px; text-transform: uppercase; }}
    dd {{ margin: 0; overflow-wrap: anywhere; font-size: 12px; line-height: 1.4; }}
    @media (max-width: 620px) {{
      .page-header {{ padding: 22px 18px; }}
      main {{ padding: 16px 12px 24px; }}
      .options {{ grid-template-columns: minmax(0, 1fr); }}
      iframe {{ height: 430px; }}
      dl {{ grid-template-columns: 1fr; }}
      dl div {{ border-right: 0; border-bottom: 1px solid #d8d8d2; }}
    }}
  </style>
</head>
<body>
  <header class="page-header">
    <h1>{escape(title)}</h1>
    <p>{escape(intro)}</p>
  </header>
  <main>{content}</main>
{resize_script}
</body>
</html>
"""


def _gallery_html(configurations: dict) -> str:
    grouped_options = []
    for option in configurations["options"]:
        if not grouped_options or grouped_options[-1][0] != option["group"]:
            grouped_options.append((option["group"], option["group_label"], []))
        grouped_options[-1][2].append(option)

    sections = []
    for group, group_label, options in grouped_options:
        cards = []
        for option in options:
            cards.append(_gallery_card(option))
        sections.append(
            f'<section id="{escape(group)}"><h2 class="group-title">{escape(group_label)}</h2>'
            f'<div class="options">{"".join(cards)}</div></section>'
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rider Header And Hero Configurations</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #f4f4f2; color: #151515; font-family: Arial, sans-serif; }}
    .page-header {{ padding: 28px 32px 20px; background: #151515; color: #fff; }}
    .page-header h1 {{ margin: 0 0 8px; font-size: 26px; letter-spacing: 0; }}
    .page-header p {{ margin: 0; max-width: 760px; font-size: 14px; line-height: 1.5; }}
    main {{ padding: 12px 24px 32px; }}
    section {{ padding-top: 20px; }}
    .group-title {{ margin: 0 0 12px; font-size: 18px; letter-spacing: 0; }}
    .options {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 20px; }}
    .option {{ min-width: 0; border: 1px solid #c9c9c4; background: #fff; }}
    .option > header {{ min-height: 128px; padding: 18px 20px; border-bottom: 1px solid #d8d8d2; }}
    .option > header div {{ display: flex; justify-content: space-between; gap: 12px; font-size: 12px; text-transform: uppercase; }}
    .option > header span {{ color: #666; }}
    .option h3 {{ margin: 14px 0 8px; font-size: 17px; line-height: 1.25; letter-spacing: 0; }}
    .codes {{ margin: 0; font-family: monospace; font-size: 12px; }}
    iframe {{ display: block; width: 100%; height: 520px; border: 0; background: #eee; }}
    dl {{ display: grid; grid-template-columns: repeat(3, 1fr); margin: 0; border-top: 1px solid #d8d8d2; }}
    dl div {{ min-width: 0; padding: 12px; border-right: 1px solid #d8d8d2; }}
    dl div:last-child {{ border-right: 0; }}
    dt {{ margin-bottom: 5px; color: #666; font-size: 10px; text-transform: uppercase; }}
    dd {{ margin: 0; font-size: 12px; line-height: 1.35; }}
    .notes {{ min-height: 58px; margin: 0; padding: 12px 20px 16px; color: #555; font-size: 12px; line-height: 1.4; }}
    @media (max-width: 520px) {{
      .page-header {{ padding: 22px 18px; }}
      main {{ padding: 4px 12px 24px; }}
      .options {{ grid-template-columns: minmax(0, 1fr); }}
      iframe {{ height: 430px; }}
      dl {{ grid-template-columns: 1fr; }}
      dl div {{ border-right: 0; border-bottom: 1px solid #d8d8d2; }}
    }}
  </style>
</head>
<body>
  <header class="page-header">
    <h1>Rider Header And Hero Configurations</h1>
    <p>Select one stable CFG code before image generation. Each option is a compatible complete configuration, not a final email-client rendering.</p>
  </header>
  <main>{''.join(sections)}</main>
</body>
</html>
"""


def _gallery_card(option: dict) -> str:
        codes = " + ".join(option["selected_module_codes"])
        notes = " ".join(option["compatibility_notes"])
        return f"""
            <article class="option" data-configuration="{escape(option['id'])}">
              <header>
                <div><strong>{escape(option['id'])}</strong><span>{escape(option['group'])}</span></div>
                <h3>{escape(option['label'])}</h3>
                <p class="codes">{escape(codes)}</p>
              </header>
              <iframe src="{escape(option['preview_path'])}" title="{escape(option['id'] + ' ' + option['label'])}"></iframe>
              <dl>
                <div><dt>Header</dt><dd>{'Included' if option['includes_header'] else 'None'}</dd></div>
                <div><dt>Text</dt><dd>{'Live HTML supported' if option['live_text_support'] else 'Image-led or locked'}</dd></div>
                <div><dt>Image</dt><dd>{'Required' if option['image_required'] else 'Not required'}</dd></div>
              </dl>
              <p class="notes">{escape(notes)}</p>
            </article>"""


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
