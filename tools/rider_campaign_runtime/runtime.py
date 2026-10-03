from __future__ import annotations

from dataclasses import dataclass
import json
import shutil
from pathlib import Path

from tools.asset_selection import load_manifest

from .agents import load_agents
from .assets import create_zip, package_documents, rewrite_and_package_assets, write_asset_manifest
from .footer import render_agent_footer, render_branded_footer, render_outside_broker_footer
from .qa import QAResult, run_qa, write_qa_report
from .scaffold import (
    FOOTER_MODULES,
    catalog,
    compose_html,
    load_scaffold,
    module_includes_header,
    module_kind,
    module_rows,
    static_content_html,
)
from .schema import CampaignSpecError, load_campaign_spec, validate_campaign_spec
from .slots import UsedAsset, apply_module_slots


class RuntimeError(ValueError):
    """Raised when a Rider campaign cannot be safely rendered."""


@dataclass(frozen=True)
class BuildResult:
    package_dir: Path
    zip_path: Path | None
    qa_report: Path
    qa: QAResult
    html_files: dict[str, Path]
    asset_manifest: Path


ROOT = Path(__file__).resolve().parents[2]
RIDER_EMAIL_DIR = ROOT / "projects/the-rider/skills/onbrand-the-rider-email"
SCAFFOLD_PATH = RIDER_EMAIL_DIR / "templates/scaffold/rider-scaffolding.canonical.html"
SLOT_MAP_PATH = RIDER_EMAIL_DIR / "templates/scaffold/rider-scaffolding.slot-map.json"
MODULE_METADATA_PATH = RIDER_EMAIL_DIR / "templates/scaffold/rider-scaffolding.module-metadata.json"
AGENTS_DIR = RIDER_EMAIL_DIR / "data/agents"


def build_campaign(spec_path: Path) -> BuildResult:
    spec_path = spec_path.resolve()
    spec = load_campaign_spec(spec_path)
    base_dir = spec_path.parent
    return build_campaign_from_spec(spec, base_dir=base_dir)


