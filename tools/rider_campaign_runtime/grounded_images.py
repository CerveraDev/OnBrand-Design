from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import struct
from urllib.parse import unquote, urlparse

from tools.asset_selection.selector import normalize_values

from .scaffold import Scaffold


WORKFLOW_VERSION = "1.0"
APPROVED_STATUS = "approved"
WORKFLOW_TYPES = {"grounded-edit", "grounded-generation", "conceptual-generation"}
ENVIRONMENT_TYPES = {"real-rider", "conceptual"}
SOURCE_ROLES = {"environment-base", "logo-reference", "likeness-reference", "style-reference"}
TEXT_POLICIES = {"live-html", "baked-approved", "none"}


class GroundedImageError(ValueError):
    """Raised when generated/edited image provenance is unsafe for runtime use."""


@dataclass(frozen=True)
class GroundedImageSummary:
    image_id: str
    workflow_type: str
    status: str
    intended_module_id: str
    intended_slot: str
    output_source: str
    output_sha256: str
    output_width: int
    output_height: int
    source_asset_ids: tuple[str, ...]


def validate_grounded_image_workflow(
    spec: dict,
    *,
    base_dir: Path,
    manifest_assets: dict[str, dict],
    scaffold: Scaffold,
) -> dict | None:
    workflow = spec.get("image_workflow")
    if workflow is None:
        return None
    if not isinstance(workflow, dict):
        raise GroundedImageError("image_workflow must be an object")
    _reject_unknown(workflow, {"version", "items"}, "image_workflow")
    if _require_str(workflow, "version", "image_workflow") != WORKFLOW_VERSION:
        raise GroundedImageError(f"image_workflow.version must be {WORKFLOW_VERSION}")
    items = workflow.get("items")
    if not isinstance(items, list) or not items:
        raise GroundedImageError("image_workflow.items must be a non-empty array")

    slot_refs = _image_workflow_slot_refs(spec)
    summaries: list[GroundedImageSummary] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise GroundedImageError(f"image_workflow.items[{index}] must be an object")
        summary = _validate_item(
            item,
            index=index,
            spec=spec,
            base_dir=base_dir,
            manifest_assets=manifest_assets,
            scaffold=scaffold,
            slot_refs=slot_refs,
        )
        if summary.image_id in seen:
            raise GroundedImageError(f"Duplicate image_workflow id: {summary.image_id}")
        seen.add(summary.image_id)
        summaries.append(summary)

    unknown_slot_refs = sorted(set(slot_refs) - seen)
    if unknown_slot_refs:
        raise GroundedImageError("Image slot references unknown image_workflow id(s): " + ", ".join(unknown_slot_refs))

    return {
        "version": WORKFLOW_VERSION,
        "items": [
            {
                "image_id": item.image_id,
                "workflow_type": item.workflow_type,
                "status": item.status,
                "intended_module_id": item.intended_module_id,
                "intended_slot": item.intended_slot,
                "output_source": item.output_source,
                "output_sha256": item.output_sha256,
                "output_width": item.output_width,
                "output_height": item.output_height,
                "source_asset_ids": list(item.source_asset_ids),
            }
            for item in summaries
        ],
    }


