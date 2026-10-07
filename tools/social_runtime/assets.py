"""Social asset resolution over the validated manifest and the approval overlay."""

from __future__ import annotations

from pathlib import Path

from tools.asset_selection.selector import load_manifest
from tools.asset_selection.social_approvals import (
    apply_social_approvals,
    load_social_approvals,
    manifest_matches,
)


PRIVATE_FIELDS = ("dropbox_id", "dropbox_path", "stable_identity")
DIRECT_ROLE = {"post": "social-post", "carousel": "social-carousel"}
CROP_ROLE = "social-crop-source"


class SocialAssetError(ValueError):
    """Raised when an image cannot be resolved to a social-approved record."""


def load_social_assets(manifest_path: Path | str, overlay_path: Path | str, *, audience: str) -> list[dict]:
    """Return the social catalog for `audience`, with overlay roles attached."""
    overlay = load_social_approvals(overlay_path)
    if not manifest_matches(overlay, manifest_path):
        raise SocialAssetError(
            "Social approvals are not bound to the current manifest; "
            "the owner must re-confirm the overlay before it is trusted"
        )
    assets = apply_social_approvals(load_manifest(manifest_path), overlay)
    if audience == "outside-broker":
        return broker_safe_assets(assets, overlay["never_social_roles"])
    return assets


def broker_safe_assets(assets: list[dict], never_social_roles: list[str]) -> list[dict]:
    """Filter to social-approved records and strip Dropbox identifiers and paths.

    Restricted records are excluded by their `approved_for` classification, never by
    filename.
    """
    never = set(never_social_roles)
    safe = []
    for asset in assets:
        if not asset.get("social_roles") or set(asset.get("approved_for") or []) & never:
            continue
        safe.append({key: value for key, value in asset.items() if key not in PRIVATE_FIELDS})
    return safe


def resolve_social_asset(assets: list[dict], filename: str, *, role: str) -> dict:
    matches = [asset for asset in assets if asset["filename"] == filename]
    if not matches:
        raise SocialAssetError(f"Asset '{filename}' is not in the social catalog for this audience")
    if len(matches) > 1:
        raise SocialAssetError(f"Asset filename '{filename}' is ambiguous in the manifest")
    asset = matches[0]
    if asset.get("media_type") != "image":
        raise SocialAssetError(f"Asset '{filename}' is not an image record")
    if role not in asset.get("social_roles", []):
        approved = ", ".join(asset.get("social_roles") or []) or "no social role"
        raise SocialAssetError(
            f"Asset '{filename}' is not approved for '{role}' (approved for: {approved})"
        )
    return asset


def resolve_direct_asset(assets: list[dict], filename: str, *, fmt: dict) -> dict:
    """Resolve an asset used as-is. Orientation must already fit the format."""
    asset = resolve_social_asset(assets, filename, role=DIRECT_ROLE[fmt["kind"]])
    wanted = "square" if fmt["aspect_ratio"][0] == fmt["aspect_ratio"][1] else "portrait"
    if asset["orientation"] != wanted:
        raise SocialAssetError(
            f"Asset '{filename}' is {asset['orientation']} and cannot be used directly in a "
            f"{fmt['aspect_ratio'][0]}:{fmt['aspect_ratio'][1]} format; it needs an approved crop"
        )
    return asset
