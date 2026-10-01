"""Manifest validation and deterministic asset selection for OnBrand Design."""

from .selector import (
    ManifestError,
    SelectionNeeds,
    load_manifest,
    select_candidates,
    validate_manifest,
)

__all__ = [
    "ManifestError",
    "SelectionNeeds",
    "load_manifest",
    "select_candidates",
    "validate_manifest",
]