def _validate_item(
    item: dict,
    *,
    index: int,
    spec: dict,
    base_dir: Path,
    manifest_assets: dict[str, dict],
    scaffold: Scaffold,
    slot_refs: dict[str, dict],
) -> GroundedImageSummary:
    label = f"image_workflow.items[{index}]"
    _reject_unknown(
        item,
        {
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
        },
        label,
    )
    image_id = _require_str(item, "image_id", label)
    workflow_type = _require_str(item, "workflow_type", label)
    if workflow_type not in WORKFLOW_TYPES:
        raise GroundedImageError(f"{label}.workflow_type is not supported: {workflow_type}")
    status = _require_str(item, "status", label)
    if status != APPROVED_STATUS:
        raise GroundedImageError(f"{label}.status must be approved before runtime assembly")
    _require_str(item, "approved_by", label)
    _require_str(item, "approved_at", label)

    intended_use = _require_object(item, "intended_use", label)
    _reject_unknown(intended_use, {"module_id", "slot", "role", "variant_scope"}, f"{label}.intended_use")
    module_id = _require_str(intended_use, "module_id", f"{label}.intended_use")
    slot_name = _require_str(intended_use, "slot", f"{label}.intended_use")
    role = _require_str(intended_use, "role", f"{label}.intended_use")
    if intended_use.get("variant_scope", "all") not in {"all", "representative"}:
        raise GroundedImageError(f"{label}.intended_use.variant_scope must be all or representative")
    if module_id not in scaffold.slot_map:
        raise GroundedImageError(f"{label}.intended_use.module_id is not in scaffold slot map: {module_id}")
    if slot_name not in scaffold.slot_map[module_id]:
        raise GroundedImageError(f"{label}.intended_use.slot is not defined for {module_id}: {slot_name}")
    if not any(
        rule["operation"]
        in {"replace_image_src", "replace_background_url", "annotation_replace_image"}
        for rule in _slot_rules(scaffold.slot_map[module_id][slot_name])
    ):
        raise GroundedImageError(f"{label}.intended_use.slot is not an image slot: {slot_name}")

    slot_ref = slot_refs.get(image_id)
    if not slot_ref:
        raise GroundedImageError(f"{label}.image_id is not referenced by any image slot: {image_id}")
    if slot_ref["module_id"] != module_id or slot_ref["slot"] != slot_name:
        raise GroundedImageError(f"{label}.intended_use does not match the referencing image slot")

    environment = _validate_environment(_require_object(item, "environment", label), label)
    source_asset_ids = _validate_source_assets(
        _require_array(item, "source_assets", label),
        label=label,
        base_dir=base_dir,
        manifest_assets=manifest_assets,
        environment=environment,
        workflow_type=workflow_type,
    )
    _validate_prompt_record(_require_object(item, "prompt_record", label), label)
    output = _validate_output(_require_object(item, "output", label), label=label, base_dir=base_dir)
    _validate_placement(_require_object(item, "placement", label), label=label)

    if _resolved_source(slot_ref["src"], base_dir) != output["source"]:
        raise GroundedImageError(f"{label}.output.src must match the image slot src")
    if role != slot_ref["role"]:
        raise GroundedImageError(f"{label}.intended_use.role must match the image slot role")

    return GroundedImageSummary(
        image_id=image_id,
        workflow_type=workflow_type,
        status=status,
        intended_module_id=module_id,
        intended_slot=slot_name,
        output_source=output["source"],
        output_sha256=output["sha256"],
        output_width=output["width"],
        output_height=output["height"],
        source_asset_ids=tuple(source_asset_ids),
    )


def _image_workflow_slot_refs(spec: dict) -> dict[str, dict]:
    refs: dict[str, dict] = {}
    for module in spec.get("modules", []):
        module_id = module.get("id", "")
        for slot_name, slot in module.get("slots", {}).items():
            if not isinstance(slot, dict) or slot.get("kind") != "image" or "image_workflow_id" not in slot:
                continue
            image_id = slot["image_workflow_id"]
            if image_id in refs:
                raise GroundedImageError(f"Duplicate image_workflow_id in image slots: {image_id}")
            if "src" not in slot or "asset_id" in slot:
                raise GroundedImageError(f"{module_id}.{slot_name} image_workflow_id requires src and forbids asset_id")
            refs[image_id] = {
                "module_id": module_id,
                "slot": slot_name,
                "src": slot["src"],
                "role": slot.get("role", slot_name),
            }
    return refs


def _slot_rules(definition: object) -> list[dict]:
    if isinstance(definition, list):
        return definition
    if isinstance(definition, dict) and isinstance(definition.get("rules"), list):
        return definition["rules"]
    return []


def _validate_environment(environment: dict, label: str) -> dict:
    _reject_unknown(
        environment,
        {"type", "description", "keywords", "conceptual_environment_approved"},
        f"{label}.environment",
    )
    env_type = _require_str(environment, "type", f"{label}.environment")
    if env_type not in ENVIRONMENT_TYPES:
        raise GroundedImageError(f"{label}.environment.type must be real-rider or conceptual")
    _require_str(environment, "description", f"{label}.environment")
    keywords = _require_string_array(environment, "keywords", f"{label}.environment")
    conceptual_approved = environment.get("conceptual_environment_approved", False)
    if not isinstance(conceptual_approved, bool):
        raise GroundedImageError(f"{label}.environment.conceptual_environment_approved must be a boolean")
    if env_type == "real-rider" and conceptual_approved:
        raise GroundedImageError(f"{label}.environment real-rider must not mark conceptual_environment_approved")
    if env_type == "conceptual" and not conceptual_approved:
        raise GroundedImageError(f"{label}.environment conceptual requires explicit approval")
    return {"type": env_type, "keywords": keywords, "conceptual_environment_approved": conceptual_approved}


