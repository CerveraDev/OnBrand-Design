"""Command-line entry point.

python3 -m tools.social_runtime.cli build --spec <path>
python3 -m tools.social_runtime.cli frames --project <slug>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .frames import FRAMES_FILE, build_frame_definitions
from .runtime import ROOT, SocialRuntimeError, build_social
from .schema import SocialSpecError


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build an OnBrand social post or carousel package.")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Validate a social spec and build its package.")
    build.add_argument("--spec", required=True, help="Path to the canonical social spec JSON.")
    frames = commands.add_parser("frames", help="Regenerate frame definitions from a project's scaffold catalog.")
    frames.add_argument("--project", required=True, help="Project slug under projects/.")
    args = parser.parse_args(argv)
    if args.command == "frames":
        return _write_frames(ROOT / "projects" / args.project)
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


def _write_frames(project_dir: Path) -> int:
    try:
        catalog = json.loads((project_dir / "social" / "scaffold" / "frame-catalog.json").read_text(encoding="utf-8"))
        project = json.loads((project_dir / "project.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        print(f"frame generation refused: {err}", file=sys.stderr)
        return 2
    definitions = build_frame_definitions(catalog, logo_label=f"{project['project_name']} logo")
    path = project_dir / "social" / "templates" / FRAMES_FILE
    path.write_text(json.dumps(definitions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(definitions['frames'])} frame definitions written to {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
