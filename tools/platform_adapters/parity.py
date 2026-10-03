from __future__ import annotations

import copy
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlparse
from zipfile import ZipFile

from tools.rider_campaign_runtime.assets import _read_asset

from .contract import PLATFORMS, VERSION, exact_fields, read_json, run, sha256
from .json_semantics import json_semantic_bytes, json_semantic_equal


COMPONENTS = (
    "campaign", "build", "variants", "composition", "image_workflow", "copy_allocation",
    "html", "assets", "metadata", "qa", "zip_inventory", "integrity", "provenance",
)
NORMALIZATIONS = [
    "campaign.campaign.output_dir: verified per-run output root -> <OUTPUT>",
    "JSON object key order and whitespace: canonical JSON serialization",
    "JSON finite numbers: equal parsed numeric values share representation (1 = 1.0; 0 = -0.0); boolean/string/null types remain distinct",
    "qa-report.json.checks: sort by unique check name (messages/outcomes preserved)",
    "ZIP: compare member paths and uncompressed bytes, not timestamps/compression/container bytes",
    "adapter-provenance.json.platform: verified actual platform -> <PLATFORM>; sidecar stays outside package",
]


def normalized_json(name: str, value):
    value = copy.deepcopy(value)
    if name == "qa-report.json":
        checks = value["checks"]
        names = [check["name"] for check in checks]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate QA check names")
        value["checks"] = sorted(checks, key=lambda check: check["name"])
    return value


def snapshot(output_root: Path, platform: str) -> dict:
    output_root = output_root.resolve()
    spec = read_json(output_root / "campaign.runtime.json")
    if spec["campaign"]["output_dir"] != str(output_root):
        raise ValueError("Undeclared campaign output path")
    spec["campaign"]["output_dir"] = "<OUTPUT>"
    package = output_root / spec["campaign"]["slug"]
    metadata = read_json(package / "campaign-metadata.json")
    assets = read_json(package / "asset-manifest.json")
    qa = normalized_json("qa-report.json", read_json(package / "qa-report.json"))
    if qa["passed"] is not True or not qa["checks"] or any(check["passed"] is not True for check in qa["checks"]):
        raise ValueError("Runtime QA is not passing")
    provenance = read_json(output_root / "adapter-provenance.json")
    exact_fields(provenance, ("contract_version", "adapter_version", "core_version", "project",
                              "runtime", "runtime_version", "platform", "invocation",
                              "input_sha256", "campaign_sha256"))
    exact_fields(provenance["invocation"], ("actor", "explicit"))
    if (provenance["platform"] != platform or provenance["invocation"]["actor"] != "HUMAN"
            or provenance["invocation"]["explicit"] is not True):
        raise ValueError("Invalid adapter provenance")
    for key in ("contract_version", "adapter_version", "core_version", "runtime_version"):
        if provenance[key] != VERSION:
            raise ValueError("Unsupported provenance version")
    provenance["platform"] = "<PLATFORM>"
    inventory = {}
    raw_inventory = {}
    for path in sorted(package.rglob("*")):
        if path.is_symlink():
            raise ValueError("Symlink in package")
        if not path.is_file():
            continue
        name = path.relative_to(package).as_posix()
        raw = path.read_bytes()
        raw_inventory[f"{package.name}/{name}"] = sha256(raw)
        data = json_semantic_bytes(normalized_json(name, read_json(path))) if name.endswith(".json") else raw
        inventory[name] = sha256(data)
    if not any(name.startswith("html/") for name in inventory):
        raise ValueError("Package contains no HTML")
    for asset in assets["assets"]:
        path = package / asset["package_path"]
        if package not in path.resolve().parents:
            raise ValueError("Asset escapes package")
        if (sha256(path.read_bytes()) != asset["sha256"]
                or not json_semantic_equal(path.stat().st_size, asset["size_bytes"])):
            raise ValueError("Packaged asset checksum/size mismatch")
    zip_path = package.with_suffix(".zip")
    directories = [package.name + "/"]
    directories.extend(f"{package.name}/{path.relative_to(package).as_posix()}/"
                       for path in package.rglob("*") if path.is_dir())
    with ZipFile(zip_path) as archive:
        names = archive.namelist()
        files = [info.filename for info in archive.infolist() if not info.is_dir()]
        zipped_directories = [info.filename for info in archive.infolist() if info.is_dir()]
        if (len(names) != len(set(names)) or archive.testzip() is not None
                or set(zipped_directories) != set(directories)):
            raise ValueError("Invalid ZIP inventory")
        zipped = {name: sha256(archive.read(name)) for name in files}
        if zipped != raw_inventory:
            raise ValueError("ZIP bytes differ from package")
    expected_outer = {"campaign.runtime.json", "adapter-provenance.json", package.name, zip_path.name}
    if {path.name for path in output_root.iterdir()} != expected_outer:
        raise ValueError("Undeclared run artifacts")
    return {
        "campaign": spec,
        "build": {"input": spec["build"], "metadata": metadata["build"], "qa": qa["build"]},
        "variants": {"input": spec.get("variants"), "rendered": metadata["variants"]},
        "composition": {"input": spec.get("composition"), "metadata": metadata["composition"], "qa": qa["composition"]},
        "image_workflow": {"input": spec.get("image_workflow"), "metadata": metadata["image_workflow"], "qa": qa["image_workflow"]},
        "copy_allocation": {"input": spec["copy_allocation"], "metadata": metadata["copy_allocation"], "qa": qa["copy_allocation"]},
        "html": {name: digest for name, digest in inventory.items() if name.startswith("html/")},
        "assets": assets,
        "metadata": metadata,
        "qa": qa,
        "zip_inventory": {"files": inventory, "directories": sorted(directories)},
        "integrity": {"qa_passed": True, "asset_checksums": True, "zip_bytes": True, "inventory": inventory},
        "provenance": provenance,
    }