def build_campaign_from_spec(spec: dict, *, base_dir: Path) -> BuildResult:
    validate_campaign_spec(spec)
    scaffold = load_scaffold(SCAFFOLD_PATH, SLOT_MAP_PATH, MODULE_METADATA_PATH)
    available = catalog(scaffold)
    manifest_path = _resolve_path(base_dir, spec["manifest"]["path"])
    assets = load_manifest(manifest_path)
    manifest_assets = {asset["dropbox_id"]: asset for asset in assets}
    manifest_assets.update({f"id:{asset['dropbox_id'].removeprefix('id:')}": asset for asset in assets})
    document_assets: list[UsedAsset] = []
    for document in spec.get("documents", []):
        asset_id = document["asset_id"]
        if asset_id not in manifest_assets:
            raise RuntimeError(f"Document asset_id is not in manifest: {asset_id}")
        asset = manifest_assets[asset_id]
        if asset.get("media_type") != "pdf":
            raise RuntimeError(f"Document asset_id is not a PDF: {asset_id}")
        if "body" not in {item.lower() for item in asset.get("approved_for", [])}:
            raise RuntimeError(f"Document asset_id is not approved for body use: {asset_id}")
        document_assets.append(
            UsedAsset(
                source=asset["public_url"],
                role=document["role"],
                identity=asset["dropbox_id"],
                filename=asset["filename"],
                dropbox_path=asset["dropbox_path"],
            )
        )

    requested_module_ids = [module["id"] for module in spec["modules"]]
    unknown = sorted(set(requested_module_ids) - set(available))
    if unknown:
        raise RuntimeError("Unknown module(s): " + ", ".join(unknown))
    footer_selected = [module_id for module_id in requested_module_ids if module_id in FOOTER_MODULES]
    if footer_selected:
        raise RuntimeError("Campaign modules must not include footer modules; variants append exactly one footer")
    _validate_static_decisions(spec, scaffold, requested_module_ids)
    _validate_module_compatibility(scaffold, requested_module_ids)
    if not any(module_kind(scaffold, module_id) == "hero" for module_id in requested_module_ids):
        raise RuntimeError("Campaign must include at least one Rider hero/header module")

    content_rows: list[str] = []
    content_asset_hints: list[UsedAsset] = []
    for module in spec["modules"]:
        module_id = module["id"]
        if module_kind(scaffold, module_id) == "static" and module.get("slots"):
            raise RuntimeError(f"{module_id} is a locked static block and cannot define slots")
        rows = "".join(module_rows(scaffold, module_id))
        rows, used = apply_module_slots(
            module_id,
            rows,
            scaffold.slot_map.get(module_id, {}),
            module.get("slots", {}),
            manifest_assets=manifest_assets,
        )
        content_rows.append(rows)
        content_asset_hints.extend(used)

    variants = spec["variants"]
    agents = load_agents(AGENTS_DIR, assets, variants.get("agents", "all")) if variants.get("agents", "all") else []
    html_by_variant: dict[str, str] = {}
    asset_hints: list[tuple[str, UsedAsset]] = []
    expected_variants: set[str] = set()

    if variants.get("branded", True):
        footer_rows, used = render_branded_footer(module_rows(scaffold, "BRANDED FOOTER"))
        variant = "branded"
        expected_variants.add(variant)
        html_by_variant[variant] = compose_html(scaffold, content_rows + footer_rows)
        asset_hints.extend((variant, item) for item in content_asset_hints + used)

    if variants.get("outside_broker", True):
        footer_rows, used = render_outside_broker_footer(
            module_rows(scaffold, "OUTSIDE-BROKER CUSTOMIZABLE FOOTER"),
            spec.get("outside_broker", {}),
            manifest_assets,
        )
        variant = "outside-broker-customizable"
        expected_variants.add(variant)
        html_by_variant[variant] = compose_html(scaffold, content_rows + footer_rows)
        asset_hints.extend((variant, item) for item in content_asset_hints + used)

    for agent in agents:
        footer_rows, used = render_agent_footer(module_rows(scaffold, "IN-HOUSE AGENT FOOTER"), agent)
        variant = f"agent-{agent['id']}"
        expected_variants.add(variant)
        html_by_variant[variant] = compose_html(scaffold, content_rows + footer_rows)
        asset_hints.extend((variant, item) for item in content_asset_hints + used)

    if not html_by_variant:
        raise RuntimeError("At least one output variant is required")
    static_content = static_content_html(scaffold)
    _validate_static_rendering(spec["static_blocks"], static_content, html_by_variant)

    campaign = spec["campaign"]
    output_root = _resolve_path(base_dir, campaign["output_dir"])
    output_root.mkdir(parents=True, exist_ok=True)
    final_package_dir = output_root / campaign["slug"]
    if final_package_dir.exists():
        runtime_markers = (
            final_package_dir / "asset-manifest.json",
            final_package_dir / "qa-report.json",
        )
        if not final_package_dir.is_dir() or not all(path.is_file() for path in runtime_markers):
            raise RuntimeError(f"Refusing to replace non-runtime output directory: {final_package_dir}")
    package_dir = output_root / f".{campaign['slug']}.building"
    building_marker = package_dir / ".onbrand-building"
    if package_dir.exists():
        if not package_dir.is_dir() or not building_marker.is_file():
            raise RuntimeError(f"Refusing to replace unrecognized staging directory: {package_dir}")
        shutil.rmtree(package_dir)
    (package_dir / "html").mkdir(parents=True)
    building_marker.write_text("OnBrand Rider runtime staging directory\n", encoding="utf-8")

    deployment = spec.get("deployment", {})
    asset_mode = deployment.get("asset_mode", "relative-review")
    rewritten_html, packaged_assets = rewrite_and_package_assets(
        html_by_variant,
        asset_hints,
        package_dir,
        asset_mode=asset_mode,
        hosted_asset_base_url=deployment.get("hosted_asset_base_url"),
    )
    packaged_assets.extend(package_documents(document_assets, package_dir))
    asset_manifest = write_asset_manifest(package_dir, campaign, packaged_assets, asset_mode=asset_mode)

    html_files: dict[str, Path] = {}
    for variant, html in sorted(rewritten_html.items()):
        path = package_dir / "html" / f"{campaign['slug']}-{variant}.html"
        path.write_text(html, encoding="utf-8")
        html_files[variant] = path

    (package_dir / "campaign-metadata.json").write_text(
        json.dumps(
            {
                "slug": campaign["slug"],
                "title": campaign["title"],
                "subject": campaign.get("subject", ""),
                "preview_text": campaign.get("preview_text", ""),
                "modules": requested_module_ids,
                "static_blocks": spec["static_blocks"],
                "variants": sorted(rewritten_html),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    qa = run_qa(
        package_dir,
        rewritten_html,
        expected_variants=expected_variants,
        agent_variant_count=len(agents),
        static_blocks=spec["static_blocks"],
        static_content=static_content,
    )
    qa_report = write_qa_report(package_dir / "qa-report.json", qa)
    zip_path = None
    if qa.passed:
        if final_package_dir.exists():
            shutil.rmtree(final_package_dir)
        building_marker.unlink()
        package_dir.rename(final_package_dir)
        package_dir = final_package_dir
        html_files = {variant: package_dir / "html" / path.name for variant, path in html_files.items()}
        asset_manifest = package_dir / asset_manifest.name
        qa_report = package_dir / qa_report.name
        zip_path = create_zip(package_dir)
    return BuildResult(
        package_dir=package_dir,
        zip_path=zip_path,
        qa_report=qa_report,
        qa=qa,
        html_files=html_files,
        asset_manifest=asset_manifest,
    )


def _resolve_path(base_dir: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    if str(path).startswith(("campaign-output", "tools/", "projects/")):
        return (ROOT / path).resolve()
    candidate = (base_dir / path).resolve()
    if candidate.exists():
        return candidate
    return (ROOT / path).resolve()


def _validate_static_decisions(spec: dict, scaffold, requested_module_ids: list[str]) -> None:
    decisions = spec.get("static_blocks", [])
    static_ids = set(scaffold.static_boundaries)
    seen: dict[str, str] = {}
    for index, item in enumerate(decisions):
        static_id = item["id"]
        if static_id in seen:
            raise RuntimeError(f"Duplicate static block decision: {static_id}")
        seen[static_id] = item["decision"]
    missing = sorted(static_ids - set(seen))
    unknown = sorted(set(seen) - static_ids)
    if missing:
        raise RuntimeError("Missing static block decision(s): " + ", ".join(missing))
    if unknown:
        raise RuntimeError("Unknown static block decision(s): " + ", ".join(unknown))

    included = {static_id for static_id, decision in seen.items() if decision == "include"}
    selected_static = [module_id for module_id in requested_module_ids if module_id in static_ids]
    duplicates = sorted({module_id for module_id in selected_static if selected_static.count(module_id) > 1})
    if duplicates:
        raise RuntimeError("Static block selected more than once: " + ", ".join(duplicates))
    missing_in_modules = sorted(included - set(selected_static))
    if missing_in_modules:
        raise RuntimeError("Included static block(s) missing from modules: " + ", ".join(missing_in_modules))
    excluded_in_modules = sorted(set(selected_static) - included)
    if excluded_in_modules:
        raise RuntimeError("Excluded static block(s) present in modules: " + ", ".join(excluded_in_modules))


def _validate_module_compatibility(scaffold, requested_module_ids: list[str]) -> None:
    selected_headers = [module_id for module_id in requested_module_ids if module_kind(scaffold, module_id) == "header"]
    header_bearing_heroes = [
        module_id
        for module_id in requested_module_ids
        if module_kind(scaffold, module_id) == "hero" and module_includes_header(scaffold, module_id)
    ]
    if len(selected_headers) > 1:
        raise RuntimeError("Campaign modules may include at most one standalone header module")
    if selected_headers and header_bearing_heroes:
        raise RuntimeError(
            "Standalone header module(s) are incompatible with hero module(s) that include their own header: "
            + ", ".join(selected_headers + header_bearing_heroes)
        )


def _validate_static_rendering(
    decisions: list[dict],
    static_content: dict[str, str],
    html_by_variant: dict[str, str],
) -> None:
    decision_map = {item["id"]: item["decision"] for item in decisions}
    for variant, html in html_by_variant.items():
        for static_id, static_html in static_content.items():
            count = html.count(static_html)
            expected = 1 if decision_map[static_id] == "include" else 0
            if count != expected:
                raise RuntimeError(
                    f"Static block lock failed for {variant}/{static_id}: expected {expected}, found {count}"
                )
