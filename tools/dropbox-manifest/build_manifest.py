#!/usr/bin/env python3
"""
Walk a Dropbox folder (recursively) and build one JSON manifest of every
image and PDF:

  {
    "filename": "project-south-elevation-dusk.jpg",
    "dropbox_id": "id:...",
    "dropbox_path": "/projects/project name/media/project-south-elevation-dusk.jpg",
    "category": [],
    "orientation": "landscape",
    "approved_for": [],
    "public_url": "https://..."
  }

`category` and `approved_for` are arrays left empty for you to fill in by hand.
Re-running the script synchronizes the manifest with Dropbox: new files are
added, deleted files are removed, and generated metadata is refreshed. The
existing values of `category` and `approved_for` are preserved exactly for
surviving files.

Setup:
  pip install dropbox pillow pymupdf

Configuration:
  By default, the script loads a .env file beside build_manifest.py. Use
  --env-file to select another file. Existing shell environment variables
  take precedence over values in the file.

Auth in .env (pick one):
  A) Short-lived token (quick test, expires in ~4 hours):
       DROPBOX_ACCESS_TOKEN=...
  B) Refresh token (recommended for repeated use):
       DROPBOX_APP_KEY=...
       DROPBOX_APP_SECRET=...
       DROPBOX_REFRESH_TOKEN=...

Dropbox app permissions (scopes) needed:
  files.metadata.read, files.content.read, sharing.read, sharing.write

Usage:
  python build_manifest.py
  python build_manifest.py --env-file /secure/path/project.env
  python build_manifest.py --root "/Projects/Project Name/Media" --out manifest.json
"""

import argparse
import io
import json
import os
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import dropbox
from dropbox.exceptions import ApiError
from dropbox.files import FileMetadata
from PIL import Image, ImageOps

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".heic", ".avif", ".bmp"}
PDF_EXTS = {".pdf"}
ALL_EXTS = IMAGE_EXTS | PDF_EXTS
MANUAL_FIELDS = ("category", "approved_for")
DEFAULT_ENV_PATH = Path(__file__).resolve().with_name(".env")


def load_env_file(path):
    """Load simple KEY=VALUE pairs without printing or overriding shell values."""
    path = Path(path).expanduser().resolve()
    if not path.exists():
        return path

    with path.open(encoding="utf-8") as f:
        for line_number, raw_line in enumerate(f, 1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].lstrip()
            if "=" not in line:
                raise ValueError(f"Invalid .env line {line_number} in {path}")

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key or not key.replace("_", "").isalnum():
                raise ValueError(f"Invalid .env key on line {line_number} in {path}")
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            elif " #" in value:
                value = value.split(" #", 1)[0].rstrip()
            os.environ.setdefault(key, value)
    return path


def configured_output_path(value, env_path):
    """Resolve relative manifest paths beside the selected .env file."""
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = env_path.parent / path
    return str(path.resolve())


def connect():
    token = os.environ.get("DROPBOX_ACCESS_TOKEN")
    if token:
        return dropbox.Dropbox(token)
    key = os.environ.get("DROPBOX_APP_KEY")
    secret = os.environ.get("DROPBOX_APP_SECRET")
    refresh = os.environ.get("DROPBOX_REFRESH_TOKEN")
    if key and secret and refresh:
        return dropbox.Dropbox(oauth2_refresh_token=refresh, app_key=key, app_secret=secret)
    sys.exit(
        "No Dropbox credentials found. Set DROPBOX_ACCESS_TOKEN, or "
        "DROPBOX_APP_KEY + DROPBOX_APP_SECRET + DROPBOX_REFRESH_TOKEN."
    )


def list_files(dbx, root):
    """Return every image/PDF FileMetadata under root, including nested folders."""
    entries = []
    result = dbx.files_list_folder(root, recursive=True, include_media_info=True)
    while True:
        for e in result.entries:
            if isinstance(e, FileMetadata) and os.path.splitext(e.name)[1].lower() in ALL_EXTS:
                entries.append(e)
        if not result.has_more:
            break
        result = dbx.files_list_folder_continue(result.cursor)
    return entries


