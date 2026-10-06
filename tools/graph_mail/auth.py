from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_ENV_PATH = Path(__file__).resolve().with_name(".env")
SCOPES = "offline_access https://graph.microsoft.com/Mail.Send"


class GraphAuthError(RuntimeError):
    """Raised when Microsoft identity authorization or token refresh fails."""


def load_env_file(path: Path) -> tuple[Path, dict[str, str]]:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(
            f"Configuration not found: {path}. Copy .env.example to .env first."
        )
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
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


def require_value(values: dict[str, str], name: str) -> str:
    value = values.get(name, "").strip()
    if not value:
        raise ValueError(f"{name} is missing from the selected .env file")
    return value


def update_env_file(path: Path, values: dict[str, str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    found = {key: 0 for key in values}
    updated: list[str] = []
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
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write("\n".join(updated) + "\n")
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def identity_url(tenant_id: str, endpoint: str) -> str:
    return f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/{endpoint}"


def post_form(url: str, fields: dict[str, str]) -> dict:
    request = Request(
        url,
        data=urlencode(fields).encode("ascii"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        payload = error.read().decode("utf-8", errors="replace")
        try:
            details = json.loads(payload)
            error_name = details.get("error", "")
            description = details.get("error_description", "")
            message = ": ".join(item for item in (error_name, description) if item) or payload
        except json.JSONDecodeError:
            message = payload
        raise GraphAuthError(f"Microsoft identity request failed ({error.code}): {message}") from error


def refresh_access_token(env_path: Path, env: dict[str, str]) -> str:
    tenant_id = require_value(env, "ONBRAND_GRAPH_TENANT_ID")
    client_id = require_value(env, "ONBRAND_GRAPH_CLIENT_ID")
    refresh_token = require_value(env, "ONBRAND_GRAPH_REFRESH_TOKEN")
    response = post_form(
        identity_url(tenant_id, "token"),
        {
            "client_id": client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": SCOPES,
        },
    )
    access_token = response.get("access_token", "")
    if not access_token:
        raise GraphAuthError("Microsoft identity response did not include an access token")
    rotated_refresh = response.get("refresh_token")
    if rotated_refresh and rotated_refresh != refresh_token:
        update_env_file(env_path, {"ONBRAND_GRAPH_REFRESH_TOKEN": rotated_refresh})
    return access_token
