#!/usr/bin/env python3
"""Authorize delegated Microsoft Graph Mail.Send and save a refresh token locally."""

from __future__ import annotations

import argparse
from pathlib import Path
import time
import webbrowser

from .auth import (
    DEFAULT_ENV_PATH,
    GraphAuthError,
    SCOPES,
    identity_url,
    load_env_file,
    post_form,
    require_value,
    update_env_file,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    env_path, env = load_env_file(args.env_file)
    tenant_id = require_value(env, "ONBRAND_GRAPH_TENANT_ID")
    client_id = require_value(env, "ONBRAND_GRAPH_CLIENT_ID")
    device = post_form(
        identity_url(tenant_id, "devicecode"),
        {"client_id": client_id, "scope": SCOPES},
    )
    verification_uri = device.get("verification_uri")
    device_code = device.get("device_code")
    if not verification_uri or not device_code:
        raise GraphAuthError("Device authorization response is incomplete")

    print(device.get("message") or f"Open {verification_uri} and enter code {device.get('user_code', '')}")
    if not args.no_browser:
        webbrowser.open(verification_uri)

    interval = max(int(device.get("interval", 5)), 1)
    expires_at = time.monotonic() + int(device.get("expires_in", 900))
    while time.monotonic() < expires_at:
        time.sleep(interval)
        response = post_form_allow_pending(
            identity_url(tenant_id, "token"),
            {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": client_id,
                "device_code": device_code,
            },
        )
        if response.get("error") == "authorization_pending":
            continue
        if response.get("error") == "slow_down":
            interval += 5
            continue
        if response.get("error"):
            raise GraphAuthError(response.get("error_description") or response["error"])
        refresh_token = response.get("refresh_token")
        if not refresh_token:
            raise GraphAuthError(
                "Authorization succeeded without a refresh token; confirm offline_access is permitted"
            )
        update_env_file(env_path, {"ONBRAND_GRAPH_REFRESH_TOKEN": refresh_token})
        print(f"Authorized delegated Mail.Send and saved the refresh token to {env_path}.")
        return
    raise GraphAuthError("Device authorization expired before sign-in completed")


def post_form_allow_pending(url: str, fields: dict[str, str]) -> dict:
    try:
        return post_form(url, fields)
    except GraphAuthError as error:
        message = str(error)
        if "authorization_pending" in message:
            return {"error": "authorization_pending"}
        if "slow_down" in message:
            return {"error": "slow_down"}
        raise


if __name__ == "__main__":
    main()

