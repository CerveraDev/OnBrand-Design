#!/usr/bin/env python3
"""Authorize Dropbox offline access and store a verified refresh token locally."""

import argparse
import getpass
import os
import tempfile
import webbrowser
from pathlib import Path

import dropbox
from dropbox.oauth import DropboxOAuth2FlowNoRedirect


DEFAULT_ENV_PATH = Path(__file__).resolve().with_name(".env")


def load_env_file(path):
    """Load simple KEY=VALUE pairs without printing secrets."""
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(
            f"Configuration not found: {path}. Copy .env.example to .env first."
        )

    values = {}
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
            values[key] = value
    return path, values


def update_env_file(path, values):
    """Atomically replace selected fields while preserving all other lines."""
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    found = {key: 0 for key in values}
    updated = []

    for line in lines:
        stripped = line.lstrip()
        prefix = "export " if stripped.startswith("export ") else ""
        candidate = stripped[7:].lstrip() if prefix else stripped
        key = candidate.split("=", 1)[0].strip() if "=" in candidate else ""
        if key in values:
            found[key] += 1
            if found[key] > 1:
                raise ValueError(f"Duplicate {key} entries in {path}")
            updated.append(f"{prefix}{key}={values[key]}")
        else:
            updated.append(line)

    for key, value in values.items():
        if not found[key]:
            updated.append(f"{key}={value}")

    content = "\n".join(updated) + "\n"
    fd, temp_path = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(temp_path, path)
    except Exception:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
        raise


def require_value(values, name):
    value = values.get(name, "").strip()
    if not value:
        raise ValueError(f"{name} is missing from the selected .env file")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env-file",
        default=DEFAULT_ENV_PATH,
        type=Path,
        help="Local credential file (default: tools/dropbox-manifest/.env)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the authorization URL without opening a browser",
    )
    args = parser.parse_args()

    env_path, env = load_env_file(args.env_file)
    app_key = require_value(env, "DROPBOX_APP_KEY")
    app_secret = require_value(env, "DROPBOX_APP_SECRET")

    flow = DropboxOAuth2FlowNoRedirect(
        app_key,
        consumer_secret=app_secret,
        token_access_type="offline",
    )
    authorize_url = flow.start()

    print("Open this Dropbox authorization URL and approve the app:")
    print(authorize_url)
    if not args.no_browser:
        webbrowser.open(authorize_url)

    authorization_code = getpass.getpass(
        "Paste the one-time authorization code (input hidden): "
    ).strip()
    if not authorization_code:
        parser.error("authorization code cannot be empty")

    result = flow.finish(authorization_code)
    refresh_token = result.refresh_token
    if not refresh_token:
        raise RuntimeError(
            "Dropbox did not return a refresh token. Confirm offline access was approved."
        )

    client = dropbox.Dropbox(
        oauth2_refresh_token=refresh_token,
        app_key=app_key,
        app_secret=app_secret,
    )
    client.files_list_folder("", limit=1)

    update_env_file(
        env_path,
        {
            "DROPBOX_REFRESH_TOKEN": refresh_token,
            "DROPBOX_ACCESS_TOKEN": "",
        },
    )
    print(f"Verified Dropbox access and saved the refresh token to {env_path}.")
    print("The short-lived DROPBOX_ACCESS_TOKEN field was cleared.")


if __name__ == "__main__":
    main()
