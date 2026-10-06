#!/usr/bin/env python3
"""Validate and explicitly send an RFC 822 message through Microsoft Graph MIME send."""

from __future__ import annotations

import argparse
import base64
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses
import hashlib
import json
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .auth import DEFAULT_ENV_PATH, load_env_file, refresh_access_token, require_value


GRAPH_SEND_URL = "https://graph.microsoft.com/v1.0/me/sendMail"


def prepare_mime_bytes(raw: bytes) -> bytes:
    return re.sub(br"(?im)^X-Unsent:[^\r\n]*(?:\r?\n)", b"", raw, count=1)


def inspect_message(raw: bytes) -> dict:
    message = BytesParser(policy=policy.default).parsebytes(raw)
    sender = getaddresses([message.get("From", "")])
    recipients = getaddresses(message.get_all("To", []))
    if len(sender) != 1 or not sender[0][1]:
        raise ValueError("MIME message must contain exactly one From address")
    if not recipients or any(not address for _, address in recipients):
        raise ValueError("MIME message must contain at least one valid To address")
    html_part = message.get_body(preferencelist=("html",))
    html = html_part.get_content() if html_part else ""
    return {
        "from": sender[0][1].lower(),
        "to": [address.lower() for _, address in recipients],
        "subject": message.get("Subject", ""),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "html_present": bool(html_part),
        "bulletproof_backgrounds": html.count('data-onbrand-background="true"'),
        "background_cid_present": bool(
            re.search(r'(?:background=["\']cid:|<v:fill\b[^>]*\bsrc=["\']cid:)', html, re.IGNORECASE)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", required=True, type=Path)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--execute-live", action="store_true")
    parser.add_argument("--confirm-send", action="store_true")
    args = parser.parse_args()

    source = args.message.expanduser().resolve()
    if not source.is_file():
        parser.error(f"message not found: {source}")
    prepared = prepare_mime_bytes(source.read_bytes())
    details = inspect_message(prepared)
    env_path, env = load_env_file(args.env_file)
    expected_sender = require_value(env, "ONBRAND_GRAPH_SENDER").lower()
    if details["from"] != expected_sender:
        parser.error(
            f"MIME From address {details['from']} does not match ONBRAND_GRAPH_SENDER {expected_sender}"
        )
    if not details["html_present"]:
        parser.error("message does not contain an HTML body")
    if details["background_cid_present"]:
        parser.error("message contains a CID-backed CSS or VML background")

    receipt_path = args.receipt or source.with_suffix(".graph-send.json")
    receipt = {
        **details,
        "transport": "Microsoft Graph v1.0 delegated MIME send",
        "endpoint": GRAPH_SEND_URL,
        "status": "validated-not-sent",
    }
    if args.execute_live != args.confirm_send:
        parser.error("live delivery requires both --execute-live and --confirm-send")
    if args.execute_live:
        access_token = refresh_access_token(env_path, env)
        request = Request(
            GRAPH_SEND_URL,
            data=base64.b64encode(prepared),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "text/plain",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=60) as response:
                status = response.status
        except HTTPError as error:
            payload = error.read().decode("utf-8", errors="replace")
            raise SystemExit(f"Microsoft Graph send failed ({error.code}): {payload}") from error
        if status != 202:
            raise SystemExit(f"Microsoft Graph send returned unexpected HTTP status {status}")
        receipt["status"] = "accepted"
        receipt["http_status"] = status
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"{receipt['status']}: {receipt_path}")


if __name__ == "__main__":
    main()