def compare(snapshots: dict) -> dict:
    if set(snapshots) != set(PLATFORMS) or any(set(value) != set(COMPONENTS) for value in snapshots.values()):
        raise ValueError("Parity requires all platforms and every component")
    components = []
    for name in COMPONENTS:
        values = {platform: json_semantic_bytes(snapshots[platform][name]) for platform in PLATFORMS}
        matches = [platform for platform in PLATFORMS if values[platform] == values["cli"]]
        valid = True
        if name == "qa":
            valid = all(value[name].get("passed") is True and value[name].get("checks")
                        and all(check.get("passed") is True for check in value[name]["checks"])
                        for value in snapshots.values())
        if name == "integrity":
            valid = all(all(value[name].get(key) is True for key in ("qa_passed", "asset_checksums", "zip_bytes"))
                        for value in snapshots.values())
        components.append({
            "id": name, "critical": True, "score": round(100 * len(matches) / len(PLATFORMS), 2),
            "passed": len(matches) == len(PLATFORMS) and valid, "matching_platforms": matches,
            "sha256": {platform: sha256(values[platform]) for platform in PLATFORMS},
        })
    return {
        "contract_version": VERSION, "evidence_kind": "deterministic-adapter-runtime-parity",
        "model_behavior_equivalence": "not established by this harness",
        "normalizations": NORMALIZATIONS,
        "components": components,
        "aggregate_score": round(sum(item["score"] for item in components) / len(components), 2),
        "passed": all(item["passed"] for item in components),
    }


def cache_reader(package: Path):
    """Evaluation-only transport substitution, preserving original source URL and filename."""
    cache = {}
    for record in read_json(package / "asset-manifest.json")["assets"]:
        path = (package / record["package_path"]).resolve()
        if package.resolve() not in path.parents:
            raise ValueError("Cache path escapes package")
        data = path.read_bytes()
        if sha256(data) != record["sha256"] or not json_semantic_equal(len(data), record["size_bytes"]):
            raise ValueError("Cache checksum/size mismatch")
        source = record["source"]
        parsed = urlparse(source)
        original_name = Path(unquote(parsed.path)).name or "asset"
        if source in cache:
            raise ValueError("Duplicate cached source")
        cache[source] = (data, original_name)

    def reader(source):
        if source in cache:
            return cache[source]
        if urlparse(source).scheme in ("http", "https"):
            raise ValueError("Uncached remote asset; parity run will not download")
        return _read_asset(source)

    return reader


def evaluate(request: Path, output: Path, *, explicit: bool, cache_package: Path | None = None):
    if explicit is not True:
        raise ValueError("Explicit HUMAN invocation required")
    if output.exists():
        raise ValueError("Parity output must be a new directory")
    reader = cache_reader(cache_package) if cache_package else _read_asset
    snapshots = {}
    with patch("tools.rider_campaign_runtime.assets._read_asset", side_effect=reader):
        for platform in PLATFORMS:
            run(request, platform, output / platform, explicit=explicit)
            snapshots[platform] = snapshot(output / platform, platform)
    report = compare(snapshots)
    report["asset_transport"] = "checksum-verified prior package cache" if cache_package else "canonical runtime asset reader"
    report["runs"] = {
        platform: {
            "variants": value["metadata"]["variants"],
            "qa_checks": len(value["qa"]["checks"]),
            "copy_units": value["metadata"]["copy_allocation"]["content_unit_count"],
            "assets": len(value["assets"]["assets"]),
            "zip_files": len(value["zip_inventory"]["files"]),
            "zip_members": len(value["zip_inventory"]["files"]) + len(value["zip_inventory"]["directories"]),
            "html_sha256": value["html"],
        }
        for platform, value in snapshots.items()
    }
    return report
