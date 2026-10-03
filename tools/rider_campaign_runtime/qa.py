from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

from .assets import extract_image_refs


@dataclass(frozen=True)
class QAResult:
    passed: bool
    checks: list[dict]
    build: dict | None = None
    composition: dict | None = None
    image_workflow: dict | None = None


def run_qa(
    package_dir: Path,
    html_by_variant: dict[str, str],
    *,
    expected_variants: set[str],
    agent_variant_count: int,
    static_blocks: list[dict] | None = None,
    static_content: dict[str, str] | None = None,
    build_metadata: dict | None = None,
    composition_metadata: dict | None = None,
    image_workflow_metadata: dict | None = None,
) -> QAResult:
    checks: list[dict] = []
    static_blocks = static_blocks or []
    static_content = static_content or {}
    _check(checks, "variant-count", set(html_by_variant) == expected_variants, f"{len(html_by_variant)} variants rendered")
    _check(checks, "agent-variant-count", sum(1 for name in html_by_variant if name.startswith("agent-")) == agent_variant_count, f"{agent_variant_count} agent variants expected")
    _check(
        checks,
        "static-decisions-accounted",
        {item["id"] for item in static_blocks} == set(static_content),
        "static block decisions match scaffold catalog",
    )
    for variant, html in sorted(html_by_variant.items()):
        label = f"html:{variant}"
        _check(checks, f"{label}:row1", 'class="row row-1"' in html, "row 1 shared CSS row is present")
        _check(checks, f"{label}:head", "<head>" in html and "fonts.googleapis.com" in html, "head and linked fonts preserved")
        _check(checks, f"{label}:outlook", "<!--[if mso]>" in html and "urn:schemas-microsoft-com:vml" in html, "Outlook/VML conditionals preserved")
        _check(
            checks,
            f"{label}:markers",
            all(token not in html for token in ("START - ", "END - ", "#55ebb9", "#ff81fb", "#ffd675", "#75edff")),
            "authoring markers omitted",
        )
        _check(checks, f"{label}:canonical-typos", "INFORMAITON" not in html and "ARTTS" not in html, "canonical typo regressions absent")
        _check(checks, f"{label}:placeholders", "{{" not in html and "}}" not in html, "template placeholders absent")
        _check(checks, f"{label}:unsafe-paths", not _has_unsafe_local_path(html), "no local corpus/temp paths leaked")
        _check(checks, f"{label}:unsafe-schemes", not _has_unsafe_scheme(html), "no unsafe href/src schemes")
        _check(checks, f"{label}:palette", "#000000" in html and "#ffffff" in html, "Rider palette present")
        refs = extract_image_refs(html)
        for ref in refs:
            if ref.startswith("../images/"):
                _check(checks, f"{label}:asset:{ref}", (package_dir / "html" / ref).resolve().is_file(), "relative image resolves in package")
            elif ref.startswith("http://") or ref.startswith("https://"):
                _check(checks, f"{label}:external:{ref}", False, "review HTML should not leave image URLs external")
    manifest_path = package_dir / "asset-manifest.json"
    metadata_path = package_dir / "campaign-metadata.json"
    _check(checks, "campaign-metadata", metadata_path.is_file(), "campaign metadata exists")
    if metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        _check(
            checks,
            "campaign-metadata-variants",
            set(metadata.get("variants", [])) == expected_variants,
            "campaign metadata lists every rendered variant",
        )
        _check(
            checks,
            "campaign-metadata-build",
            metadata.get("build") == build_metadata,
            "campaign metadata records effective build mode and variant scope",
        )
        _check(
            checks,
            "campaign-metadata-composition",
            metadata.get("composition", {}) == (composition_metadata or {}),
            "campaign metadata records approved composition plan",
        )
        _check(
            checks,
            "campaign-metadata-image-workflow",
            metadata.get("image_workflow", {}) == (image_workflow_metadata or {}),
            "campaign metadata records generated image provenance summary",
        )
    _check(checks, "asset-manifest", manifest_path.is_file(), "asset manifest exists")
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        paths = {item["package_path"] for item in manifest.get("assets", [])}
        for item in manifest.get("assets", []):
            path = item["package_path"]
            asset_path = package_dir / path
            exists = asset_path.is_file()
            _check(checks, f"manifest-path:{path}", exists, "manifest asset path exists")
            if exists:
                data = asset_path.read_bytes()
                _check(
                    checks,
                    f"manifest-checksum:{path}",
                    hashlib.sha256(data).hexdigest() == item.get("sha256"),
                    "manifest checksum matches packaged file",
                )
                _check(
                    checks,
                    f"manifest-size:{path}",
                    len(data) == item.get("size_bytes"),
                    "manifest byte size matches packaged file",
                )
        package_files = {
            str(path.relative_to(package_dir))
            for folder in (package_dir / "images", package_dir / "documents")
            if folder.is_dir()
            for path in folder.glob("*")
            if path.is_file()
        }
        _check(checks, "manifest-covers-assets", package_files == paths, "asset manifest matches packaged asset files")
        _check(checks, "manifest-checksums", all(item.get("sha256") and item.get("size_bytes", 0) > 0 for item in manifest.get("assets", [])), "assets have checksums and sizes")
        _check(checks, "no-agent-diego", not any("diego ojeda" in item.get("dropbox_path", "").lower() for item in manifest.get("assets", []) if "agent" in item.get("role", "")), "Diego likeness assets excluded from agent footers")
        _check(
            checks,
            "manifest-image-workflow",
            manifest.get("image_workflow", {}) == (image_workflow_metadata or {}),
            "asset manifest records generated image provenance summary",
        )
        workflow_ids = {
            item["image_id"]
            for item in (image_workflow_metadata or {}).get("items", [])
        }
        packaged_workflow_ids = {
            item.get("image_workflow_id", "")
            for item in manifest.get("assets", [])
            if item.get("image_workflow_id")
        }
        _check(
            checks,
            "manifest-image-workflow-assets",
            packaged_workflow_ids == workflow_ids,
            "packaged generated image assets match workflow items",
        )
    return QAResult(
        passed=all(item["passed"] for item in checks),
        checks=checks,
        build=build_metadata,
        composition=composition_metadata,
        image_workflow=image_workflow_metadata,
    )


def write_qa_report(path: Path, result: QAResult) -> Path:
    path.write_text(
        json.dumps(
            {
                "passed": result.passed,
                "build": result.build or {},
                "composition": result.composition or {},
                "image_workflow": result.image_workflow or {},
                "checks": result.checks,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _check(checks: list[dict], name: str, passed: bool, message: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "message": message})


def _has_unsafe_local_path(html: str) -> bool:
    lowered = html.lower()
    return any(token in lowered for token in ("/users/", "/private/tmp", "/var/folders", "tools/dropbox-manifest"))


def _has_unsafe_scheme(html: str) -> bool:
    for attr in re.findall(r'\b(?:href|src)=["\']([^"\']+)["\']', html, flags=re.IGNORECASE):
        lowered = attr.lower()
        if lowered.startswith(("http://", "https://", "mailto:", "tel:", "../images/")):
            continue
        return True
    return False
