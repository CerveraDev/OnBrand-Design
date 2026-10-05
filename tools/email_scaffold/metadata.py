from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Iterable

from .parser import AnnotationBoundary, ModuleBoundary, ScaffoldError


REQUIRED_MODULE_FIELDS = {
    "id",
    "code",
    "source",
    "label",
    "family",
    "layout_role",
    "theme",
    "includes_header",
    "content",
    "image",
    "campaign_types",
    "compatibility",
    "client_behavior",
}
REQUIRED_ANNOTATION_FIELDS = {
    "id",
    "source",
    "parent_module_id",
    "parent_annotation_id",
    "role",
    "value_type",
    "required",
    "repeatable",
    "generation",
    "constraints",
    "placeholder_policy",
}


def load_block_metadata(
    metadata_path: Path,
    scaffold_path: Path,
    modules: Iterable[ModuleBoundary],
    annotations: Iterable[AnnotationBoundary],
) -> dict:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    scaffold_html = scaffold_path.read_text(encoding="utf-8")
    validate_block_metadata(metadata, scaffold_html, modules, annotations)
    return metadata


def validate_block_metadata(
    metadata: object,
    scaffold_html: str,
    modules: Iterable[ModuleBoundary],
    annotations: Iterable[AnnotationBoundary],
) -> None:
    if not isinstance(metadata, dict) or metadata.get("schema_version") != "1.0":
        raise ScaffoldError("Block metadata must be a version 1.0 object")
    source = metadata.get("source")
    if not isinstance(source, dict):
        raise ScaffoldError("Block metadata requires a source object")
    expected_hash = hashlib.sha256(scaffold_html.encode("utf-8")).hexdigest()
    if source.get("sha256") != expected_hash:
        raise ScaffoldError("Block metadata source checksum does not match the scaffold")

    module_list = list(modules)
    annotation_list = list(annotations)
    expected_counts = {
        "row_count": max((boundary.end_marker_row for boundary in module_list), default=0),
        "module_count": len(module_list),
        "annotation_count": len(annotation_list),
    }
    for field, expected in expected_counts.items():
        if source.get(field) != expected:
            raise ScaffoldError(
                f"Block metadata source {field} is {source.get(field)!r}; expected {expected}"
            )
    _validate_entries(metadata.get("modules"), REQUIRED_MODULE_FIELDS, "module")
    _validate_entries(metadata.get("annotations"), REQUIRED_ANNOTATION_FIELDS, "annotation")
    module_entries = metadata["modules"]
    annotation_entries = metadata["annotations"]
    for entry in module_entries:
        _validate_creative_guidance(entry)
    _validate_unique(module_entries + annotation_entries, "id")
    _validate_unique(module_entries, "code")

    module_lookup = _occurrence_lookup(
        (boundary.label, boundary.start_marker_row, boundary.end_marker_row)
        for boundary in module_list
    )
    annotation_lookup = _occurrence_lookup(
        (
            boundary.label,
            boundary.start_marker.row_number,
            boundary.end_marker.row_number,
        )
        for boundary in annotation_list
    )
    module_ids = _validate_source_coverage(module_entries, module_lookup, "module")
    annotation_ids = _validate_source_coverage(
        annotation_entries, annotation_lookup, "annotation"
    )

    module_id_by_label = {
        boundary.label: module_ids[(boundary.label, occurrence)]
        for boundary, occurrence in _with_occurrences(module_list, lambda item: item.label)
    }
    annotations_by_source = {
        (entry["source"]["label"], entry["source"].get("occurrence", 1)): entry
        for entry in annotation_entries
    }
    annotations_by_id = {entry["id"]: entry for entry in annotation_entries}
    annotation_boundaries_by_source = {
        (boundary.label, occurrence): boundary
        for boundary, occurrence in _with_occurrences(
            annotation_list, lambda item: item.label
        )
    }
    for boundary, occurrence in _with_occurrences(annotation_list, lambda item: item.label):
        entry = annotations_by_source[(boundary.label, occurrence)]
        expected_module = (
            module_id_by_label.get(boundary.parent_module_label)
            if boundary.parent_module_label
            else None
        )
        if entry["parent_module_id"] != expected_module:
            raise ScaffoldError(
                f"Annotation {entry['id']} has parent_module_id {entry['parent_module_id']!r}; "
                f"expected {expected_module!r}"
            )
        declared_parent_id = entry["parent_annotation_id"]
        if boundary.parent_annotation_label is None and declared_parent_id is not None:
            raise ScaffoldError(
                f"Annotation {entry['id']} has parent_annotation_id "
                f"{declared_parent_id!r}; expected None"
            )
        if boundary.parent_annotation_label is not None:
            parent_entry = annotations_by_id.get(declared_parent_id)
            if parent_entry is None:
                raise ScaffoldError(
                    f"Annotation {entry['id']} has unknown parent_annotation_id "
                    f"{declared_parent_id!r}"
                )
            parent_source = parent_entry["source"]
            parent_boundary = annotation_boundaries_by_source.get(
                (parent_source["label"], parent_source.get("occurrence", 1))
            )
            contains_child = bool(
                parent_boundary
                and parent_boundary.start_marker.start < boundary.start_marker.start
                and boundary.end_marker.end < parent_boundary.end_marker.end
            )
            if parent_source["label"] != boundary.parent_annotation_label or not contains_child:
                raise ScaffoldError(
                    f"Annotation {entry['id']} parent_annotation_id {declared_parent_id!r} "
                    "does not identify its containing annotation"
                )


