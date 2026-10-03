from __future__ import annotations

import argparse
import json
from pathlib import Path

from .dataset import load_dataset
from .reviews import compare_reviews, create_review_template, validate_review


def main() -> int:
    parser = argparse.ArgumentParser(description="Create, validate, or compare blinded Phase 13 dataset reviews.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    template = subparsers.add_parser("template")
    template.add_argument("dataset", type=Path)
    template.add_argument("--reviewer-id", required=True)
    template.add_argument("--output", type=Path, required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("dataset", type=Path)
    validate.add_argument("review", type=Path)

    compare = subparsers.add_parser("compare")
    compare.add_argument("dataset", type=Path)
    compare.add_argument("left", type=Path)
    compare.add_argument("right", type=Path)
    compare.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    dataset = load_dataset(args.dataset)
    if args.command == "template":
        payload = create_review_template(dataset, args.reviewer_id)
        _write_json(args.output, payload)
        print(json.dumps({"output": str(args.output), "case_count": len(payload["labels"]), "status": "draft"}, indent=2))
        return 0
    if args.command == "validate":
        review = _read_json(args.review)
        print(json.dumps(validate_review(review, dataset, require_complete=True), indent=2))
        return 0
    left = _read_json(args.left)
    right = _read_json(args.right)
    report = compare_reviews(dataset, left, right)
    _write_json(args.output, report)
    print(json.dumps({key: report[key] for key in ("case_count", "full_agreement_count", "adjudication_required_count")}, indent=2))
    return 0


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
