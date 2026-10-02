from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from tools.email_scaffold import ScaffoldError, find_module_boundaries, parse_rows


FOOTER_MODULES = {
    "BRANDED FOOTER",
    "OUTSIDE-BROKER CUSTOMIZABLE FOOTER",
    "IN-HOUSE AGENT FOOTER",
}
HERO_MODULES = {
    "TWO-COLUMN HEADER",
    "HERO - DARK FRAMED LAYOUT",
    "INVITE - TWO-COLUMN HEADER - COLLABORATION",
    "HERO - FULL-WIDTH WITH LIVE TEXT HEADING AND LOGO",
    "HERO - LIGHT LAYOUT - FRAMED",
}


@dataclass(frozen=True)
class Scaffold:
    html: str
    rows: tuple
    boundaries: dict[str, object]
    row1_html: str
    prefix: str
    suffix: str
    slot_map: dict


def load_scaffold(scaffold_path: Path, slot_map_path: Path) -> Scaffold:
    html = scaffold_path.read_text(encoding="utf-8")
    rows = tuple(parse_rows(html))
    boundaries_list = find_module_boundaries(rows)
    boundaries = {boundary.label: boundary for boundary in boundaries_list}
    if len(boundaries) != len(boundaries_list):
        raise ScaffoldError("Duplicate scaffold module labels")
    if rows[0].number != 1:
        raise ScaffoldError("Scaffold row 1 is required")
    slot_map = json.loads(slot_map_path.read_text(encoding="utf-8"))
    _validate_slot_map(slot_map, boundaries)
    return Scaffold(
        html=html,
        rows=rows,
        boundaries=boundaries,
        row1_html=rows[0].html,
        prefix=html[: rows[0].start],
        suffix=html[rows[-1].end :],
        slot_map=slot_map,
    )


def catalog(scaffold: Scaffold) -> dict[str, tuple[int, ...]]:
    return {
        label: tuple(boundary.content_rows)
        for label, boundary in sorted(
            scaffold.boundaries.items(), key=lambda item: item[1].start_marker_row
        )
    }


def module_rows(scaffold: Scaffold, module_id: str) -> list[str]:
    if module_id not in scaffold.boundaries:
        raise ScaffoldError(f"Unknown Rider module: {module_id}")
    return [scaffold.rows[number - 1].html for number in scaffold.boundaries[module_id].content_rows]


def compose_html(scaffold: Scaffold, rows: list[str]) -> str:
    return scaffold.prefix + scaffold.row1_html + "".join(rows) + scaffold.suffix


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
