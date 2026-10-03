from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from tools.email_scaffold import (
    END_MARKER_COLOR,
    START_MARKER_COLOR,
    STATIC_END_MARKER_COLOR,
    STATIC_START_MARKER_COLOR,
    ScaffoldError,
    find_module_boundaries,
    parse_rows,
)


STATIC_BLOCK_LABEL = "STATIC BLOCK"
FOOTER_MODULES = {
    "BRANDED FOOTER",
    "OUTSIDE-BROKER CUSTOMIZABLE FOOTER",
    "IN-HOUSE AGENT FOOTER",
}


@dataclass(frozen=True)
class ModuleMetadata:
    id: str
    label: str
    kind: str
    includes_header: bool = False
    locked: bool = False
    summary: str = ""


@dataclass(frozen=True)
class Scaffold:
    html: str
    rows: tuple
    boundaries: dict[str, object]
    static_boundaries: dict[str, object]
    metadata: dict[str, ModuleMetadata]
    row1_html: str
    prefix: str
    suffix: str
    slot_map: dict


def load_scaffold(scaffold_path: Path, slot_map_path: Path, metadata_path: Path | None = None) -> Scaffold:
    html = scaffold_path.read_text(encoding="utf-8")
    rows = tuple(parse_rows(html))
    boundaries_list = find_module_boundaries(rows)
    _validate_boundary_marker_types(boundaries_list, rows)
    boundaries, static_boundaries = _index_boundaries(boundaries_list)
    if rows[0].number != 1:
        raise ScaffoldError("Scaffold row 1 is required")
    slot_map = json.loads(slot_map_path.read_text(encoding="utf-8"))
    metadata = _load_metadata(metadata_path, set(boundaries) | set(static_boundaries))
    _validate_slot_map(slot_map, boundaries)
    return Scaffold(
        html=html,
        rows=rows,
        boundaries=boundaries,
        static_boundaries=static_boundaries,
        metadata=metadata,
        row1_html=rows[0].html,
        prefix=html[: rows[0].start],
        suffix=html[rows[-1].end :],
        slot_map=slot_map,
    )


def catalog(scaffold: Scaffold) -> dict[str, tuple[int, ...]]:
    return {
        module_id: tuple(_content_rows_for(scaffold, module_id))
        for module_id, boundary in sorted(
            {**scaffold.boundaries, **scaffold.static_boundaries}.items(),
            key=lambda item: item[1].start_marker_row,
        )
    }


def module_rows(scaffold: Scaffold, module_id: str) -> list[str]:
    if module_id not in scaffold.boundaries and module_id not in scaffold.static_boundaries:
        raise ScaffoldError(f"Unknown Rider module: {module_id}")
    return [scaffold.rows[number - 1].html for number in _content_rows_for(scaffold, module_id)]


def module_kind(scaffold: Scaffold, module_id: str) -> str:
    metadata = scaffold.metadata.get(module_id)
    return metadata.kind if metadata else "body"


def module_includes_header(scaffold: Scaffold, module_id: str) -> bool:
    metadata = scaffold.metadata.get(module_id)
    return bool(metadata and metadata.includes_header)


def compose_html(scaffold: Scaffold, rows: list[str]) -> str:
    return scaffold.prefix + scaffold.row1_html + "".join(rows) + scaffold.suffix


def static_content_html(scaffold: Scaffold) -> dict[str, str]:
    return {module_id: "".join(module_rows(scaffold, module_id)) for module_id in scaffold.static_boundaries}


def _index_boundaries(boundaries_list: list[object]) -> tuple[dict[str, object], dict[str, object]]:
    boundaries: dict[str, object] = {}
    static_boundaries: dict[str, object] = {}
    static_count = 0
    for boundary in sorted(boundaries_list, key=lambda item: item.start_marker_row):
        if boundary.label == STATIC_BLOCK_LABEL:
            static_count += 1
            static_boundaries[f"{STATIC_BLOCK_LABEL} {static_count}"] = boundary
            continue
        if boundary.label in boundaries:
            raise ScaffoldError(f"Duplicate scaffold module label: {boundary.label}")
        boundaries[boundary.label] = boundary
    return boundaries, static_boundaries


def _validate_boundary_marker_types(boundaries_list: list[object], rows: tuple) -> None:
    for boundary in boundaries_list:
        start_colors = set(rows[boundary.start_marker_row - 1].style_colors)
        end_colors = set(rows[boundary.end_marker_row - 1].style_colors)
        if boundary.label == STATIC_BLOCK_LABEL:
            expected_start, expected_end = STATIC_START_MARKER_COLOR, STATIC_END_MARKER_COLOR
        else:
            expected_start, expected_end = START_MARKER_COLOR, END_MARKER_COLOR
        if expected_start not in start_colors or expected_end not in end_colors:
            raise ScaffoldError(
                f"{boundary.label} uses the wrong marker color pair at rows "
                f"{boundary.start_marker_row}-{boundary.end_marker_row}"
            )


