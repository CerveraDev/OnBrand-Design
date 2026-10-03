#!/usr/bin/env python3
"""Create an OnBrand Design project pack for use with the shared core."""

import argparse
import json
import os
import re
import shutil
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = REPO_ROOT / "templates" / "project-starter"
PROJECTS_ROOT = REPO_ROOT / "projects"
REGISTRY_PATH = PROJECTS_ROOT / "registry.json"
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".txt"}


def valid_slug(value):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise argparse.ArgumentTypeError(
            "slug must contain lowercase letters, digits, and single hyphens"
        )
    if len(f"onbrand-{value}-email") > 64:
        raise argparse.ArgumentTypeError("slug produces a skill ID longer than 64 characters")
    return value


def render_tree(source, destination, replacements):
    for source_path in source.rglob("*"):
        relative = source_path.relative_to(source)
        if source_path.is_dir():
            continue

        if relative.parts[0] == "email":
            relative = Path(
                "skills",
                f"onbrand-{replacements['__PROJECT_SLUG__']}-email",
                *relative.parts[1:],
            )
        elif relative.parts[0] == "image":
            relative = Path(
                "skills",
                f"onbrand-{replacements['__PROJECT_SLUG__']}-image",
                *relative.parts[1:],
            )

        target_path = destination / relative
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if source_path.suffix.lower() in TEXT_SUFFIXES:
            text = source_path.read_text(encoding="utf-8")
            for key, value in replacements.items():
                text = text.replace(key, value)
            target_path.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(source_path, target_path)


def write_json_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(temp_path, path)
    except Exception:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
        raise


def register_project(name, slug, status):
    with REGISTRY_PATH.open(encoding="utf-8") as f:
        registry = json.load(f)
    if any(item["slug"] == slug for item in registry["projects"]):
        raise ValueError(f"project '{slug}' is already registered")
    registry["projects"].append(
        {
            "name": name,
            "slug": slug,
            "status": status,
            "path": f"projects/{slug}",
        }
    )
    registry["projects"].sort(key=lambda item: item["slug"])
    write_json_atomic(REGISTRY_PATH, registry)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Public project name")
    parser.add_argument("--slug", required=True, type=valid_slug)
    parser.add_argument("--owner", default="Cervera Real Estate, Inc.")
    parser.add_argument("--author", default="Felix Mendoza")
    parser.add_argument("--status", default="scaffold")
    args = parser.parse_args()

    destination = PROJECTS_ROOT / args.slug
    if destination.exists():
        parser.error(f"destination already exists: {destination}")
    if not TEMPLATE_ROOT.is_dir():
        parser.error(f"starter template is missing: {TEMPLATE_ROOT}")

    replacements = {
        "__PROJECT_NAME__": args.name,
        "__PROJECT_SLUG__": args.slug,
        "__OWNER__": args.owner,
        "__AUTHOR__": args.author,
    }

    try:
        render_tree(TEMPLATE_ROOT, destination, replacements)
        project = {
            "schema_version": 1,
            "framework": "OnBrand Design",
            "project_name": args.name,
            "project_slug": args.slug,
            "owner": args.owner,
            "author": args.author,
            "license": "Apache-2.0",
            "status": args.status,
            "skills": {
                "email": f"onbrand-{args.slug}-email",
                "image": f"onbrand-{args.slug}-image",
            },
            "brand_calibration": "pending_project_materials",
            "footer_calibration": "pending_locked_partials",
            "asset_manifest": "pending_configuration",
        }
        write_json_atomic(destination / "project.json", project)
        register_project(args.name, args.slug, args.status)
    except Exception:
        if destination.exists():
            shutil.rmtree(destination)
        raise

    print(f"Created OnBrand Design project: {destination}")


if __name__ == "__main__":
    main()