def dimensions_from_listing(entry):
    """Use the dimensions Dropbox already computed, if present."""
    mi = getattr(entry, "media_info", None)
    if mi is not None and mi.is_metadata():
        dims = getattr(mi.get_metadata(), "dimensions", None)
        if dims:
            return dims.width, dims.height
    return None


def dimensions_from_download(dbx, entry):
    """Download the file and measure it (honors EXIF rotation for images)."""
    ext = os.path.splitext(entry.name)[1].lower()
    _, resp = dbx.files_download(entry.path_lower)

    if ext in PDF_EXTS:
        if fitz is None:
            raise RuntimeError("PyMuPDF not installed (pip install pymupdf)")
        doc = fitz.open(stream=resp.content, filetype="pdf")
        try:
            if doc.page_count == 0:
                raise RuntimeError("PDF has no pages")
            rect = doc[0].rect
            return rect.width, rect.height
        finally:
            doc.close()

    img = Image.open(io.BytesIO(resp.content))
    img = ImageOps.exif_transpose(img)
    return img.size


def orientation_of(width, height):
    if width > height:
        return "landscape"
    if height > width:
        return "portrait"
    return "square"


def to_direct_url(url):
    """Turn a Dropbox preview link into one that serves the file itself."""
    parts = urlparse(url)
    query = [(k, v) for k, v in parse_qsl(parts.query) if k not in ("dl", "raw")]
    query.append(("raw", "1"))
    return urlunparse(parts._replace(query=urlencode(query)))


def canonical_shared_url(url):
    """Normalize a shared URL to its stable token, ignoring mutable filenames."""
    if not url:
        return ""
    parts = urlparse(url)
    path_parts = [part for part in parts.path.split("/") if part]
    if len(path_parts) >= 3 and path_parts[:2] == ["scl", "fi"]:
        stable_path = f"/scl/fi/{path_parts[2]}"
    elif len(path_parts) >= 2 and path_parts[0] == "s":
        stable_path = f"/s/{path_parts[1]}"
    else:
        stable_path = parts.path
    query = [(k, v) for k, v in parse_qsl(parts.query) if k not in ("dl", "raw")]
    return urlunparse(parts._replace(path=stable_path, query=urlencode(query)))


def public_url_for(dbx, path):
    try:
        link = dbx.sharing_create_shared_link_with_settings(path)
        return to_direct_url(link.url)
    except ApiError as e:
        if e.error.is_shared_link_already_exists():
            links = dbx.sharing_list_shared_links(path=path, direct_only=True).links
            if links:
                return to_direct_url(links[0].url)
        print(f"  ! could not create shared link for {path}: {e}", file=sys.stderr)
        return ""


def load_existing(out_path):
    if not os.path.exists(out_path):
        return []
    with open(out_path, encoding="utf-8") as f:
        manifest = json.load(f)

    if not isinstance(manifest, list):
        raise ValueError(f"{out_path} must contain a JSON array")

    for index, item in enumerate(manifest):
        if not isinstance(item, dict):
            raise ValueError(f"Entry {index} in {out_path} must be a JSON object")
        if not item.get("filename"):
            raise ValueError(f"Entry {index} in {out_path} is missing filename")
        for field in MANUAL_FIELDS:
            if field in item and not isinstance(item[field], list):
                raise ValueError(
                    f"Entry {index} ({item['filename']}) has non-array {field}; "
                    "fix it manually so curated values are not changed implicitly"
                )
    return manifest


def unique_index(items, key_fn):
    """Index only unambiguous keys; duplicate keys are intentionally excluded."""
    keys = [key_fn(item) for item in items]
    counts = Counter(key for key in keys if key)
    return {
        key: item
        for key, item in zip(keys, items)
        if key and counts[key] == 1
    }


def build_existing_indexes(items):
    return {
        "dropbox_id": unique_index(items, lambda item: item.get("dropbox_id", "")),
        "dropbox_path": unique_index(items, lambda item: item.get("dropbox_path", "").lower()),
        "public_url": unique_index(
            items, lambda item: canonical_shared_url(item.get("public_url", ""))
        ),
        "filename": unique_index(items, lambda item: item.get("filename", "")),
    }


