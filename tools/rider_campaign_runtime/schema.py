from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse


class CampaignSpecError(ValueError):
    """Raised when a campaign spec is not safe to render."""


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_TOP = {
    "schema_version",
    "build",
    "campaign",
    "manifest",
    "modules",
    "static_blocks",
    "variants",
    "outside_broker",
    "deployment",
    "documents",
}
ALLOWED_BUILD = {
    "mode",
    "representative_variant",
    "variant_policy",
    "changed_surfaces",
}
ALLOWED_CAMPAIGN = {
    "slug",
    "title",
    "output_dir",
    "subject",
    "preview_text",
}
ALLOWED_MANIFEST = {"path"}
ALLOWED_MODULE = {"id", "variant", "slots"}
ALLOWED_STATIC_BLOCK = {"id", "decision"}
ALLOWED_SLOT = {
    "kind",
    "value",
    "href",
    "asset_id",
    "src",
    "alt",
    "title",
    "role",
}
ALLOWED_VARIANTS = {"branded", "outside_broker", "agents"}
ALLOWED_OUTSIDE = {"headshot", "name", "title", "phone", "email", "social"}
ALLOWED_OUTSIDE_HEADSHOT = {"src", "asset_id", "alt", "title"}
ALLOWED_DEPLOYMENT = {"asset_mode", "hosted_asset_base_url"}
ALLOWED_DOCUMENT = {"asset_id", "role"}
SLOT_KINDS = {"text", "safe_rich_text", "url", "image"}
URL_SCHEMES = {"http", "https", "mailto", "tel"}
IMAGE_SCHEMES = {"http", "https", "file"}
BUILD_MODES = {"composition-preview", "smoke-test", "release-build"}
VARIANT_POLICIES = {"single", "all", "changed-surface-expanded"}
CHANGED_SURFACES = {
    "agent-roster",
    "agent-data",
    "agent-footer-assets",
    "footer-renderer",
    "footer-data",
    "scaffold-footer-structure",
}
REPRESENTATIVE_VARIANT_RE = re.compile(r"^(branded|outside-broker-customizable|agent-[a-z0-9]+(?:-[a-z0-9]+)*)$")