def _validate_source_assets(
    sources: list,
    *,
    label: str,
    base_dir: Path,
    manifest_assets: dict[str, dict],
    environment: dict,
    workflow_type: str,
) -> list[str]:
    if not sources:
        raise GroundedImageError(f"{label}.source_assets must contain at least one source asset")
    ids: list[str] = []
    environment_assets: list[dict] = []
    for source_index, source in enumerate(sources):
        source_label = f"{label}.source_assets[{source_index}]"
        if not isinstance(source, dict):
            raise GroundedImageError(f"{source_label} must be an object")
        _reject_unknown(source, {"asset_id", "path", "sha256", "role", "required_approval", "preserve"}, source_label)
        has_asset_id = "asset_id" in source
        has_path = "path" in source
        if has_asset_id == has_path:
            raise GroundedImageError(f"{source_label} must contain exactly one of asset_id or path")
        role = _require_str(source, "role", source_label)
        if role not in SOURCE_ROLES:
            raise GroundedImageError(f"{source_label}.role is not supported: {role}")
        if has_asset_id:
            asset_id = _require_str(source, "asset_id", source_label)
            if asset_id not in manifest_assets:
                raise GroundedImageError(f"{source_label}.asset_id is not in manifest: {asset_id}")
            asset = manifest_assets[asset_id]
            if asset.get("media_type") != "image":
                raise GroundedImageError(f"{source_label}.asset_id is not an image: {asset_id}")
            required_approval = source.get("required_approval", "")
            if required_approval:
                approvals = normalize_values(asset.get("approved_for", []))
                if required_approval.strip().lower() not in approvals:
                    raise GroundedImageError(
                        f"{source_label}.asset_id is not approved for {required_approval}: {asset_id}"
                    )
            source_identity = asset_id
        else:
            path_source = _resolved_source(_require_str(source, "path", source_label), base_dir)
            parsed = urlparse(path_source)
            if parsed.scheme != "file":
                raise GroundedImageError(f"{source_label}.path must resolve to a local file")
            path = Path(unquote(parsed.path))
            if not path.is_file():
                raise GroundedImageError(f"{source_label}.path file does not exist: {path}")
            expected_sha = _require_str(source, "sha256", source_label)
            actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual_sha != expected_sha:
                raise GroundedImageError(f"{source_label}.sha256 does not match path file")
            asset = {
                "filename": path.name,
                "dropbox_path": str(path),
                "category": [role.replace("-reference", "")],
            }
            source_identity = f"path:{source['path']}"
        preserve = source.get("preserve", [])
        if not isinstance(preserve, list) or any(not isinstance(item, str) or not item for item in preserve):
            raise GroundedImageError(f"{source_label}.preserve must be an array of strings")
        if role == "environment-base":
            environment_assets.append(asset)
        ids.append(source_identity)

    if environment["type"] == "real-rider":
        if workflow_type == "conceptual-generation":
            raise GroundedImageError(f"{label}.workflow_type conceptual-generation cannot use a real-rider environment")
        if not environment_assets:
            raise GroundedImageError(f"{label} real-rider environment requires an environment-base source asset")
        keywords = normalize_values(environment["keywords"])
        if not any(_asset_matches_keywords(asset, keywords) for asset in environment_assets):
            raise GroundedImageError(f"{label} environment-base source is not grounded in the requested environment")
    return ids


def _asset_matches_keywords(asset: dict, keywords: set[str]) -> bool:
    haystack = " ".join(
        [
            asset.get("filename", ""),
            asset.get("dropbox_path", ""),
            " ".join(asset.get("category", [])),
        ]
    ).lower().replace("_", "-").replace(" ", "-")
    for keyword in keywords:
        normalized = keyword.lower().replace("_", "-").replace(" ", "-")
        if normalized and normalized in haystack:
            return True
    return False


def _validate_prompt_record(prompt_record: dict, label: str) -> None:
    _reject_unknown(
        prompt_record,
        {"tool", "model", "prompt", "negative_prompt", "edit_steps", "text_policy"},
        f"{label}.prompt_record",
    )
    _require_str(prompt_record, "tool", f"{label}.prompt_record")
    _require_str(prompt_record, "prompt", f"{label}.prompt_record")
    if "model" in prompt_record and not isinstance(prompt_record["model"], str):
        raise GroundedImageError(f"{label}.prompt_record.model must be a string")
    if "negative_prompt" in prompt_record and not isinstance(prompt_record["negative_prompt"], str):
        raise GroundedImageError(f"{label}.prompt_record.negative_prompt must be a string")
    steps = _require_string_array(prompt_record, "edit_steps", f"{label}.prompt_record")
    if not steps:
        raise GroundedImageError(f"{label}.prompt_record.edit_steps must not be empty")
    text_policy = _require_str(prompt_record, "text_policy", f"{label}.prompt_record")
    if text_policy not in TEXT_POLICIES:
        raise GroundedImageError(f"{label}.prompt_record.text_policy is not supported: {text_policy}")