def find_existing(indexes, entry, public_url):
    """Find a prior record from strongest to weakest stable identity."""
    candidates = (
        ("dropbox_id", getattr(entry, "id", "")),
        ("dropbox_path", (getattr(entry, "path_lower", "") or "").lower()),
        ("public_url", canonical_shared_url(public_url)),
        ("filename", entry.name),
    )
    for index_name, key in candidates:
        if key and key in indexes[index_name]:
            return indexes[index_name][key]
    return None


def write_manifest(out_path, manifest):
    """Write atomically and keep the previous hand-curated manifest as a backup."""
    out_path = os.path.abspath(out_path)
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)

    if os.path.exists(out_path):
        shutil.copy2(out_path, f"{out_path}.bak")

    fd, temp_path = tempfile.mkstemp(prefix=".manifest-", suffix=".json", dir=out_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(temp_path, out_path)
    except Exception:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
        raise


def main():
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_PATH),
        help="Path to the local environment file (default: .env beside this script).",
    )
    preliminary, _ = pre_parser.parse_known_args()
    env_path = load_env_file(preliminary.env_file)

    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[pre_parser],
    )
    ap.add_argument(
        "--root",
        default=os.environ.get("DROPBOX_ROOT", ""),
        help='Dropbox folder path; defaults to DROPBOX_ROOT from .env.',
    )
    ap.add_argument(
        "--out",
        default=configured_output_path(
            os.environ.get("DROPBOX_MANIFEST_PATH", "manifest.json"), env_path
        ),
        help="Manifest output path; defaults to DROPBOX_MANIFEST_PATH from .env.",
    )
    ap.add_argument(
        "--measure-downloads",
        action="store_true",
        help="Always download each image to measure it instead of trusting Dropbox's listing (slower, most accurate).",
    )
    args = ap.parse_args()

    if not args.root:
        ap.error("Dropbox root is required; set DROPBOX_ROOT in .env or pass --root")

    root = args.root.rstrip("/")
    if root == "/":
        root = ""

    dbx = connect()
    existing = load_existing(args.out)
    existing_indexes = build_existing_indexes(existing)
    existing_filename_counts = Counter(item["filename"] for item in existing)

    print(f"Listing {args.root or '/'} ...")
    entries = sorted(list_files(dbx, root), key=lambda e: e.path_lower)
    print(f"Found {len(entries)} files (images + PDFs).")

    seen = {}
    matched_existing = set()
    manifest = []
    for i, e in enumerate(entries, 1):
        print(f"[{i}/{len(entries)}] {e.path_display}")

        if e.name in seen:
            print(f"  ! duplicate filename '{e.name}' also at {seen[e.name]}", file=sys.stderr)
        seen[e.name] = e.path_display

        dims = None if args.measure_downloads else dimensions_from_listing(e)
        if dims is None:
            try:
                dims = dimensions_from_download(dbx, e)
            except Exception as err:  # unreadable/unsupported format
                print(f"  ! could not measure {e.name}: {err}", file=sys.stderr)

        public_url = public_url_for(dbx, e.path_lower)
        prev = find_existing(existing_indexes, e, public_url)
        if prev is None and existing_filename_counts[e.name] > 1:
            raise RuntimeError(
                f"Could not safely match duplicate filename '{e.name}' at {e.path_display}. "
                "The manifest was not changed. Restore access to its existing shared link "
                "or add dropbox_id/dropbox_path before retrying."
            )
        if prev is not None:
            matched_existing.add(id(prev))

        manifest.append(
            {
                "filename": e.name,
                "dropbox_id": getattr(e, "id", ""),
                "dropbox_path": e.path_lower,
                "category": prev.get("category", []) if prev is not None else [],
                "orientation": orientation_of(*dims) if dims else "",
                "approved_for": prev.get("approved_for", []) if prev is not None else [],
                "public_url": public_url,
            }
        )

    added = len(manifest) - len(matched_existing)
    removed = len(existing) - len(matched_existing)
    write_manifest(args.out, manifest)
    print(
        f"Wrote {len(manifest)} entries to {args.out} "
        f"({added} added, {removed} removed, {len(matched_existing)} preserved)."
    )
    if existing:
        print(f"Previous manifest backed up to {os.path.abspath(args.out)}.bak")


if __name__ == "__main__":
    main()
