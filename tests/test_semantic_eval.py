import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools.semantic_eval.dataset import (
    DatasetError,
    evaluate_lexical_baseline,
    load_dataset,
    review_markdown,
    validate_dataset,
)
from tools.semantic_eval.reviews import (
    ReviewError,
    compare_reviews,
    create_review_template,
    dataset_sha256,
    validate_review,
)
from tools.semantic_eval.adjudication import (
    AdjudicationError,
    comparison_sha256,
    freeze_dataset,
    validate_adjudication,
)


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "docs/evals/data/phase-13-rider-copy-pairs.v1.json"
SCHEMA_PATH = ROOT / "tools/semantic_eval/dataset.schema.json"
REVIEW_SCHEMA_PATH = ROOT / "tools/semantic_eval/review.schema.json"
ADJUDICATION_PATH = ROOT / "docs/evals/reviews/phase-13-adjudication.v1.json"


class SemanticEvaluationDatasetTests(unittest.TestCase):
    def setUp(self):
        self.dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    def test_seed_dataset_is_valid_balanced_and_provisional(self):
        result = validate_dataset(self.dataset)
        self.assertEqual(result["case_count"], 26)
        self.assertEqual(result["status"], "provisional")
        self.assertGreaterEqual(result["counts"]["copy-similarity:holdout"], 2)
        self.assertGreaterEqual(result["counts"]["claim-support:holdout"], 2)

    def test_portable_schema_declares_same_dataset_version(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["schema_version"]["const"], self.dataset["schema_version"])
        self.assertFalse(schema["additionalProperties"])
        review_schema = json.loads(REVIEW_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(review_schema["properties"]["schema_version"]["const"], "1.0")

    def test_loader_rejects_duplicate_state_and_split_leakage(self):
        duplicate = copy.deepcopy(self.dataset)
        duplicate["cases"][1]["state"] = duplicate["cases"][0]["state"]
        with self.assertRaisesRegex(DatasetError, "duplicates another case state"):
            validate_dataset(duplicate)

        no_claim_holdout = copy.deepcopy(self.dataset)
        for case in no_claim_holdout["cases"]:
            if case["task"] == "claim-support":
                case["split"] = "calibration"
        with self.assertRaisesRegex(DatasetError, "claim-support requires at least two holdout"):
            validate_dataset(no_claim_holdout)

    def test_rejects_personal_contact_data_and_false_review_claims(self):
        pii = copy.deepcopy(self.dataset)
        pii["cases"][0]["state"]["left"] = "Contact sales@example.com for details."
        with self.assertRaisesRegex(DatasetError, "personal contact data"):
            validate_dataset(pii)

        false_review = copy.deepcopy(self.dataset)
        false_review["cases"][0]["adjudication"]["reviewer_labels"] = [{"reviewer": "A", "label": "equivalent"}]
        with self.assertRaisesRegex(DatasetError, "cannot claim completed adjudication"):
            validate_dataset(false_review)

    def test_baseline_exposes_semantic_gaps_without_claiming_acceptance(self):
        report = evaluate_lexical_baseline(self.dataset)
        self.assertFalse(report["acceptance_evidence"])
        self.assertIn("sim-cal-003", report["semantic_gap_case_ids"])
        self.assertIn("sim-hold-003", report["semantic_gap_case_ids"])
        self.assertEqual(report["task_metrics"]["copy-similarity"], {"matched": 12, "total": 18, "accuracy": 0.667})
        self.assertEqual(report["task_metrics"]["claim-support"], {"matched": 2, "total": 8, "accuracy": 0.25})
        by_id = {item["id"]: item for item in report["results"]}
        self.assertEqual(by_id["sim-cal-006"]["predicted_action"], "allow")
        self.assertEqual(by_id["claim-cal-002"]["predicted_action"], "review")

    def test_review_worksheet_omits_expected_labels(self):
        worksheet = review_markdown(self.dataset)
        self.assertIn("## sim-hold-001", worksheet)
        self.assertIn("Reviewer label:", worksheet)
        self.assertNotIn('"semantic_relation"', worksheet)
        self.assertNotIn("Expected action", worksheet)

    def test_load_dataset_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dataset.json"
            path.write_text(json.dumps(self.dataset), encoding="utf-8")
            loaded = load_dataset(path)
        self.assertEqual(loaded["dataset_id"], self.dataset["dataset_id"])

    def test_review_template_is_blinded_bound_and_incomplete(self):
        review = create_review_template(self.dataset, "reviewer-a")
        self.assertEqual(review["dataset_sha256"], dataset_sha256(self.dataset))
        self.assertEqual(len(review["labels"]), len(self.dataset["cases"]))
        self.assertTrue(all(item["label"] is None for item in review["labels"]))
        summary = validate_review(review, self.dataset, require_complete=False)
        self.assertEqual(summary["completed_count"], 0)
        with self.assertRaisesRegex(ReviewError, "status must be complete"):
            validate_review(review, self.dataset, require_complete=True)

    def test_review_rejects_dataset_drift_duplicate_ids_and_incomplete_labels(self):
        review = complete_review(self.dataset, "reviewer-a")
        review["dataset_sha256"] = "0" * 64
        with self.assertRaisesRegex(ReviewError, "does not match the exact dataset"):
            validate_review(review, self.dataset)

        review = complete_review(self.dataset, "reviewer-a")
        review["labels"][1]["case_id"] = review["labels"][0]["case_id"]
        with self.assertRaisesRegex(ReviewError, "duplicate case IDs"):
            validate_review(review, self.dataset)

        review = complete_review(self.dataset, "reviewer-a")
        review["labels"][0]["label"] = None
        with self.assertRaisesRegex(ReviewError, "copy label is unsupported"):
            validate_review(review, self.dataset)

    def test_comparison_requires_independent_reviewers_and_reports_disagreements(self):
        left = complete_review(self.dataset, "reviewer-a")
        right = complete_review(self.dataset, "reviewer-b")
        right["labels"][0]["action"] = "review"
        report = compare_reviews(self.dataset, left, right)
        self.assertEqual(report["full_agreement_count"], 25)
        self.assertEqual(report["adjudication_required_count"], 1)
        self.assertTrue(report["cases"][0]["adjudication_required"])

        right["reviewer_id"] = "REVIEWER-A"
        with self.assertRaisesRegex(ReviewError, "different reviewer IDs"):
            compare_reviews(self.dataset, left, right)

    def test_adjudication_freezes_reviews_without_mutating_source(self):
        left, right = reviews_with_five_real_disagreements(self.dataset)
        comparison = compare_reviews(self.dataset, left, right)
        adjudication = adjudication_for(comparison, self.dataset)
        summary = validate_adjudication(self.dataset, left, right, adjudication)
        self.assertEqual(summary["decision_count"], 5)
        frozen = freeze_dataset(self.dataset, left, right, adjudication)
        self.assertEqual(self.dataset["status"], "provisional")
        self.assertEqual(frozen["status"], "adjudicated")
        self.assertTrue(all(case["adjudication"]["status"] == "adjudicated" for case in frozen["cases"]))
        by_id = {case["id"]: case for case in frozen["cases"]}
        self.assertEqual(by_id["sim-cal-010"]["expected"]["semantic_relation"], "related-distinct")
        self.assertEqual(by_id["sim-hold-006"]["expected"]["action"], "block")

    def test_adjudication_rejects_missing_decision_and_comparison_drift(self):
        left, right = reviews_with_five_real_disagreements(self.dataset)
        comparison = compare_reviews(self.dataset, left, right)
        adjudication = adjudication_for(comparison, self.dataset)
        adjudication["decisions"].pop()
        with self.assertRaisesRegex(AdjudicationError, "coverage invalid"):
            validate_adjudication(self.dataset, left, right, adjudication)

        adjudication = adjudication_for(comparison, self.dataset)
        adjudication["comparison_sha256"] = "0" * 64
        with self.assertRaisesRegex(AdjudicationError, "comparison_sha256 does not match"):
            validate_adjudication(self.dataset, left, right, adjudication)


def complete_review(dataset, reviewer_id):
    review = create_review_template(dataset, reviewer_id)
    review["status"] = "complete"
    review["reviewed_at"] = "2026-10-03"
    by_id = {case["id"]: case for case in dataset["cases"]}
    for item in review["labels"]:
        expected = by_id[item["case_id"]]["expected"]
        item["label"] = expected.get("semantic_relation", expected.get("support"))
        item["action"] = expected["action"]
        item["intentional_refrain"] = expected.get("intentional_refrain", "not-applicable")
    return review


def reviews_with_five_real_disagreements(dataset):
    left = complete_review(dataset, "reviewer-a")
    right = complete_review(dataset, "reviewer-b")
    left_by_id = {item["case_id"]: item for item in left["labels"]}
    for case_id in ("sim-cal-003", "sim-cal-009", "sim-hold-001", "sim-hold-006"):
        left_by_id[case_id]["action"] = "review"
    left_by_id["sim-cal-010"]["label"] = "distinct"
    right_by_id = {item["case_id"]: item for item in right["labels"]}
    right_by_id["sim-cal-010"]["label"] = "related-distinct"
    return left, right


def adjudication_for(comparison, dataset):
    source = json.loads(ADJUDICATION_PATH.read_text(encoding="utf-8"))
    source["source_dataset_sha256"] = dataset_sha256(dataset)
    source["comparison_sha256"] = comparison_sha256(comparison)
    return source


if __name__ == "__main__":
    unittest.main()
