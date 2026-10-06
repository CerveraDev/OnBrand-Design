#!/usr/bin/env python3
"""Build a self-contained RFC 822 test message from a packaged email."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
from email.message import EmailMessage
from email.policy import SMTP
from pathlib import Path


IMAGE_REFERENCE = re.compile(r"\.\./images/([A-Za-z0-9._-]+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--from-address", required=True)
    parser.add_argument("--to-address", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    html_path = args.html.resolve()
    package_root = html_path.parent.parent
    images_dir = package_root / "images"
    html = html_path.read_text(encoding="utf-8")

    referenced_names = sorted(set(IMAGE_REFERENCE.findall(html)))
    missing = [name for name in referenced_names if not (images_dir / name).is_file()]
    if missing:
        raise SystemExit(f"Missing packaged image(s): {', '.join(missing)}")

    cid_by_name = {
        name: f"onbrand-{hashlib.sha256(name.encode()).hexdigest()[:16]}"
        for name in referenced_names
    }
    for name, cid in cid_by_name.items():
        html = html.replace(f"../images/{name}", f"cid:{cid}")

    message = EmailMessage(policy=SMTP)
    message["From"] = args.from_address
    message["To"] = args.to_address
    message["Subject"] = args.subject
    message["X-Unsent"] = "1"
    message.set_content(
        "This message contains an HTML email compatibility test. "
        "Open it in an HTML-capable mail client."
    )
    message.add_alternative(html, subtype="html")
    html_part = message.get_payload()[-1]

    embedded = []
    for name in referenced_names:
        image_path = images_dir / name
        mime_type, _ = mimetypes.guess_type(name)
        if not mime_type or not mime_type.startswith("image/"):
            raise SystemExit(f"Unsupported image MIME type: {name}")
        maintype, subtype = mime_type.split("/", 1)
        data = image_path.read_bytes()
        html_part.add_related(
            data,
            maintype=maintype,
            subtype=subtype,
            cid=f"<{cid_by_name[name]}>",
            filename=name,
            disposition="inline",
        )
        embedded.append(
            {
                "filename": name,
                "cid": cid_by_name[name],
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(message.as_bytes())
    receipt = {
        "source_html": args.html.as_posix(),
        "from": args.from_address,
        "to": args.to_address,
        "subject": args.subject,
        "transport": "multipart/alternative with HTML multipart/related CID images",
        "html_structure_changed": False,
        "transport_reference_change": "../images/<name> -> cid:<content-id>",
        "embedded_images": embedded,
        "eml_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }
    args.output.with_suffix(".json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
