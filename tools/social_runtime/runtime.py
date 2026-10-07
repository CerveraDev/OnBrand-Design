"""Build a reviewable social package from a canonical social spec."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import shutil

from tools.asset_selection.manifest_source import validate_manifest_source_config
from tools.asset_selection.selector import ManifestError
from tools.asset_selection.social_approvals import SocialApprovalError, load_social_approvals

from .assets import SocialAssetError, load_social_assets, resolve_direct_asset
from .copy_allocation import SocialCopyError, validate_copy_allocation
from .crops import CropError, validate_crop
from .formats import FORMATS_PATH, FormatError, load_formats, require_format
from .qa import QAResult, run_qa, write_qa_report
from .schema import validate_social_spec
from .templates import TemplateError, load_template, match_slides


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_MANIFEST = "social-package.json"


class SocialRuntimeError(ValueError):
    """Raised when a social build is refused, with the specific reason."""


@dataclass(frozen=True)
class BuildResult:
    package_dir: Path
    zip_path: Path | None
    qa_report: Path
    qa: QAResult
    package_manifest: Path
    asset_manifest: Path


def build_social(spec_path: Path | str) -> BuildResult:
    spec_path = Path(spec_path).resolve()
    return build_social_from_spec(json.loads(spec_path.read_text(encoding="utf-8")), base_dir=spec_path.parent)


def build_social_from_spec(
    spec: dict,
    *,
    base_dir: Path,
    project_dir: Path | None = None,
    manifest_path: Path | None = None,
    formats_path: Path = FORMATS_PATH,
) -> BuildResult:
    validate_social_spec(spec)
    base_dir = Path(base_dir).resolve()
    try:
        return _build(spec, base_dir, project_dir, manifest_path, formats_path)
    except (FormatError, TemplateError, SocialAssetError, SocialApprovalError, ManifestError,
            CropError, SocialCopyError) as err:
        raise SocialRuntimeError(str(err)) from err


def _build(spec, base_dir, project_dir, manifest_path, formats_path) -> BuildResult:
    mode = spec["build"]["mode"]
    audience = spec["audience"]
    format_id = spec["composition"]["format"]
    project_dir = Path(project_dir) if project_dir else ROOT / "projects" / spec["campaign"]["project"]
    warnings: list[str] = []

    sidecar = load_formats(formats_path)
    fmt = require_format(sidecar, format_id)
    template = load_template(project_dir / "social" / "templates", spec["composition"]["template"])
    code = template["code"]
    if template["kind"] != fmt["kind"] or format_id not in template["formats"]:
        raise TemplateError(f"Template {code} does not support format '{format_id}'")
    if audience not in template["audiences"]:
        raise TemplateError(f"Template {code} is not available to the {audience} audience")
    if not fmt["min_slides"] <= len(spec["slides"]) <= fmt["max_slides"]:
        raise FormatError(
            f"Format '{format_id}' takes {fmt['min_slides']}-{fmt['max_slides']} slides; got {len(spec['slides'])}"
        )
    steps = match_slides(template, [slide["role"] for slide in spec["slides"]])
    for index, (slide, step) in enumerate(zip(spec["slides"], steps), start=1):
        locked = sorted(set(slide["text"]) & set(step["locked"]))
        if locked:
            raise TemplateError(f"Slide {index} overrides locked content: {', '.join(locked)}")
        unknown = sorted(set(slide["text"]) - set(step["slots"]))
        if unknown:
            raise TemplateError(f"Slide {index} fills slot(s) template {code} does not define: {', '.join(unknown)}")
        missing = sorted(s for s, rule in step["slots"].items() if rule["required"] and s not in slide["text"])
        if missing:
            raise TemplateError(f"Slide {index} leaves required slot(s) empty: {', '.join(missing)}")

    if template["approval_status"] != "approved":
        if mode == "release" or audience == "outside-broker":
            raise TemplateError(f"Template {code} is a draft; {audience} {mode} builds need an approved template")
        warnings.append(f"Template {code} is a draft pending owner approval")
    if fmt["verified_date"] is None:
        if mode == "release":
            raise FormatError(
                f"Format '{format_id}' values are unverified in sidecar {sidecar['sidecar_version']}; "
                "release builds need a verified, dated format"
            )
        warnings.append(f"Format '{format_id}' values are provisional and unverified")

    if manifest_path is None:
        manifest_path = validate_manifest_source_config(project_dir / "manifest-source.json")["local_cache_path"]
    overlay_path = project_dir / "asset-approvals.social.json"
    assets = load_social_assets(manifest_path, overlay_path, audience=audience)
    never_social_roles = load_social_approvals(overlay_path)["never_social_roles"]

    crops = {
        crop["id"]: validate_crop(crop, assets=assets, format_id=format_id, fmt=fmt, base_dir=base_dir, mode=mode)
        for crop in spec.get("crops", [])
    }
    used: dict[str, dict] = {}
    slide_images = []
    for index, slide in enumerate(spec["slides"], start=1):
        image = slide["image"]
        if "asset" in image:
            asset = resolve_direct_asset(assets, image["asset"], fmt=fmt)
            used[asset["filename"]] = {**asset, "use": "direct"}
            slide_images.append({"kind": "asset", "filename": asset["filename"], "src": asset["public_url"]})
            continue
        crop = crops.get(image["crop"])
        if crop is None:
            raise CropError(f"Slide {index} references undeclared crop '{image['crop']}'")
        source = next(a for a in assets if a["filename"] == crop["source_asset"])
        used.setdefault(source["filename"], {**source, "use": "crop-source"})
        if crop["output"] is None:
            warnings.append(f"Crop '{crop['id']}' is planned; slide {index} shows its uncropped source")
            slide_images.append({"kind": "crop", "crop_id": crop["id"], "filename": source["filename"],
                                 "src": None, "pending": True, "source_src": source["public_url"]})
        else:
            slide_images.append({"kind": "crop", "crop_id": crop["id"], "filename": crop["output"]["name"],
                                 "src": "images/" + crop["output"]["name"]})
    unused = sorted(set(crops) - {img.get("crop_id") for img in slide_images})
    if unused:
        raise CropError("Crop(s) declared but not used by any slide: " + ", ".join(unused))
    if any(item["use"] == "direct" for item in used.values()):
        warnings.append(
            "Directly used assets are matched by manifest orientation only; "
            "their pixel dimensions and file sizes are not verified"
        )

    allocation = validate_copy_allocation(spec, steps, mode=mode, base_dir=base_dir)
    if allocation["status"] != "approved":
        warnings.append("Copy allocation is a draft pending approval")
    if "cross_medium" not in spec and audience == "in-house":
        warnings.append("No cross_medium surface was declared; email repetition was not checked")

    variants = spec.get("variants", {"branded": {}})
    representative = spec["build"].get("representative_variant", sorted(variants)[0])
    built = [representative] if mode == "composition-preview" else sorted(variants)
    slides = [
        {"index": index, "role": slide["role"], "image": image, "text": dict(slide["text"]),
         "locked": dict(step["locked"]), "alt_text": slide["alt_text"]}
        for index, (slide, step, image) in enumerate(zip(spec["slides"], steps, slide_images), start=1)
    ]
    package = {
        "schema_version": spec["schema_version"],
        "medium": "social",
        "campaign": {k: v for k, v in spec["campaign"].items() if k != "output_dir"},
        "audience": audience,
        "build": {"mode": mode, "variants_built": built, "deliverable": mode != "smoke-test"},
        "composition": {
            "template": code, "label": template["label"], "template_status": template["approval_status"],
            "format": format_id, "width": fmt["width"], "height": fmt["height"],
            "sidecar_version": sidecar["sidecar_version"], "format_verified_date": fmt["verified_date"],
        },
        "variants": {
            name: {"contact": variants[name].get("contact"), "caption": spec["caption"],
                   "hashtags": list(spec.get("hashtags", [])), "slides": slides}
            for name in built
        },
    }

    package_dir = _prepare_package_dir(base_dir, spec["campaign"])
    for crop in crops.values():
        if crop["output"] is not None:
            (package_dir / "images").mkdir(exist_ok=True)
            shutil.copyfile(crop["output"]["path"], package_dir / "images" / crop["output"]["name"])
    package_manifest = _write_json(package_dir / PACKAGE_MANIFEST, package)
    asset_manifest = _write_json(package_dir / "asset-manifest.json", {
        "assets": [
            {key: asset[key] for key in ("filename", "public_url", "orientation", "category", "social_roles",
                                         "social_cluster", "third_party_rights", "use") if key in asset}
            for _, asset in sorted(used.items())
        ],
        "crops": [
            {**{k: v for k, v in crop.items() if k != "output"},
             "output": None if crop["output"] is None else {k: v for k, v in crop["output"].items() if k != "path"}}
            for _, crop in sorted(crops.items())
        ],
    })
    (package_dir / "preview.html").write_text(_preview_html(package, warnings), encoding="utf-8")

    qa = run_qa(
        package_dir, package=package, template=template, steps=steps, fmt=fmt,
        resolved_assets=list(used.values()), crops=list(crops.values()),
        never_social_roles=never_social_roles, allocation=allocation, warnings=warnings,
    )
    qa_report = write_qa_report(package_dir / "qa-report.json", qa)
    zip_path = None
    if qa.passed and mode != "smoke-test":
        zip_path = Path(shutil.make_archive(str(package_dir), "zip", root_dir=package_dir.parent, base_dir=package_dir.name))
    return BuildResult(package_dir, zip_path, qa_report, qa, package_manifest, asset_manifest)


def _prepare_package_dir(base_dir: Path, campaign: dict) -> Path:
    output_dir = Path(campaign["output_dir"]).expanduser()
    if not output_dir.is_absolute():
        output_dir = base_dir / output_dir
    package_dir = output_dir.resolve() / campaign["slug"]
    if package_dir.exists():
        if any(package_dir.iterdir()) and not (package_dir / PACKAGE_MANIFEST).is_file():
            raise SocialRuntimeError(f"Refusing to replace a directory that is not a social package: {package_dir.name}")
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)
    return package_dir


def _write_json(path: Path, value) -> Path:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _preview_html(package: dict, warnings: list[str]) -> str:
    composition = package["composition"]
    ratio = f"{composition['width']} / {composition['height']}"
    parts = [
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">",
        f"<title>{escape(package['campaign']['slug'])} social preview</title>",
        "<style>body{font:14px/1.5 system-ui,sans-serif;margin:24px;color:#222}"
        ".slides{display:flex;flex-wrap:wrap;gap:16px}.slide{width:270px}"
        f".frame{{aspect-ratio:{ratio};background:#ddd;overflow:hidden}}"
        ".frame img{width:100%;height:100%;object-fit:cover;display:block}"
        ".pending{outline:3px dashed #b00}dt{font-weight:600}dd{margin:0 0 6px}"
        ".warn{color:#b00}</style></head><body>",
        f"<h1>{escape(composition['label'])} ({escape(composition['template'])})</h1>",
        f"<p>{escape(package['build']['mode'])} · {escape(package['audience'])} · "
        f"{escape(composition['format'])} {composition['width']}×{composition['height']}</p>",
    ]
    if warnings:
        parts.append("<ul class=\"warn\">" + "".join(f"<li>{escape(w)}</li>" for w in warnings) + "</ul>")
    for name, variant in sorted(package["variants"].items()):
        parts.append(f"<h2>Variant: {escape(name)}</h2><div class=\"slides\">")
        for slide in variant["slides"]:
            image = slide["image"]
            src = image.get("src") or image.get("source_src") or ""
            pending = " pending" if image.get("pending") else ""
            parts.append(
                f"<div class=\"slide\"><div class=\"frame{pending}\">"
                f"<img src=\"{escape(src, quote=True)}\" alt=\"{escape(slide['alt_text'], quote=True)}\"></div>"
                f"<p><strong>{slide['index']}. {escape(slide['role'])}</strong> · {escape(image['filename'])}</p><dl>"
            )
            for slot, text in {**slide["locked"], **slide["text"]}.items():
                parts.append(f"<dt>{escape(slot)}</dt><dd>{escape(text)}</dd>")
            parts.append(f"<dt>alt text</dt><dd>{escape(slide['alt_text'])}</dd></dl></div>")
        parts.append("</div>")
        parts.append(f"<h3>Caption</h3><p>{escape(variant['caption'])}</p>")
        parts.append(f"<p>{escape(' '.join(variant['hashtags']))}</p>")
        if variant["contact"]:
            parts.append("<h3>Contact</h3><p>" + " · ".join(escape(v) for v in variant["contact"].values()) + "</p>")
    parts.append("</body></html>\n")
    return "".join(parts)
