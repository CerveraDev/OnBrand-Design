from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from .copy_allocation import CHANNELS, CLAIM_POLICIES, REUSE_POLICIES


class CampaignSpecError(ValueError):
    """Raised when a campaign spec is not safe to render."""


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_TOP = {
    "schema_version",
    "build",
    "composition",
    "image_workflow",
    "copy_allocation",
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
ALLOWED_COMPOSITION = {
    "plan_version",
    "plan_id",
    "status",
    "approved_by",
    "approved_at",
    "representative_variant",
    "selected_module_codes",
    "selected_modules",
    "static_block_decisions",
    "editable_slots",
    "required_assets",
    "compatibility",
    "approval_required_before",
    "selected_hero_configuration",
}
ALLOWED_COMPOSITION_MODULE = {"code", "scaffold_module_id", "module_type", "includes_header", "locked"}
ALLOWED_COMPOSITION_STATIC = {"code", "scaffold_module_id", "decision"}
ALLOWED_COMPOSITION_SLOT = {"code", "scaffold_module_id", "slot", "slot_type", "operations", "required_approvals"}
ALLOWED_COMPOSITION_ASSET = {"code", "scaffold_module_id", "slot", "required_approvals", "image_aspect_ratio"}
ALLOWED_IMAGE_WORKFLOW = {"version", "items"}
ALLOWED_IMAGE_WORKFLOW_ITEM = {
    "image_id",
    "workflow_type",
    "status",
    "approved_by",
    "approved_at",
    "intended_use",
    "environment",
    "source_assets",
    "prompt_record",
    "output",
    "placement",
    "approval_notes",
}
ALLOWED_IMAGE_INTENDED_USE = {"module_id", "slot", "role", "variant_scope"}
ALLOWED_IMAGE_ENVIRONMENT = {"type", "description", "keywords", "conceptual_environment_approved"}
ALLOWED_IMAGE_SOURCE = {"asset_id", "path", "sha256", "role", "required_approval", "preserve"}
ALLOWED_IMAGE_PROMPT = {"tool", "model", "prompt", "negative_prompt", "edit_steps", "text_policy"}
ALLOWED_IMAGE_OUTPUT = {"src", "sha256", "width", "height", "format"}
ALLOWED_IMAGE_PLACEMENT = {"aspect_ratio", "crop", "focal_point", "safe_area", "logo_overlay"}
ALLOWED_IMAGE_FOCAL = {"x", "y"}
ALLOWED_COPY_ALLOCATION = {
    "version",
    "plan_id",
    "status",
    "approved_by",
    "approved_at",
    "content_units",
    "slot_allocation",
    "restricted_phrases",
    "dedupe_exemptions",
}
ALLOWED_COPY_UNIT = {
    "id",
    "text",
    "content_role",
    "source",
    "approval_status",
    "owner",
    "reuse_policy",
    "max_occurrences",
    "claim_policy",
    "claim_references",
    "declared_text_source",
    "notes",
}
ALLOWED_COPY_OWNER = {
    "channel",
    "module_id",
    "slot",
    "metadata_field",
    "image_workflow_id",
    "static_block_id",
    "variant_scope",
}
ALLOWED_SLOT_ALLOCATION = {"module_id", "slot", "content_unit_id", "rendering_type"}
ALLOWED_RESTRICTED_PHRASE = {"id", "phrase", "max_occurrences", "reason"}
ALLOWED_DEDUPE_EXEMPTION = {"id", "reason", "scope", "applies_to", "approved_by", "approved_at", "evidence"}
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
    "image_workflow_id",
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
    if "composition" in data:
        _validate_composition(_require(data, "composition", dict, "campaign spec"))
    if "image_workflow" in data:
        _validate_image_workflow(_require(data, "image_workflow", dict, "campaign spec"))
    _validate_copy_allocation(_require(data, "copy_allocation", dict, "campaign spec"))

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


def _validate_composition(composition: dict) -> None:
    _reject_unknown(composition, ALLOWED_COMPOSITION, "composition")
    if _require(composition, "plan_version", str, "composition") != "1.0":
        raise CampaignSpecError("composition.plan_version must be '1.0'")
    _require(composition, "plan_id", str, "composition")
    if _require(composition, "status", str, "composition") != "approved":
        raise CampaignSpecError("composition.status must be approved")
    _require(composition, "approved_by", str, "composition")
    _require(composition, "approved_at", str, "composition")
    representative = _require(composition, "representative_variant", str, "composition")
    if not REPRESENTATIVE_VARIANT_RE.match(representative):
        raise CampaignSpecError(
            "composition.representative_variant must be branded, outside-broker-customizable, or agent-<agent-id>"
        )
    _require_string_array(composition, "selected_module_codes", "composition")
    for index, item in enumerate(_optional_array(composition, "selected_modules", "composition")):
        _validate_object(item, ALLOWED_COMPOSITION_MODULE, f"composition.selected_modules[{index}]")
        for field in ("code", "scaffold_module_id", "module_type"):
            _require(item, field, str, f"composition.selected_modules[{index}]")
        for field in ("includes_header", "locked"):
            if field in item and not isinstance(item[field], bool):
                raise CampaignSpecError(f"composition.selected_modules[{index}].{field} must be a boolean")
    for index, item in enumerate(_require_array(composition, "static_block_decisions", "composition")):
        _validate_object(item, ALLOWED_COMPOSITION_STATIC, f"composition.static_block_decisions[{index}]")
        _require(item, "code", str, f"composition.static_block_decisions[{index}]")
        _require(item, "scaffold_module_id", str, f"composition.static_block_decisions[{index}]")
        decision = _require(item, "decision", str, f"composition.static_block_decisions[{index}]")
        if decision not in {"include", "exclude"}:
            raise CampaignSpecError(f"composition.static_block_decisions[{index}].decision must be include or exclude")
    for field, allowed in (
        ("editable_slots", ALLOWED_COMPOSITION_SLOT),
        ("required_assets", ALLOWED_COMPOSITION_ASSET),
    ):
        for index, item in enumerate(_optional_array(composition, field, "composition")):
            _validate_object(item, allowed, f"composition.{field}[{index}]")
            for string_field in sorted(allowed - {"operations", "required_approvals"}):
                _require(item, string_field, str, f"composition.{field}[{index}]")
            for array_field in sorted(allowed & {"operations", "required_approvals"}):
                allow_empty = array_field == "required_approvals"
                _require_string_array(item, array_field, f"composition.{field}[{index}]", allow_empty=allow_empty)
    if "approval_required_before" in composition:
        _require_string_array(composition, "approval_required_before", "composition")
    if "selected_hero_configuration" in composition:
        _require(composition, "selected_hero_configuration", str, "composition")
    if "compatibility" in composition and not isinstance(composition["compatibility"], dict):
        raise CampaignSpecError("composition.compatibility must be an object")


def _validate_image_workflow(workflow: dict) -> None:
    _reject_unknown(workflow, ALLOWED_IMAGE_WORKFLOW, "image_workflow")
    if _require(workflow, "version", str, "image_workflow") != "1.0":
        raise CampaignSpecError("image_workflow.version must be '1.0'")
    items = _require_array(workflow, "items", "image_workflow")
    if not items:
        raise CampaignSpecError("image_workflow.items must be a non-empty array")
    seen_ids: set[str] = set()
    for index, item in enumerate(items):
        label = f"image_workflow.items[{index}]"
        _validate_object(item, ALLOWED_IMAGE_WORKFLOW_ITEM, label)
        image_id = _require(item, "image_id", str, label)
        if image_id in seen_ids:
            raise CampaignSpecError(f"Duplicate image_workflow image_id: {image_id}")
        seen_ids.add(image_id)
        workflow_type = _require(item, "workflow_type", str, label)
        if workflow_type not in {"grounded-edit", "grounded-generation", "conceptual-generation"}:
            raise CampaignSpecError(f"{label}.workflow_type is not supported")
        status = _require(item, "status", str, label)
        if status not in {"approved", "candidate", "rejected"}:
            raise CampaignSpecError(f"{label}.status must be approved, candidate, or rejected")
        for field in ("approved_by", "approved_at"):
            if field in item and not isinstance(item[field], str):
                raise CampaignSpecError(f"{label}.{field} must be a string")

        intended = _require(item, "intended_use", dict, label)
        _reject_unknown(intended, ALLOWED_IMAGE_INTENDED_USE, f"{label}.intended_use")
        for field in ("module_id", "slot", "role"):
            _require(intended, field, str, f"{label}.intended_use")
        if "variant_scope" in intended and intended["variant_scope"] not in {"all", "representative"}:
            raise CampaignSpecError(f"{label}.intended_use.variant_scope must be all or representative")

        environment = _require(item, "environment", dict, label)
        _reject_unknown(environment, ALLOWED_IMAGE_ENVIRONMENT, f"{label}.environment")
        if _require(environment, "type", str, f"{label}.environment") not in {"real-rider", "conceptual"}:
            raise CampaignSpecError(f"{label}.environment.type must be real-rider or conceptual")
        _require(environment, "description", str, f"{label}.environment")
        _require_string_array(environment, "keywords", f"{label}.environment")
        if "conceptual_environment_approved" in environment and not isinstance(
            environment["conceptual_environment_approved"], bool
        ):
            raise CampaignSpecError(f"{label}.environment.conceptual_environment_approved must be a boolean")

        for source_index, source in enumerate(_require_array(item, "source_assets", label)):
            source_label = f"{label}.source_assets[{source_index}]"
            _validate_object(source, ALLOWED_IMAGE_SOURCE, source_label)
            has_asset_id = "asset_id" in source
            has_path = "path" in source
            if has_asset_id == has_path:
                raise CampaignSpecError(f"{source_label} must contain exactly one of asset_id or path")
            if has_asset_id:
                _require(source, "asset_id", str, source_label)
            if has_path:
                _require(source, "path", str, source_label)
                _require(source, "sha256", str, source_label)
            if _require(source, "role", str, source_label) not in {
                "environment-base",
                "logo-reference",
                "likeness-reference",
                "style-reference",
            }:
                raise CampaignSpecError(f"{source_label}.role is not supported")
            if "required_approval" in source and not isinstance(source["required_approval"], str):
                raise CampaignSpecError(f"{source_label}.required_approval must be a string")
            if "preserve" in source:
                _require_string_array(source, "preserve", source_label, allow_empty=True)

        prompt = _require(item, "prompt_record", dict, label)
        _reject_unknown(prompt, ALLOWED_IMAGE_PROMPT, f"{label}.prompt_record")
        _require(prompt, "tool", str, f"{label}.prompt_record")
        _require(prompt, "prompt", str, f"{label}.prompt_record")
        _require_string_array(prompt, "edit_steps", f"{label}.prompt_record")
        if _require(prompt, "text_policy", str, f"{label}.prompt_record") not in {
            "live-html",
            "baked-approved",
            "none",
        }:
            raise CampaignSpecError(f"{label}.prompt_record.text_policy is not supported")
        for field in ("model", "negative_prompt"):
            if field in prompt and not isinstance(prompt[field], str):
                raise CampaignSpecError(f"{label}.prompt_record.{field} must be a string")

        output = _require(item, "output", dict, label)
        _reject_unknown(output, ALLOWED_IMAGE_OUTPUT, f"{label}.output")
        _require(output, "src", str, f"{label}.output")
        _require(output, "sha256", str, f"{label}.output")
        for field in ("width", "height"):
            if not isinstance(output.get(field), int) or output[field] <= 0:
                raise CampaignSpecError(f"{label}.output.{field} must be a positive integer")
        if _require(output, "format", str, f"{label}.output") not in {"png", "jpg", "jpeg", "gif"}:
            raise CampaignSpecError(f"{label}.output.format must be png, jpg, jpeg, or gif")

        placement = _require(item, "placement", dict, label)
        _reject_unknown(placement, ALLOWED_IMAGE_PLACEMENT, f"{label}.placement")
        _require(placement, "aspect_ratio", str, f"{label}.placement")
        _require(placement, "crop", str, f"{label}.placement")
        focal = _require(placement, "focal_point", dict, f"{label}.placement")
        _reject_unknown(focal, ALLOWED_IMAGE_FOCAL, f"{label}.placement.focal_point")
        for axis in ("x", "y"):
            value = focal.get(axis)
            if not isinstance(value, (int, float)) or not (0 <= value <= 1):
                raise CampaignSpecError(f"{label}.placement.focal_point.{axis} must be between 0 and 1")
        for field in ("safe_area", "logo_overlay"):
            if field in placement and not isinstance(placement[field], str):
                raise CampaignSpecError(f"{label}.placement.{field} must be a string")
        if "approval_notes" in item and not isinstance(item["approval_notes"], str):
            raise CampaignSpecError(f"{label}.approval_notes must be a string")


def _validate_copy_allocation(allocation: dict) -> None:
    _reject_unknown(allocation, ALLOWED_COPY_ALLOCATION, "copy_allocation")
    if _require(allocation, "version", str, "copy_allocation") != "1.0":
        raise CampaignSpecError("copy_allocation.version must be '1.0'")
    _require(allocation, "plan_id", str, "copy_allocation")
    if _require(allocation, "status", str, "copy_allocation") != "approved":
        raise CampaignSpecError("copy_allocation.status must be approved")
    _require(allocation, "approved_by", str, "copy_allocation")
    _require(allocation, "approved_at", str, "copy_allocation")
    units = _require_array(allocation, "content_units", "copy_allocation")
    if not units:
        raise CampaignSpecError("copy_allocation.content_units must not be empty")
    for index, unit in enumerate(units):
        label = f"copy_allocation.content_units[{index}]"
        _validate_object(unit, ALLOWED_COPY_UNIT, label)
        for field in ("id", "text", "content_role", "source", "approval_status"):
            _require(unit, field, str, label)
        if unit["approval_status"] != "approved":
            raise CampaignSpecError(f"{label}.approval_status must be approved")
        owner = _require(unit, "owner", dict, label)
        _reject_unknown(owner, ALLOWED_COPY_OWNER, f"{label}.owner")
        _require(owner, "channel", str, f"{label}.owner")
        if owner["channel"] not in CHANNELS:
            raise CampaignSpecError(f"{label}.owner.channel is not supported")
        for field in ("module_id", "slot", "metadata_field", "image_workflow_id", "static_block_id"):
            if field in owner:
                _require(owner, field, str, f"{label}.owner")
        if "variant_scope" in owner and owner["variant_scope"] not in {"all", "representative"}:
            raise CampaignSpecError(f"{label}.owner.variant_scope must be all or representative")
        if "reuse_policy" in unit and _require(unit, "reuse_policy", str, label) not in REUSE_POLICIES:
            raise CampaignSpecError(f"{label}.reuse_policy is not supported")
        if "max_occurrences" in unit:
            value = unit["max_occurrences"]
            if type(value) is not int or value <= 0:
                raise CampaignSpecError(f"{label}.max_occurrences must be a positive integer")
        if "claim_policy" in unit and _require(unit, "claim_policy", str, label) not in CLAIM_POLICIES:
            raise CampaignSpecError(f"{label}.claim_policy is not supported")
        if "claim_references" in unit:
            _require_string_array(unit, "claim_references", label, allow_empty=True)
        for field in ("declared_text_source", "notes"):
            if field in unit and not isinstance(unit[field], str):
                raise CampaignSpecError(f"{label}.{field} must be a string")
        if "declared_text_source" in unit and unit["declared_text_source"] not in {"ocr", "creator-declared"}:
            raise CampaignSpecError(f"{label}.declared_text_source is not supported")
    for index, item in enumerate(_optional_array(allocation, "slot_allocation", "copy_allocation")):
        label = f"copy_allocation.slot_allocation[{index}]"
        _validate_object(item, ALLOWED_SLOT_ALLOCATION, label)
        for field in ("module_id", "slot", "content_unit_id", "rendering_type"):
            _require(item, field, str, label)
    for index, item in enumerate(_optional_array(allocation, "restricted_phrases", "copy_allocation")):
        label = f"copy_allocation.restricted_phrases[{index}]"
        _validate_object(item, ALLOWED_RESTRICTED_PHRASE, label)
        for field in ("id", "phrase", "reason"):
            _require(item, field, str, label)
        if "max_occurrences" in item:
            value = item["max_occurrences"]
            if type(value) is not int or value <= 0:
                raise CampaignSpecError(f"{label}.max_occurrences must be a positive integer")
    for index, item in enumerate(_optional_array(allocation, "dedupe_exemptions", "copy_allocation")):
        label = f"copy_allocation.dedupe_exemptions[{index}]"
        _validate_object(item, ALLOWED_DEDUPE_EXEMPTION, label)
        for field in ("id", "reason", "scope", "approved_by", "approved_at"):
            _require(item, field, str, label)
        _require_string_array(item, "applies_to", label)
        if "evidence" in item and not isinstance(item["evidence"], str):
            raise CampaignSpecError(f"{label}.evidence must be a string")


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
        _reject_unknown(slot, {"kind", "asset_id", "src", "alt", "title", "role", "image_workflow_id"}, label)
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
        if "image_workflow_id" in slot:
            if not has_src:
                raise CampaignSpecError(f"{label}.image_workflow_id requires a src image")
            _require(slot, "image_workflow_id", str, label)


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


def _validate_object(value: object, allowed: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise CampaignSpecError(f"{label} must be an object")
    _reject_unknown(value, allowed, label)


def _require_array(obj: dict, field: str, label: str) -> list:
    value = obj.get(field)
    if not isinstance(value, list):
        raise CampaignSpecError(f"{label}.{field} must be an array")
    return value


def _optional_array(obj: dict, field: str, label: str) -> list:
    if field not in obj:
        return []
    return _require_array(obj, field, label)


def _require_string_array(obj: dict, field: str, label: str, *, allow_empty: bool = False) -> list[str]:
    value = _require_array(obj, field, label)
    if (not allow_empty and not value) or not all(isinstance(item, str) and item for item in value):
        qualifier = "an array" if allow_empty else "a non-empty array"
        raise CampaignSpecError(f"{label}.{field} must be {qualifier} of strings")
    return value
