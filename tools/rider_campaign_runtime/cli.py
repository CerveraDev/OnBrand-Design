#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from .composition import CompositionError, create_composition_plan, write_catalog_artifacts
    from .runtime import RuntimeError, build_campaign
    from .runtime import MODULE_METADATA_PATH, SCAFFOLD_PATH, SLOT_MAP_PATH
    from .scaffold import load_scaffold
    from .schema import CampaignSpecError
    from .grounded_images import GroundedImageError
    from .slots import SlotError
    from .agents import AgentError
    from .assets import AssetPackageError
except ImportError:  # Allow direct execution: python3 tools/rider_campaign_runtime/cli.py
    from composition import CompositionError, create_composition_plan, write_catalog_artifacts
    from runtime import RuntimeError, build_campaign
    from runtime import MODULE_METADATA_PATH, SCAFFOLD_PATH, SLOT_MAP_PATH
    from scaffold import load_scaffold
    from schema import CampaignSpecError
    from grounded_images import GroundedImageError
    from slots import SlotError
    from agents import AgentError
    from assets import AssetPackageError


def main(argv=None):
    argv = list(argv or sys.argv[1:])
    if not argv or argv[0] not in {"build", "catalog", "plan"}:
        argv = ["build", *argv]
    parser = argparse.ArgumentParser(description="Build Rider campaign packages and composition approval artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build", help="Build a Rider campaign package from a validated JSON spec.")
    build_parser.add_argument("campaign_json", help="Path to the campaign JSON spec.")
    _add_scaffold_arguments(build_parser)
    catalog_parser = subparsers.add_parser("catalog", help="Generate the Rider module catalog and review artifacts.")
    catalog_parser.add_argument("--output", required=True, help="Directory for module_catalog.json and preview artifacts.")
    _add_scaffold_arguments(catalog_parser)
    plan_parser = subparsers.add_parser("plan", help="Create an approved composition plan from a selection JSON file.")
    plan_parser.add_argument("--selection", required=True, help="Path to an approved composition selection JSON file.")
    plan_parser.add_argument("--output", required=True, help="Path to write composition_plan.json.")
    _add_scaffold_arguments(plan_parser)
    args = parser.parse_args(argv)

    try:
        if args.command == "catalog":
            scaffold = _load_selected_scaffold(args)
            artifacts = write_catalog_artifacts(scaffold, Path(args.output))
            print(f"module catalog: {artifacts['catalog']}")
            print(f"review guide: {artifacts['review']}")
            print(f"module previews: {artifacts['preview_dir']}")
            print(f"hero configuration catalog: {artifacts['hero_configurations']}")
            print(f"hero selection gallery: {artifacts['hero_gallery']}")
            print(f"module gallery: {artifacts['module_gallery']}")
            if "sequence_gallery" in artifacts:
                print(f"sequence configuration catalog: {artifacts['sequence_configurations']}")
                print(f"sequence gallery: {artifacts['sequence_gallery']}")
            return 0
        if args.command == "plan":
            selection_path = Path(args.selection)
            selection = json.loads(selection_path.read_text(encoding="utf-8"))
            scaffold = _load_selected_scaffold(args)
            plan = create_composition_plan(scaffold, selection)
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"composition plan: {output_path}")
            print(f"selected modules: {len(plan['selected_module_codes'])}")
            print(f"required assets: {len(plan['required_assets'])}")
            return 0
        result = build_campaign(Path(args.campaign_json), scaffold=_load_selected_scaffold(args))
    except (
        RuntimeError,
        CampaignSpecError,
        SlotError,
        AgentError,
        AssetPackageError,
        CompositionError,
        GroundedImageError,
        ValueError,
    ) as err:
        print(f"rider campaign runtime error: {err}", file=sys.stderr)
        return 3

    failed = [check for check in result.qa.checks if not check["passed"]]
    print(f"package: {result.package_dir}")
    if result.qa.build:
        print(f"build mode: {result.qa.build['mode']} ({result.qa.build['variant_scope']})")
    print(f"html variants: {len(result.html_files)}")
    print(f"asset manifest: {result.asset_manifest}")
    print(f"qa report: {result.qa_report}")
    print(f"qa: {'passed' if result.qa.passed else 'blocked'} ({len(failed)} failing checks)")
    if result.zip_path:
        print(f"zip: {result.zip_path}")
        return 0
    for check in failed[:10]:
        print(f"blocking: {check['name']} - {check['message']}", file=sys.stderr)
    return 4


def _add_scaffold_arguments(parser):
    parser.add_argument("--scaffold", help="Optional staged scaffold HTML path.")
    parser.add_argument("--slot-map", help="Optional staged scaffold slot-map JSON path.")
    parser.add_argument("--metadata", help="Optional staged scaffold metadata JSON path.")


def _load_selected_scaffold(args):
    supplied = [args.scaffold, args.slot_map, args.metadata]
    if any(supplied) and not all(supplied):
        raise ValueError("--scaffold, --slot-map, and --metadata must be supplied together")
    if all(supplied):
        return load_scaffold(Path(args.scaffold), Path(args.slot_map), Path(args.metadata))
    return load_scaffold(SCAFFOLD_PATH, SLOT_MAP_PATH, MODULE_METADATA_PATH)


if __name__ == "__main__":
    raise SystemExit(main())
