from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adjudication import freeze_dataset, validate_adjudication
from .dataset import load_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 13 adjudication and freeze an reviewed dataset.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("reviewer_a", type=Path)
    parser.add_argument("reviewer_b", type=Path)
    parser.add_argument("adjudication", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    dataset = load_dataset(args.dataset)
    left = _read_json(args.reviewer_a)
    right = _read_json(args.reviewer_b)
    adjudication = _read_json(args.adjudication)
    summary = validate_adjudication(dataset, left, right, adjudication)
    if args.output:
        frozen = freeze_dataset(dataset, left, right, adjudication)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(frozen, indent=2) + "\n", encoding="utf-8")
        summary["output"] = str(args.output)
    print(json.dumps(summary, indent=2))
    return 0


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
