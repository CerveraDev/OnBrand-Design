from __future__ import annotations

from dataclasses import dataclass
from html import escape, unescape
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from .slots import UsedAsset


class AssetPackageError(ValueError):
    """Raised when campaign assets cannot be safely packaged."""


IMAGE_URL_RE = re.compile(r"url\(['\"]?([^'\"\)]+)['\"]?\)")


@dataclass(frozen=True)
class PackagedAsset:
    source: str
    package_path: str
    sha256: str
    size_bytes: int
    role: str
    variants: tuple[str, ...]
    identity: str = ""
    filename: str = ""
    dropbox_path: str = ""
    image_workflow_id: str = ""


def rewrite_and_package_assets(
    html_by_variant: dict[str, str],
    asset_hints: list[tuple[str, UsedAsset]],
    package_dir: Path,
    *,
    asset_mode: str,
    hosted_asset_base_url: str | None,
) -> tuple[dict[str, str], list[PackagedAsset]]:
    source_usage: dict[str, set[str]] = {}
    roles: dict[str, set[str]] = {}
    identities: dict[str, UsedAsset] = {}
    for variant, html in html_by_variant.items():
        for source in extract_image_refs(html):
            source_usage.setdefault(source, set()).add(variant)
            roles.setdefault(source, set()).add(_role_from_source(source))
    for variant, hint in asset_hints:
        source_usage.setdefault(hint.source, set()).add(variant)
        roles.setdefault(hint.source, set()).add(hint.role)
        if hint.identity or hint.filename or hint.dropbox_path or hint.image_workflow_id:
            identities[hint.source] = hint

    images_dir = package_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    source_to_ref = {}
    packaged = []
    for source in sorted(source_usage):
        data, original_name = _read_asset(source)
        digest = hashlib.sha256(data).hexdigest()
        filename = _deterministic_name(source, original_name, digest)
        local_path = images_dir / filename
        local_path.write_bytes(data)
        if hashlib.sha256(local_path.read_bytes()).hexdigest() != digest:
            raise AssetPackageError(f"Checksum verification failed for {source}")
        package_ref = f"../images/{filename}"
        if asset_mode == "hosted-deployment":
            package_ref = hosted_asset_base_url.rstrip("/") + "/" + filename
        source_to_ref[source] = package_ref
        hint = identities.get(source)
        packaged.append(
            PackagedAsset(
                source=source,
                package_path=f"images/{filename}",
                sha256=digest,
                size_bytes=len(data),
                role=", ".join(sorted(roles[source])),
                variants=tuple(sorted(source_usage[source])),
                identity=hint.identity if hint else "",
                filename=hint.filename if hint else original_name,
                dropbox_path=hint.dropbox_path if hint else "",
                image_workflow_id=hint.image_workflow_id if hint else "",
            )
        )

    rewritten = {}
    for variant, html in html_by_variant.items():
        for source, ref in source_to_ref.items():
            html = html.replace(escape(source, quote=True), ref)
            html = html.replace(source, ref)
        rewritten[variant] = html
    return rewritten, packaged