def _validate_entries(entries: object, required: set[str], kind: str) -> None:
    if not isinstance(entries, list):
        raise ScaffoldError(f"Block metadata requires a {kind}s array")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ScaffoldError(f"Block metadata {kind} {index} must be an object")
        missing = sorted(required - set(entry))
        if missing:
            raise ScaffoldError(
                f"Block metadata {kind} {index} is missing: {', '.join(missing)}"
            )


def _validate_unique(entries: list[dict], field: str) -> None:
    values = [entry.get(field) for entry in entries]
    if any(not isinstance(value, str) or not value for value in values):
        raise ScaffoldError(f"Block metadata {field} values must be non-empty strings")
    duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
    if duplicates:
        raise ScaffoldError(f"Duplicate block metadata {field}(s): {', '.join(duplicates)}")


def _validate_creative_guidance(entry: dict) -> None:
    guidance = entry.get("creative_guidance")
    if guidance is None:
        return
    required = {"visual_subject", "selection_tags", "use_when", "avoid_when"}
    if not isinstance(guidance, dict) or set(guidance) != required:
        raise ScaffoldError(
            f"Block metadata module {entry['id']} creative_guidance must contain: "
            + ", ".join(sorted(required))
        )
    for field in ("visual_subject", "use_when", "avoid_when"):
        if not isinstance(guidance[field], str) or not guidance[field].strip():
            raise ScaffoldError(
                f"Block metadata module {entry['id']} creative_guidance.{field} must be a non-empty string"
            )
    tags = guidance["selection_tags"]
    if (
        not isinstance(tags, list)
        or not tags
        or any(not isinstance(tag, str) or not tag.strip() for tag in tags)
        or len(tags) != len(set(tags))
    ):
        raise ScaffoldError(
            f"Block metadata module {entry['id']} creative_guidance.selection_tags must contain unique non-empty strings"
        )


def _occurrence_lookup(items: Iterable[tuple[str, int, int]]) -> dict[tuple[str, int], tuple[int, int]]:
    counts: Counter[str] = Counter()
    lookup = {}
    for label, start_row, end_row in items:
        counts[label] += 1
        lookup[(label, counts[label])] = (start_row, end_row)
    return lookup


def _validate_source_coverage(
    entries: list[dict],
    expected: dict[tuple[str, int], tuple[int, int]],
    kind: str,
) -> dict[tuple[str, int], str]:
    actual: dict[tuple[str, int], str] = {}
    for entry in entries:
        source = entry["source"]
        if not isinstance(source, dict) or not isinstance(source.get("label"), str):
            raise ScaffoldError(f"Block metadata {kind} {entry['id']} has invalid source")
        key = (source["label"], source.get("occurrence", 1))
        if key in actual:
            raise ScaffoldError(f"Duplicate block metadata {kind} source: {key!r}")
        actual[key] = entry["id"]
        rows = expected.get(key)
        if rows is None:
            raise ScaffoldError(f"Unknown block metadata {kind} source: {key!r}")
        if [*rows] != source.get("marker_rows"):
            raise ScaffoldError(
                f"Block metadata {kind} {entry['id']} marker rows do not match {rows}"
            )
    missing = sorted(set(expected) - set(actual))
    if missing:
        raise ScaffoldError(f"Block metadata is missing {kind} source(s): {missing!r}")
    return actual


def _with_occurrences(items: list, label_getter) -> list[tuple[object, int]]:
    counts: Counter[str] = Counter()
    result = []
    for item in items:
        label = label_getter(item)
        counts[label] += 1
        result.append((item, counts[label]))
    return result
