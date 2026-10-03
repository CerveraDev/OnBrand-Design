#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from .runtime import RuntimeError, build_campaign
    from .schema import CampaignSpecError
    from .slots import SlotError
    from .agents import AgentError
    from .assets import AssetPackageError
except ImportError:  # Allow direct execution: python3 tools/rider_campaign_runtime/cli.py
    from runtime import RuntimeError, build_campaign
    from schema import CampaignSpecError
    from slots import SlotError
    from agents import AgentError
    from assets import AssetPackageError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a Rider campaign package from a validated JSON spec.")
    parser.add_argument("campaign_json", help="Path to the campaign JSON spec.")
    args = parser.parse_args(argv)
    try:
        result = build_campaign(Path(args.campaign_json))
    except (RuntimeError, CampaignSpecError, SlotError, AgentError, AssetPackageError, ValueError) as err:
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


if __name__ == "__main__":
    raise SystemExit(main())
