"""Utilities for validated Beefree scaffold extraction."""

from .parser import (
    END_MARKER_COLOR,
    ScaffoldError,
    START_MARKER_COLOR,
    STATIC_END_MARKER_COLOR,
    STATIC_START_MARKER_COLOR,
    apply_canonical_text_corrections,
    analyze_style_colors,
    find_module_boundaries,
    parse_rows,
    render_without_marker_rows,
)

__all__ = [
    "ScaffoldError",
    "START_MARKER_COLOR",
    "END_MARKER_COLOR",
    "STATIC_START_MARKER_COLOR",
    "STATIC_END_MARKER_COLOR",
    "apply_canonical_text_corrections",
    "analyze_style_colors",
    "find_module_boundaries",
    "parse_rows",
    "render_without_marker_rows",
]
