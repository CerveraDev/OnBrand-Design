"""Command-line entry point.

python3 -m tools.social_runtime.cli build --spec <path>
python3 -m tools.social_runtime.cli frames --project <slug>
python3 -m tools.social_runtime.cli render --package <directory>
python3 -m tools.social_runtime.cli gallery --project <slug>
python3 -m tools.social_runtime.cli images --project <slug>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import webbrowser

from .catalog import CatalogError, write_catalog
from .frames import FRAMES_FILE, build_frame_definitions
from .gallery import GalleryError, write_gallery
from .render import RenderError, render_package
from .runtime import ROOT, SocialRuntimeError, build_social
from .schema import SocialSpecError


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build an OnBrand social post or carousel package.")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Validate a social spec and build its package.")
    build.add_argument("--spec", required=True, help="Path to the canonical social spec JSON.")
    frames = commands.add_parser("frames", help="Regenerate frame definitions from a project's scaffold catalog.")
    frames.add_argument("--project", required=True, help="Project slug under projects/.")
    render = commands.add_parser("render", help="Render a built package's slides from the project scaffold.")
    render.add_argument("--package", required=True, help="Path to a built social package directory.")
    gallery = commands.add_parser("gallery", help="Write a project's layout gallery and open it in the browser.")
    gallery.add_argument("--project", required=True, help="Project slug under projects/.")
    gallery.add_argument("--no-open", action="store_true", help="Write the gallery without opening it.")
    images = commands.add_parser("images", help="Write a project's image catalog page and open it in the browser.")
    images.add_argument("--project", required=True, help="Project slug under projects/.")
    images.add_argument("--no-open", action="store_true", help="Write the page without opening it.")
    args = parser.parse_args(argv)
    if args.command == "images":
        return _images(ROOT / "projects" / args.project, show=not args.no_open)
    if args.command == "gallery":
        return _gallery(ROOT / "projects" / args.project, show=not args.no_open)
    if args.command == "frames":
        return _write_frames(ROOT / "projects" / args.project)
    if args.command == "render":
        return _render(args.package)
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


def _render(package: str) -> int:
    try:
        result = render_package(package)
    except RenderError as err:
        print(f"social render refused: {err}", file=sys.stderr)
        return 2
    json.dump(
        {
            "passed": result.passed,
            "slides": [str(path) for path in result.slides],
            "zip_path": str(result.zip_path) if result.zip_path else None,
            "render_report": str(result.report),
            "simulator": str(result.simulator) if result.simulator else None,
            "warnings": result.warnings,
            "failed_checks": [f"{c['name']}: {c['message']}" for c in result.checks if not c["passed"]],
        },
        sys.stdout, indent=2,
    )
    sys.stdout.write("\n")
    return 0 if result.passed else 1


def _gallery(project_dir: Path, *, show: bool) -> int:
    try:
        path = write_gallery(project_dir)
    except GalleryError as err:
        print(f"layout gallery refused: {err}", file=sys.stderr)
        return 2
    if show:
        webbrowser.open(path.resolve().as_uri())
    print(f"Layout gallery written to {path.relative_to(ROOT)}" + (" and opened in the browser" if show else ""))
    return 0


def _images(project_dir: Path, *, show: bool) -> int:
    try:
        result = write_catalog(project_dir)
    except CatalogError as err:
        print(f"image catalog refused: {err}", file=sys.stderr)
        return 2
    if show:
        webbrowser.open(result.path.resolve().as_uri())
    print(f"Image catalog with {result.images} images written to {result.path.relative_to(ROOT)}"
          + (" and opened in the browser" if show else ""))
    if result.without_preview:
        print(f"{len(result.without_preview)} image(s) have no preview yet; run the command again to retry: "
              + ", ".join(result.without_preview), file=sys.stderr)
    return 0


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
