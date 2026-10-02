"""Utilities for validated Beefree scaffold extraction."""

from .parser import (
    ScaffoldError,
    apply_canonical_text_corrections,
    analyze_style_colors,
    find_module_boundaries,
    parse_rows,
    render_without_marker_rows,
)

__all__ = [
    "ScaffoldError",
    "apply_canonical_text_corrections",
    "analyze_style_colors",
    "find_module_boundaries",
    "parse_rows",
    "render_without_marker_rows",
]
