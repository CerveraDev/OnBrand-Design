"""Command-line entry point: python3 -m tools.social_runtime.cli build --spec <path>"""

from __future__ import annotations

import argparse
import json
import sys

from .runtime import SocialRuntimeError, build_social
from .schema import SocialSpecError


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build an OnBrand social post or carousel package.")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Validate a social spec and build its package.")
    build.add_argument("--spec", required=True, help="Path to the canonical social spec JSON.")
    args = parser.parse_args(argv)
    try:
        result = build_social(args.spec)
    except (SocialSpecError, SocialRuntimeError, OSError, json.JSONDecodeError) as err:
        print(f"social build refused: {err}", file=sys.stderr)
        return 2
    json.dump(
        {
            "passed": result.qa.passed,
            "package_dir": str(result.package_dir),
            "zip_path": str(result.zip_path) if result.zip_path else None,
            "qa_report": str(result.qa_report),
            "warnings": result.qa.warnings,
            "failed_checks": [c["name"] for c in result.qa.checks if not c["passed"]],
        },
        sys.stdout, indent=2,
    )
    sys.stdout.write("\n")
    return 0 if result.qa.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