def load_campaign_spec(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise CampaignSpecError(f"Invalid campaign JSON: {err}") from err
    validate_campaign_spec(data)
    return data


def validate_campaign_spec(data: object) -> None:
    if not isinstance(data, dict):
        raise CampaignSpecError("Campaign spec must be a JSON object")
    _reject_unknown(data, ALLOWED_TOP, "campaign spec")

    _require(data, "schema_version", str, "campaign spec")
    if data["schema_version"] != "1.0":
        raise CampaignSpecError("schema_version must be '1.0'")

    build = _require(data, "build", dict, "campaign spec")
    _validate_build(build)

    campaign = _require(data, "campaign", dict, "campaign spec")
    _reject_unknown(campaign, ALLOWED_CAMPAIGN, "campaign")
    slug = _require(campaign, "slug", str, "campaign")
    if not SLUG_RE.match(slug):
        raise CampaignSpecError("campaign.slug must be lowercase kebab-case")
    _require(campaign, "title", str, "campaign")
    _require(campaign, "output_dir", str, "campaign")
    for field in ("subject", "preview_text"):
        if field in campaign and not isinstance(campaign[field], str):
            raise CampaignSpecError(f"campaign.{field} must be a string")

    manifest = _require(data, "manifest", dict, "campaign spec")
    _reject_unknown(manifest, ALLOWED_MANIFEST, "manifest")
    _require(manifest, "path", str, "manifest")

    modules = _require(data, "modules", list, "campaign spec")
    if not modules:
        raise CampaignSpecError("modules must contain at least one content module")
    for index, module in enumerate(modules):
        if not isinstance(module, dict):
            raise CampaignSpecError(f"modules[{index}] must be an object")
        _reject_unknown(module, ALLOWED_MODULE, f"modules[{index}]")
        _require(module, "id", str, f"modules[{index}]")
        if "variant" in module and module["variant"] != "default":
            raise CampaignSpecError(f"modules[{index}].variant must be 'default'")
        slots = module.get("slots", {})
        if not isinstance(slots, dict):
            raise CampaignSpecError(f"modules[{index}].slots must be an object")
        for slot_name, slot in slots.items():
            if not isinstance(slot_name, str) or not slot_name:
                raise CampaignSpecError(f"modules[{index}].slots has an invalid key")
            _validate_slot(slot, f"modules[{index}].slots.{slot_name}")

    static_blocks = _require(data, "static_blocks", list, "campaign spec")
    for index, static_block in enumerate(static_blocks):
        if not isinstance(static_block, dict):
            raise CampaignSpecError(f"static_blocks[{index}] must be an object")
        _reject_unknown(static_block, ALLOWED_STATIC_BLOCK, f"static_blocks[{index}]")
        _require(static_block, "id", str, f"static_blocks[{index}]")
        decision = _require(static_block, "decision", str, f"static_blocks[{index}]")
        if decision not in {"include", "exclude"}:
            raise CampaignSpecError(f"static_blocks[{index}].decision must be include or exclude")

    variants = _require(data, "variants", dict, "campaign spec")
    _reject_unknown(variants, ALLOWED_VARIANTS, "variants")
    if "branded" in variants and not isinstance(variants["branded"], bool):
        raise CampaignSpecError("variants.branded must be a boolean")
    if "outside_broker" in variants and not isinstance(variants["outside_broker"], bool):
        raise CampaignSpecError("variants.outside_broker must be a boolean")
    agents = variants.get("agents", "all")
    if agents != "all":
        if not isinstance(agents, list) or not all(isinstance(item, str) for item in agents):
            raise CampaignSpecError("variants.agents must be 'all' or an array of agent ids")

    outside = data.get("outside_broker", {})
    if not isinstance(outside, dict):
        raise CampaignSpecError("outside_broker must be an object")
    _reject_unknown(outside, ALLOWED_OUTSIDE, "outside_broker")
    for field in ("name", "title", "phone", "email", "social"):
        if field in outside and not isinstance(outside[field], str):
            raise CampaignSpecError(f"outside_broker.{field} must be a string")
    if "headshot" in outside:
        headshot = outside["headshot"]
        if not isinstance(headshot, dict):
            raise CampaignSpecError("outside_broker.headshot must be an object")
        _reject_unknown(headshot, ALLOWED_OUTSIDE_HEADSHOT, "outside_broker.headshot")
        if ("src" in headshot) == ("asset_id" in headshot):
            raise CampaignSpecError("outside_broker.headshot must contain exactly one of src or asset_id")
        for field in ("src", "asset_id", "alt", "title"):
            if field in headshot and not isinstance(headshot[field], str):
                raise CampaignSpecError(f"outside_broker.headshot.{field} must be a string")
        if "src" in headshot:
            validate_image_url(headshot["src"], "outside_broker.headshot.src")

    documents = data.get("documents", [])
    if not isinstance(documents, list):
        raise CampaignSpecError("documents must be an array")
    for index, document in enumerate(documents):
        if not isinstance(document, dict):
            raise CampaignSpecError(f"documents[{index}] must be an object")
        _reject_unknown(document, ALLOWED_DOCUMENT, f"documents[{index}]")
        _require(document, "asset_id", str, f"documents[{index}]")
        _require(document, "role", str, f"documents[{index}]")

    deployment = data.get("deployment", {})
    if not isinstance(deployment, dict):
        raise CampaignSpecError("deployment must be an object")
    _reject_unknown(deployment, ALLOWED_DEPLOYMENT, "deployment")
    asset_mode = deployment.get("asset_mode", "relative-review")
    if asset_mode not in {"relative-review", "hosted-deployment"}:
        raise CampaignSpecError("deployment.asset_mode must be relative-review or hosted-deployment")
    hosted_base = deployment.get("hosted_asset_base_url")
    if asset_mode == "hosted-deployment":
        if not isinstance(hosted_base, str) or not hosted_base:
            raise CampaignSpecError("hosted-deployment requires hosted_asset_base_url")
        validate_http_url(hosted_base, "deployment.hosted_asset_base_url")
    elif hosted_base is not None:
        raise CampaignSpecError("hosted_asset_base_url is only valid with hosted-deployment")


def validate_http_url(value: str, label: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise CampaignSpecError(f"{label} must be an http(s) URL")


def validate_href(value: str, label: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in URL_SCHEMES:
        raise CampaignSpecError(f"{label} has unsupported URL scheme: {parsed.scheme or '<relative>'}")
    if parsed.scheme in {"http", "https"} and not parsed.netloc:
        raise CampaignSpecError(f"{label} must include a host")


def validate_image_url(value: str, label: str) -> None:
    parsed = urlparse(value)
    if not parsed.scheme:
        path = parsed.path
        if not path or path.startswith("/") or ".." in path.split("/"):
            raise CampaignSpecError(f"{label} must be an http(s), file, or safe relative image URL")
        return
    if parsed.scheme not in IMAGE_SCHEMES:
        raise CampaignSpecError(f"{label} must be an http(s), file, or safe relative image URL")
    if parsed.scheme in {"http", "https"} and not parsed.netloc:
        raise CampaignSpecError(f"{label} must include a host")
    if parsed.scheme == "file" and not parsed.path:
        raise CampaignSpecError(f"{label} file URL must include a path")


def _validate_build(build: dict) -> None:
    _reject_unknown(build, ALLOWED_BUILD, "build")
    mode = _require(build, "mode", str, "build")
    if mode not in BUILD_MODES:
        raise CampaignSpecError("build.mode must be composition-preview, smoke-test, or release-build")
    variant_policy = _require(build, "variant_policy", str, "build")
    if variant_policy not in VARIANT_POLICIES:
        raise CampaignSpecError("build.variant_policy must be single, all, or changed-surface-expanded")

    representative_variant = build.get("representative_variant", "branded")
    if not isinstance(representative_variant, str) or not REPRESENTATIVE_VARIANT_RE.match(representative_variant):
        raise CampaignSpecError(
            "build.representative_variant must be branded, outside-broker-customizable, or agent-<agent-id>"
        )

    changed_surfaces = build.get("changed_surfaces", [])
    if not isinstance(changed_surfaces, list) or not all(isinstance(item, str) for item in changed_surfaces):
        raise CampaignSpecError("build.changed_surfaces must be an array of strings")
    unknown_surfaces = sorted(set(changed_surfaces) - CHANGED_SURFACES)
    if unknown_surfaces:
        raise CampaignSpecError("build.changed_surfaces has unknown value(s): " + ", ".join(unknown_surfaces))
    if len(set(changed_surfaces)) != len(changed_surfaces):
        raise CampaignSpecError("build.changed_surfaces must not contain duplicates")

    if mode == "composition-preview" and variant_policy != "single":
        raise CampaignSpecError("composition-preview requires build.variant_policy single")
    if mode == "release-build" and variant_policy != "all":
        raise CampaignSpecError("release-build requires build.variant_policy all")
    if mode != "smoke-test" and changed_surfaces:
        raise CampaignSpecError("build.changed_surfaces is only valid for smoke-test builds")
    if variant_policy == "changed-surface-expanded" and mode != "smoke-test":
        raise CampaignSpecError("changed-surface-expanded is only valid for smoke-test builds")
    if variant_policy == "changed-surface-expanded" and not changed_surfaces:
        raise CampaignSpecError("changed-surface-expanded requires at least one build.changed_surfaces value")
    if variant_policy != "changed-surface-expanded" and changed_surfaces:
        raise CampaignSpecError("build.changed_surfaces requires build.variant_policy changed-surface-expanded")


def _validate_slot(slot: object, label: str) -> None:
    if not isinstance(slot, dict):
        raise CampaignSpecError(f"{label} must be an object")
    _reject_unknown(slot, ALLOWED_SLOT, label)
    kind = _require(slot, "kind", str, label)
    if kind not in SLOT_KINDS:
        raise CampaignSpecError(f"{label}.kind must be one of: {', '.join(sorted(SLOT_KINDS))}")
    if kind in {"text", "safe_rich_text"}:
        _reject_unknown(slot, {"kind", "value"}, label)
        _require(slot, "value", str, label)
    elif kind == "url":
        _reject_unknown(slot, {"kind", "href"}, label)
        href = _require(slot, "href", str, label)
        validate_href(href, f"{label}.href")
    elif kind == "image":
        _reject_unknown(slot, {"kind", "asset_id", "src", "alt", "title", "role"}, label)
        has_asset = "asset_id" in slot
        has_src = "src" in slot
        if has_asset == has_src:
            raise CampaignSpecError(f"{label} image slot must contain exactly one of asset_id or src")
        if has_asset:
            _require(slot, "asset_id", str, label)
        if has_src:
            src = _require(slot, "src", str, label)
            validate_image_url(src, f"{label}.src")
        for field in ("alt", "title", "role"):
            if field in slot and not isinstance(slot[field], str):
                raise CampaignSpecError(f"{label}.{field} must be a string")


def _require(obj: dict, field: str, expected_type: type, label: str):
    if field not in obj:
        raise CampaignSpecError(f"{label} is missing required field '{field}'")
    value = obj[field]
    if not isinstance(value, expected_type):
        raise CampaignSpecError(f"{label}.{field} must be {expected_type.__name__}")
    if expected_type is str and not value:
        raise CampaignSpecError(f"{label}.{field} must not be empty")
    return value


def _reject_unknown(obj: dict, allowed: set[str], label: str) -> None:
    unknown = sorted(set(obj) - allowed)
    if unknown:
        raise CampaignSpecError(f"{label} has unknown field(s): {', '.join(unknown)}")
