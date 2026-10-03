from __future__ import annotations

import argparse
import json
from pathlib import Path

from .dataset import load_dataset
from .jev_pilot import build_request_batch, validate_question_set


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a no-network Jev pilot request batch from the frozen dataset.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("question_set", type=Path)
    parser.add_argument("--split", choices=("calibration", "holdout"), default="calibration")
    parser.add_argument("--allow-holdout", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    dataset = load_dataset(args.dataset)
    question_set = json.loads(args.question_set.read_text(encoding="utf-8"))
    validate_question_set(question_set)
    batch = build_request_batch(dataset, question_set, split=args.split, allow_holdout=args.allow_holdout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: batch[key] for key in ("question_set_id", "split", "record_count", "production_effect")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
