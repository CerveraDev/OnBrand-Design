from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation import evaluate_split


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a completed Jev holdout receipt using the locked non-production policy.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("lexical_baseline", type=Path)
    parser.add_argument("policy", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = evaluate_split(
        _read(args.dataset),
        _read(args.receipt),
        _read(args.lexical_baseline),
        _read(args.policy),
        split="holdout",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decision": report["decision"], "case_count": report["case_count"], **report["metrics"], "production_effect": "none"}, indent=2))
    return 0


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
