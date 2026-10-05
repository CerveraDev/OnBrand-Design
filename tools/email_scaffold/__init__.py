"""Utilities for validated Beefree scaffold extraction."""

from .parser import (
    AnnotationBoundary,
    END_MARKER_COLOR,
    MarkerElement,
    ModuleBoundary,
    ScaffoldError,
    START_MARKER_COLOR,
    STATIC_END_MARKER_COLOR,
    STATIC_START_MARKER_COLOR,
    apply_canonical_text_corrections,
    analyze_style_colors,
    find_annotation_boundaries,
    find_module_boundaries,
    parse_marker_elements,
    parse_rows,
    render_without_authoring_markers,
    render_without_marker_rows,
)
from .metadata import load_block_metadata, validate_block_metadata

__all__ = [
    "AnnotationBoundary",
    "ScaffoldError",
    "START_MARKER_COLOR",
    "END_MARKER_COLOR",
    "MarkerElement",
    "ModuleBoundary",
    "STATIC_START_MARKER_COLOR",
    "STATIC_END_MARKER_COLOR",
    "apply_canonical_text_corrections",
    "analyze_style_colors",
    "find_annotation_boundaries",
    "find_module_boundaries",
    "parse_marker_elements",
    "parse_rows",
    "render_without_authoring_markers",
    "render_without_marker_rows",
    "load_block_metadata",
    "validate_block_metadata",
]