def write_asset_manifest(
    package_dir: Path,
    campaign: dict,
    packaged: list[PackagedAsset],
    *,
    asset_mode: str,
    image_workflow_metadata: dict | None = None,
) -> Path:
    manifest = {
        "campaign": {
            "slug": campaign["slug"],
            "title": campaign["title"],
        },
        "asset_mode": asset_mode,
        "image_workflow": image_workflow_metadata or {},
        "assets": [
            {
                "source": asset.source,
                "identity": asset.identity,
                "dropbox_path": asset.dropbox_path,
                "original_filename": asset.filename,
                "package_path": asset.package_path,
                "sha256": asset.sha256,
                "size_bytes": asset.size_bytes,
                "role": asset.role,
                "variants": list(asset.variants),
                **({"image_workflow_id": asset.image_workflow_id} if asset.image_workflow_id else {}),
            }
            for asset in packaged
        ],
    }
    path = package_dir / "asset-manifest.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def package_documents(documents: list[UsedAsset], package_dir: Path) -> list[PackagedAsset]:
    if not documents:
        return []
    documents_dir = package_dir / "documents"
    documents_dir.mkdir(parents=True, exist_ok=True)
    packaged: list[PackagedAsset] = []
    seen_sources: set[str] = set()
    for document in documents:
        if document.source in seen_sources:
            continue
        seen_sources.add(document.source)
        data, original_name = _read_asset(document.source)
        if not data.startswith(b"%PDF"):
            raise AssetPackageError(f"Document is not a valid PDF payload: {document.source}")
        digest = hashlib.sha256(data).hexdigest()
        filename = _deterministic_name(document.source, original_name, digest)
        if Path(filename).suffix.lower() != ".pdf":
            raise AssetPackageError(f"Document filename is not PDF: {original_name}")
        local_path = documents_dir / filename
        local_path.write_bytes(data)
        if hashlib.sha256(local_path.read_bytes()).hexdigest() != digest:
            raise AssetPackageError(f"Checksum verification failed for {document.source}")
        packaged.append(
            PackagedAsset(
                source=document.source,
                package_path=f"documents/{filename}",
                sha256=digest,
                size_bytes=len(data),
                role=document.role,
                variants=(),
                identity=document.identity,
                filename=document.filename or original_name,
                dropbox_path=document.dropbox_path,
            )
        )
    return packaged


def extract_image_refs(html: str) -> set[str]:
    parser = _ImageRefParser()
    parser.feed(html)
    refs = set(parser.refs)
    refs.update(unescape(match.group(1)) for match in IMAGE_URL_RE.finditer(html))
    return {ref for ref in refs if _is_packaged_image_ref(ref)}


def create_zip(package_dir: Path) -> Path:
    zip_base = package_dir.with_suffix("")
    zip_path = shutil.make_archive(str(zip_base), "zip", root_dir=package_dir.parent, base_dir=package_dir.name)
    return Path(zip_path)


def _read_asset(source: str) -> tuple[bytes, str]:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        request = Request(source, headers={"User-Agent": "OnBrand-Rider-Runtime/1.0"})
        with urlopen(request, timeout=30) as response:
            data = response.read()
        if not data:
            raise AssetPackageError(f"Downloaded empty asset: {source}")
        return data, Path(unquote(parsed.path)).name or "asset"
    if parsed.scheme == "file":
        path = Path(unquote(parsed.path))
    elif not parsed.scheme:
        path = Path(source)
    else:
        raise AssetPackageError(f"Unsupported asset scheme: {parsed.scheme}")
    if not path.is_file():
        raise AssetPackageError(f"Asset file not found: {path}")
    return path.read_bytes(), path.name


def _deterministic_name(source: str, original_name: str, digest: str) -> str:
    suffix = Path(original_name).suffix.lower() or ".bin"
    stem = re.sub(r"[^a-zA-Z0-9]+", "-", Path(original_name).stem).strip("-").lower() or "asset"
    return f"{stem}-{digest[:12]}{suffix}"


def _role_from_source(source: str) -> str:
    lower = source.lower()
    if "logo" in lower:
        return "logo"
    if "headshot" in lower or "jake-lecce-hero" in lower or "generic-headshot" in lower:
        return "footer-headshot"
    if "hero" in lower:
        return "hero"
    return "module-image"


def _is_packaged_image_ref(ref: str) -> bool:
    parsed = urlparse(ref)
    if parsed.scheme in {"mailto", "tel"}:
        return False
    if parsed.scheme in {"http", "https", "file"}:
        return True
    return ref.startswith("../images/") or ref.startswith("images/") or ref.startswith("/")


class _ImageRefParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "img":
            return
        values = dict(attrs)
        src = values.get("src")
        if src:
            self.refs.append(src)