def _validate_output(output: dict, *, label: str, base_dir: Path) -> dict:
    _reject_unknown(output, {"src", "sha256", "width", "height", "format"}, f"{label}.output")
    source = _resolved_source(_require_str(output, "src", f"{label}.output"), base_dir)
    parsed = urlparse(source)
    if parsed.scheme != "file":
        raise GroundedImageError(f"{label}.output.src must resolve to a local file for checksum validation")
    path = Path(unquote(parsed.path))
    if not path.is_file():
        raise GroundedImageError(f"{label}.output.src file does not exist: {path}")
    data = path.read_bytes()
    actual_sha = hashlib.sha256(data).hexdigest()
    expected_sha = _require_str(output, "sha256", f"{label}.output")
    if actual_sha != expected_sha:
        raise GroundedImageError(f"{label}.output.sha256 does not match output file")
    width = _require_positive_int(output, "width", f"{label}.output")
    height = _require_positive_int(output, "height", f"{label}.output")
    actual_width, actual_height = _image_dimensions(data)
    if (actual_width, actual_height) != (width, height):
        raise GroundedImageError(f"{label}.output dimensions do not match output file")
    file_format = _require_str(output, "format", f"{label}.output").lower()
    if file_format not in {"png", "jpg", "jpeg", "gif"}:
        raise GroundedImageError(f"{label}.output.format must be png, jpg, jpeg, or gif")
    return {"source": source, "sha256": actual_sha, "width": width, "height": height}


def _validate_placement(placement: dict, *, label: str) -> None:
    _reject_unknown(
        placement,
        {"aspect_ratio", "crop", "focal_point", "safe_area", "logo_overlay"},
        f"{label}.placement",
    )
    _require_str(placement, "aspect_ratio", f"{label}.placement")
    _require_str(placement, "crop", f"{label}.placement")
    focal = _require_object(placement, "focal_point", f"{label}.placement")
    _reject_unknown(focal, {"x", "y"}, f"{label}.placement.focal_point")
    for axis in ("x", "y"):
        value = focal.get(axis)
        if not isinstance(value, (int, float)) or not (0 <= value <= 1):
            raise GroundedImageError(f"{label}.placement.focal_point.{axis} must be between 0 and 1")
    if "safe_area" in placement and not isinstance(placement["safe_area"], str):
        raise GroundedImageError(f"{label}.placement.safe_area must be a string")
    logo_overlay = placement.get("logo_overlay", "none")
    if not isinstance(logo_overlay, str):
        raise GroundedImageError(f"{label}.placement.logo_overlay must be a string")


def _resolved_source(value: str, base_dir: Path) -> str:
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https", "file"}:
        return value
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.as_uri()
    if str(path).startswith(("projects/", "tools/", "campaign-output/")):
        return (Path(__file__).resolve().parents[2] / path).resolve().as_uri()
    return (base_dir / path).resolve().as_uri()


def _image_dimensions(data: bytes) -> tuple[int, int]:
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data.startswith((b"GIF87a", b"GIF89a")) and len(data) >= 10:
        return struct.unpack("<HH", data[6:10])
    if data.startswith(b"\xff\xd8"):
        index = 2
        while index + 9 < len(data):
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            index += 2
            if marker in {0xD8, 0xD9}:
                continue
            if index + 2 > len(data):
                break
            length = int.from_bytes(data[index : index + 2], "big")
            if length < 2 or index + length > len(data):
                break
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                height = int.from_bytes(data[index + 3 : index + 5], "big")
                width = int.from_bytes(data[index + 5 : index + 7], "big")
                return width, height
            index += length
    raise GroundedImageError("Unsupported or unreadable image dimensions")


def _reject_unknown(obj: dict, allowed: set[str], label: str) -> None:
    unknown = sorted(set(obj) - allowed)
    if unknown:
        raise GroundedImageError(f"{label} has unknown field(s): {', '.join(unknown)}")


def _require_str(obj: dict, field: str, label: str) -> str:
    value = obj.get(field)
    if not isinstance(value, str) or not value:
        raise GroundedImageError(f"{label}.{field} must be a non-empty string")
    return value


def _require_object(obj: dict, field: str, label: str) -> dict:
    value = obj.get(field)
    if not isinstance(value, dict):
        raise GroundedImageError(f"{label}.{field} must be an object")
    return value


def _require_array(obj: dict, field: str, label: str) -> list:
    value = obj.get(field)
    if not isinstance(value, list):
        raise GroundedImageError(f"{label}.{field} must be an array")
    return value


def _require_string_array(obj: dict, field: str, label: str) -> list[str]:
    values = _require_array(obj, field, label)
    if any(not isinstance(item, str) or not item for item in values):
        raise GroundedImageError(f"{label}.{field} must be an array of strings")
    return values


def _require_positive_int(obj: dict, field: str, label: str) -> int:
    value = obj.get(field)
    if not isinstance(value, int) or value <= 0:
        raise GroundedImageError(f"{label}.{field} must be a positive integer")
    return value
