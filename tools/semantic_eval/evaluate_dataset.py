from __future__ import annotations

import argparse
import json
from pathlib import Path

from .dataset import evaluate_lexical_baseline, load_dataset, review_markdown, validate_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 13 dataset and evaluate the Phase 10 baseline.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--review", type=Path)
    args = parser.parse_args()

    dataset = load_dataset(args.dataset)
    validation = validate_dataset(dataset)
    report = evaluate_lexical_baseline(dataset)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.review:
        args.review.parent.mkdir(parents=True, exist_ok=True)
        args.review.write_text(review_markdown(dataset), encoding="utf-8")
    print(json.dumps({"validation": validation, "baseline": {key: report[key] for key in ("matched", "case_count", "accuracy", "semantic_gap_case_ids")}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