def _content_rows_for(scaffold: Scaffold, module_id: str) -> tuple[int, ...]:
    if module_id in scaffold.static_boundaries:
        return scaffold.static_boundaries[module_id].content_rows
    boundary = scaffold.boundaries[module_id]
    static_ranges = {
        row_number
        for static in scaffold.static_boundaries.values()
        if boundary.start_marker_row < static.start_marker_row and static.end_marker_row < boundary.end_marker_row
        for row_number in range(static.start_marker_row, static.end_marker_row + 1)
    }
    return tuple(row_number for row_number in boundary.content_rows if row_number not in static_ranges)


def _load_metadata(metadata_path: Path | None, module_ids: set[str]) -> dict[str, ModuleMetadata]:
    if metadata_path is None:
        return {module_id: _infer_metadata(module_id) for module_id in module_ids}
    raw = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("modules"), list):
        raise ScaffoldError("Module metadata must contain a modules array")
    metadata: dict[str, ModuleMetadata] = {}
    for index, item in enumerate(raw["modules"]):
        if not isinstance(item, dict):
            raise ScaffoldError(f"Module metadata entry {index} must be an object")
        unknown = sorted(set(item) - {"id", "label", "kind", "includes_header", "locked", "summary"})
        if unknown:
            raise ScaffoldError(
                f"Module metadata entry {index} has unknown field(s): {', '.join(unknown)}"
            )
        module_id = item.get("id")
        if not isinstance(module_id, str) or not module_id:
            raise ScaffoldError(f"Module metadata entry {index} has invalid id")
        kind = item.get("kind")
        if kind not in {"header", "hero", "body", "static", "footer"}:
            raise ScaffoldError(f"Module metadata {module_id} has invalid kind")
        metadata[module_id] = ModuleMetadata(
            id=module_id,
            label=item.get("label", module_id),
            kind=kind,
            includes_header=bool(item.get("includes_header", False)),
            locked=bool(item.get("locked", False)),
            summary=item.get("summary", ""),
        )
    missing = sorted(module_ids - set(metadata))
    unknown = sorted(set(metadata) - module_ids)
    if missing:
        raise ScaffoldError("Module metadata missing module(s): " + ", ".join(missing))
    if unknown:
        raise ScaffoldError("Module metadata references unknown module(s): " + ", ".join(unknown))
    return metadata


def _infer_metadata(module_id: str) -> ModuleMetadata:
    if module_id.startswith(STATIC_BLOCK_LABEL):
        return ModuleMetadata(module_id, STATIC_BLOCK_LABEL, "static", locked=True)
    if module_id in FOOTER_MODULES:
        return ModuleMetadata(module_id, module_id, "footer")
    if "HEADER & HERO" in module_id:
        return ModuleMetadata(module_id, module_id, "hero", includes_header=True)
    if "HEADER" in module_id:
        return ModuleMetadata(module_id, module_id, "header")
    if "HERO" in module_id or "AI GENERATED IMAGE" in module_id:
        return ModuleMetadata(module_id, module_id, "hero")
    return ModuleMetadata(module_id, module_id, "body")


def _validate_slot_map(slot_map: object, boundaries: dict[str, object]) -> None:
    if not isinstance(slot_map, dict):
        raise ScaffoldError("Slot map must be an object")
    unknown_modules = sorted(set(slot_map) - set(boundaries))
    if unknown_modules:
        raise ScaffoldError("Slot map references unknown module(s): " + ", ".join(unknown_modules))
    for module_id, slots in slot_map.items():
        if not isinstance(slots, dict):
            raise ScaffoldError(f"Slot map for {module_id} must be an object")
        for slot_name, rules in slots.items():
            if not isinstance(slot_name, str) or not slot_name:
                raise ScaffoldError(f"Invalid slot name in {module_id}")
            if not isinstance(rules, list) or not rules:
                raise ScaffoldError(f"Slot map {module_id}.{slot_name} must be a non-empty list")
            for rule in rules:
                if not isinstance(rule, dict):
                    raise ScaffoldError(f"Slot map {module_id}.{slot_name} rule must be an object")
                unknown = sorted(set(rule) - {"operation", "anchor", "text_anchor", "required_approval"})
                if unknown:
                    raise ScaffoldError(
                        f"Slot map {module_id}.{slot_name} rule has unknown field(s): {', '.join(unknown)}"
                    )
                required = {"operation", "anchor"}
                missing = sorted(required - set(rule))
                if missing:
                    raise ScaffoldError(f"Slot map {module_id}.{slot_name} is missing {missing}")
                if rule["operation"] == "replace_text_in_context" and not isinstance(rule.get("text_anchor"), str):
                    raise ScaffoldError(
                        f"Slot map {module_id}.{slot_name} contextual rule requires text_anchor"
                    )
