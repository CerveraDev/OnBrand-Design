from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from tools.email_scaffold import (
    END_MARKER_COLOR,
    ModuleBoundary,
    START_MARKER_COLOR,
    STATIC_END_MARKER_COLOR,
    STATIC_START_MARKER_COLOR,
    ScaffoldError,
    find_annotation_boundaries,
    find_module_boundaries,
    load_block_metadata,
    parse_marker_elements,
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
    code: str = ""
    family: str = ""
    layout_role: str = ""
    theme: dict | None = None
    compatibility: dict | None = None
    campaign_types: tuple[str, ...] = ()
    image: dict | None = None
    creative_guidance: dict | None = None


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
    render_rows: tuple[str, ...] = ()
    annotation_anchors: dict[str, str] | None = None
    refined: bool = False


def load_scaffold(scaffold_path: Path, slot_map_path: Path, metadata_path: Path | None = None) -> Scaffold:
    html = scaffold_path.read_text(encoding="utf-8")
    rows = tuple(parse_rows(html))
    boundaries_list = find_module_boundaries(rows)
    _validate_boundary_marker_types(boundaries_list, rows)
    if rows[0].number != 1:
        raise ScaffoldError("Scaffold row 1 is required")
    metadata_raw = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path else None
    refined = bool(isinstance(metadata_raw, dict) and metadata_raw.get("schema_version") == "1.0")
    annotation_anchors: dict[str, str] = {}
    if refined:
        annotations = find_annotation_boundaries(html, rows)
        metadata_raw = load_block_metadata(metadata_path, scaffold_path, boundaries_list, annotations)
        boundaries, static_boundaries, metadata, annotation_anchors = _load_refined_structure(
            boundaries_list,
            annotations,
            metadata_raw,
            html,
        )
    else:
        boundaries, static_boundaries = _index_boundaries(boundaries_list)
        metadata = _load_metadata(metadata_path, set(boundaries) | set(static_boundaries))
    slot_map = json.loads(slot_map_path.read_text(encoding="utf-8"))
    slot_map = _prepare_slot_map(slot_map, boundaries, annotation_anchors)
    marker_elements = parse_marker_elements(html, rows)
    render_rows = tuple(_row_without_inline_markers(row, marker_elements) for row in rows)
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
        render_rows=render_rows,
        annotation_anchors=annotation_anchors,
        refined=refined,
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
    source_rows = scaffold.render_rows or tuple(row.html for row in scaffold.rows)
    return [source_rows[number - 1] for number in _content_rows_for(scaffold, module_id)]


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
        if boundary.label.startswith((STATIC_BLOCK_LABEL, "SEMI-STATIC")):
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


def _prepare_slot_map(
    slot_map: object,
    boundaries: dict[str, object],
    annotation_anchors: dict[str, str],
) -> dict:
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
            if isinstance(rules, list):
                definition = {"rules": rules}
            elif isinstance(rules, dict):
                definition = dict(rules)
                unknown_definition = sorted(
                    set(definition)
                    - {
                        "annotation_id",
                        "required",
                        "omit_if_missing",
                        "allowed_kinds",
                        "min_words",
                        "max_words",
                        "rules",
                    }
                )
                if unknown_definition:
                    raise ScaffoldError(
                        f"Slot map {module_id}.{slot_name} has unknown definition field(s): "
                        + ", ".join(unknown_definition)
                    )
            else:
                raise ScaffoldError(f"Slot map {module_id}.{slot_name} must be a list or object")
            rule_list = definition.get("rules")
            if not isinstance(rule_list, list) or not rule_list:
                raise ScaffoldError(f"Slot map {module_id}.{slot_name}.rules must be a non-empty list")
            annotation_id = definition.get("annotation_id")
            if annotation_id is not None:
                if annotation_id not in annotation_anchors:
                    raise ScaffoldError(
                        f"Slot map {module_id}.{slot_name} references unknown annotation {annotation_id}"
                    )
                definition["annotation_anchor"] = annotation_anchors[annotation_id]
            for rule in rule_list:
                if not isinstance(rule, dict):
                    raise ScaffoldError(f"Slot map {module_id}.{slot_name} rule must be an object")
                unknown = sorted(
                    set(rule)
                    - {
                        "operation",
                        "anchor",
                        "text_anchor",
                        "secondary_text_anchor",
                        "list_items_anchor",
                        "item_template",
                        "required_approval",
                    }
                )
                if unknown:
                    raise ScaffoldError(
                        f"Slot map {module_id}.{slot_name} rule has unknown field(s): {', '.join(unknown)}"
                    )
                if "operation" not in rule:
                    raise ScaffoldError(f"Slot map {module_id}.{slot_name} rule requires operation")
                if not rule["operation"].startswith("annotation_") and "anchor" not in rule:
                    raise ScaffoldError(f"Slot map {module_id}.{slot_name} rule requires anchor")
                if rule["operation"] == "replace_text_in_context" and not isinstance(rule.get("text_anchor"), str):
                    raise ScaffoldError(
                        f"Slot map {module_id}.{slot_name} contextual rule requires text_anchor"
                    )
            slots[slot_name] = definition if isinstance(rules, dict) else rule_list
    return slot_map


def _load_refined_structure(boundaries_list, annotations, raw: dict, html: str):
    module_sources = _entries_by_source(raw["modules"])
    annotation_sources = _entries_by_source(raw["annotations"])
    boundaries: dict[str, object] = {}
    static_boundaries: dict[str, object] = {}
    metadata: dict[str, ModuleMetadata] = {}
    counts: dict[str, int] = {}
    for boundary in sorted(boundaries_list, key=lambda item: item.start_marker_row):
        counts[boundary.label] = counts.get(boundary.label, 0) + 1
        entry = module_sources[(boundary.label, counts[boundary.label])]
        module_id = entry["id"]
        module_metadata = _refined_module_metadata(entry)
        target = static_boundaries if module_metadata.kind == "static" else boundaries
        target[module_id] = boundary
        metadata[module_id] = module_metadata

    annotation_anchors: dict[str, str] = {}
    counts.clear()
    markers = parse_marker_elements(html)
    for annotation in annotations:
        counts[annotation.label] = counts.get(annotation.label, 0) + 1
        entry = annotation_sources[(annotation.label, counts[annotation.label])]
        annotation_id = entry["id"]
        annotation_anchors[annotation_id] = _annotation_content_without_markers(
            annotation, markers, html
        )
        composition = entry.get("composition")
        if composition and composition.get("standalone"):
            boundaries[annotation_id] = ModuleBoundary(
                label=annotation.label,
                start_marker_row=annotation.start_marker.row_number,
                end_marker_row=annotation.end_marker.row_number,
                content_rows=annotation.content_rows,
            )
            metadata[annotation_id] = ModuleMetadata(
                id=annotation_id,
                label=composition["label"],
                kind="body",
                summary=composition["summary"],
                code=composition["code"],
                family=composition["family"],
                layout_role=composition["layout_role"],
                theme=composition["theme"],
                compatibility=composition["compatibility"],
                campaign_types=tuple(composition["campaign_types"]),
                image=composition["image"],
            )
    return boundaries, static_boundaries, metadata, annotation_anchors


def _entries_by_source(entries: list[dict]) -> dict[tuple[str, int], dict]:
    return {
        (entry["source"]["label"], entry["source"].get("occurrence", 1)): entry
        for entry in entries
    }


def _refined_module_metadata(entry: dict) -> ModuleMetadata:
    family = entry["family"]
    kind = family if family in {"header", "hero", "static", "footer"} else "body"
    return ModuleMetadata(
        id=entry["id"],
        label=entry["label"],
        kind=kind,
        includes_header=bool(entry["includes_header"]),
        locked=family == "static",
        summary=entry["label"],
        code=entry["code"],
        family=family,
        layout_role=entry["layout_role"],
        theme=entry["theme"],
        compatibility=entry["compatibility"],
        campaign_types=tuple(entry["campaign_types"]),
        image=entry["image"],
        creative_guidance=entry.get("creative_guidance", {}),
    )


def _row_without_inline_markers(row, markers) -> str:
    ranges = []
    for marker in markers:
        if marker.row_number != row.number or marker.is_full_row:
            continue
        start, end = _marker_table_range(marker, row.html, offset=row.start)
        ranges.append((start, end))
    rendered = row.html
    for start, end in sorted(ranges, reverse=True):
        rendered = rendered[:start] + rendered[end:]
    return rendered


def _annotation_content_without_markers(annotation, markers, html: str) -> str:
    _, start = _marker_table_range(annotation.start_marker, html)
    end, _ = _marker_table_range(annotation.end_marker, html)
    content = html[start:end]
    ranges = []
    for marker in markers:
        if not (start <= marker.start and marker.end <= end):
            continue
        marker_start, marker_end = _marker_table_range(marker, html)
        ranges.append((marker_start - start, marker_end - start))
    for range_start, range_end in sorted(ranges, reverse=True):
        content = content[:range_start] + content[range_end:]
    return content


def _marker_table_range(marker, html: str, *, offset: int = 0) -> tuple[int, int]:
    local_start = marker.start - offset
    local_end = marker.end - offset
    table_start = html.rfind("<table", 0, local_start)
    table_end_start = html.find("</table>", local_end)
    if table_start < 0 or table_end_start < 0:
        raise ScaffoldError(
            f"Marker {marker.label!r} in row {marker.row_number} is not inside a table block"
        )
    return table_start, table_end_start + len("</table>")
