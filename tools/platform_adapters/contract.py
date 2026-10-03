from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re

from tools.rider_campaign_runtime.composition import create_composition_plan
from tools.rider_campaign_runtime.runtime import (
    ROOT, SCAFFOLD_PATH, SLOT_MAP_PATH, MODULE_METADATA_PATH, build_campaign_from_spec,
)
from tools.rider_campaign_runtime.scaffold import load_scaffold
from tools.rider_campaign_runtime.schema import validate_campaign_spec

from .json_semantics import json_semantic_equal


VERSION = "1.0"
PLATFORMS = ("cli", "codex", "claude")
ATTACHMENTS = {
    "brief": None,
    "selection": None,
    "composition": "composition",
    "image": "image_workflow",
    "copy": "copy_allocation",
}


def rider_selection(value):
    return create_composition_plan(
        load_scaffold(SCAFFOLD_PATH, SLOT_MAP_PATH, MODULE_METADATA_PATH), value
    )


RUNTIMES = {
    "rider-campaign": (VERSION, validate_campaign_spec, build_campaign_from_spec, rider_selection),
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def exact_fields(value, required, optional=()):
    if not isinstance(value, dict):
        raise ValueError("Contract must be a JSON object")
    missing = set(required) - value.keys()
    unknown = value.keys() - set(required) - set(optional)
    if missing or unknown:
        raise ValueError(f"Contract fields: missing={sorted(missing)}, unknown={sorted(unknown)}")


def project_contract(slug: str, root: Path = ROOT) -> dict:
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Invalid project slug")
    path = root / "projects" / slug / "adapter.json"
    if not path.is_file():
        raise ValueError(f"Unsupported project: {slug}")
    descriptor = read_json(path)
    exact_fields(descriptor, ("contract_version", "adapter_version", "core_version",
                              "project", "runtime", "runtime_version"))
    if descriptor["project"] != slug or any(
        descriptor[key] != VERSION for key in ("contract_version", "adapter_version", "core_version")
    ):
        raise ValueError("Unsupported project contract/core/adapter version")
    runtime = descriptor["runtime"]
    if runtime is not None and (
        not isinstance(runtime, str) or runtime not in RUNTIMES
        or descriptor["runtime_version"] != RUNTIMES[runtime][0]
    ):
        raise ValueError("Unsupported runtime/version")
    if runtime is None and descriptor["runtime_version"] is not None:
        raise ValueError("Scaffold project cannot declare a runtime version")
    return descriptor


def prepare(request_path: Path, platform: str, *, explicit: bool) -> dict:
    if platform not in PLATFORMS:
        raise ValueError("Unsupported platform")
    if explicit is not True:
        raise ValueError("Explicit HUMAN invocation required")
    request_path = request_path.resolve()
    request = read_json(request_path)
    exact_fields(request, ("contract_version", "adapter_version", "core_version", "project",
                           "runtime", "runtime_version", "campaign_spec", "inputs", "invocation"))
    descriptor = project_contract(request["project"])
    for key in descriptor:
        if request[key] != descriptor[key]:
            raise ValueError(f"Unsupported request {key}")
    exact_fields(request["invocation"], ("actor", "explicit"))
    if request["invocation"]["actor"] != "HUMAN" or request["invocation"]["explicit"] is not True:
        raise ValueError("Explicit HUMAN invocation required")
    if descriptor["runtime"] is None:
        raise ValueError("Project runtime is not implemented; references only")
    if not isinstance(request["campaign_spec"], str) or not request["campaign_spec"]:
        raise ValueError("campaign_spec must be a file path")
    spec_path = (request_path.parent / request["campaign_spec"]).resolve()
    spec = read_json(spec_path)
    if not isinstance(spec, dict):
        raise ValueError("Canonical campaign must be a JSON object")
    runtime_version, validator, _, selection_builder = RUNTIMES[descriptor["runtime"]]
    if spec.get("schema_version") != runtime_version:
        raise ValueError("Unsupported canonical campaign schema version")
    validator(spec)
    if not isinstance(request["inputs"], dict) or set(request["inputs"]) - ATTACHMENTS.keys():
        raise ValueError("Unsupported input roles")
    inputs = {}
    for role, attachment in request["inputs"].items():
        exact_fields(attachment, ("path", "sha256"))
        if not isinstance(attachment["path"], str) or not attachment["path"]:
            raise ValueError("Input path must be a nonempty string")
        path = (request_path.parent / attachment["path"]).resolve()
        digest = sha256(path.read_bytes())
        if attachment["sha256"] != digest:
            raise ValueError(f"Input checksum mismatch: {role}")
        value = read_json(path)
        key = ATTACHMENTS[role]
        if key and not json_semantic_equal(value, spec.get(key)):
            raise ValueError(f"Approval file differs from canonical campaign: {role}")
        if role == "selection":
            plan = selection_builder(value)
            if not json_semantic_equal(plan, spec.get("composition")):
                raise ValueError("Selection file differs from canonical composition")
        inputs[role] = digest
    return {
        "spec": spec, "base_dir": spec_path.parent,
        "provenance": {
            "contract_version": VERSION, "adapter_version": VERSION, "core_version": VERSION,
            "project": descriptor["project"], "runtime": descriptor["runtime"],
            "runtime_version": descriptor["runtime_version"], "platform": platform,
            "invocation": request["invocation"], "input_sha256": inputs,
            "campaign_sha256": sha256(canonical_bytes(spec)),
        },
    }


def run(request_path: Path, platform: str, output_root: Path, *, explicit: bool, build=True):
    prepared = prepare(request_path, platform, explicit=explicit)
    output_root = output_root.resolve()
    # Per-run output isolation is the only permitted campaign transformation.
    spec = copy.deepcopy(prepared["spec"])
    spec["campaign"]["output_dir"] = str(output_root)
    if output_root.exists() and any(output_root.iterdir()):
        expected = {"campaign.runtime.json", "adapter-provenance.json",
                    spec["campaign"]["slug"], spec["campaign"]["slug"] + ".zip"}
        provenance_path = output_root / "adapter-provenance.json"
        if (not provenance_path.is_file() or not (output_root / "campaign.runtime.json").is_file()
                or {path.name for path in output_root.iterdir()} - expected
                or read_json(provenance_path).get("platform") != platform):
            raise ValueError("Refusing to replace unrecognized adapter output")
    output_root.mkdir(parents=True, exist_ok=True)
    write_json(output_root / "campaign.runtime.json", spec)
    write_json(output_root / "adapter-provenance.json", prepared["provenance"])
    if not build:
        return None
    _, _, builder, _ = RUNTIMES[prepared["provenance"]["runtime"]]
    result = builder(spec, base_dir=prepared["base_dir"])
    if not result.qa.passed or result.zip_path is None:
        raise ValueError("Shared runtime QA blocked the adapter build")
    return result
