from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

from .provider import run_provider_batch


DEFAULT_ENV_PATH = Path(__file__).resolve().with_name(".env")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or safely skip the optional TypeSafe Jev calibration batch.")
    parser.add_argument("batch", type=Path)
    parser.add_argument("question_set", type=Path)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument("--execute-live", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    _load_env(args.env_file)
    enabled = os.environ.get("ONBRAND_JEV_ENABLED", "false").strip().lower() == "true"
    receipt = run_provider_batch(
        _read_json(args.batch),
        _read_json(args.question_set),
        enabled=enabled,
        live_authorized=args.execute_live,
        api_key=os.environ.get("TYPESAFE_API_KEY"),
        transport=_http_transport,
        executed_at=datetime.now(timezone.utc).isoformat(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "record_count": len(receipt["records"]), "production_effect": "none"}, indent=2))
    return 0


def _http_transport(endpoint: str, headers: dict[str, str], payload: dict, timeout: float) -> dict:
    request = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"TypeSafe HTTP {exc.code}") from exc


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid .env line {line_number} in {path}")
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid .env key on line {line_number} in {path}")
        os.environ.setdefault(key, value.strip())


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
