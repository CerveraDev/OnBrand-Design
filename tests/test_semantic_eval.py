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
from tools.semantic_eval.jev_pilot import (
    QuestionSetError,
    build_request_batch,
    question_set_sha256,
    validate_question_set,
)
from tools.semantic_eval.provider import ProviderError, run_provider_batch
from tools.semantic_eval.evaluation import EvaluationError, evaluate_calibration


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "docs/evals/data/phase-13-rider-copy-pairs.v1.json"
SCHEMA_PATH = ROOT / "tools/semantic_eval/dataset.schema.json"
REVIEW_SCHEMA_PATH = ROOT / "tools/semantic_eval/review.schema.json"
ADJUDICATION_PATH = ROOT / "docs/evals/reviews/phase-13-adjudication.v1.json"
FROZEN_DATASET_PATH = ROOT / "docs/evals/data/phase-13-rider-copy-pairs.v1.frozen.json"
QUESTION_SET_PATH = ROOT / "docs/evals/config/phase-13-jev-questions.v1.json"
QUESTION_SET_SCHEMA_PATH = ROOT / "tools/semantic_eval/question_set.schema.json"
CALIBRATION_BATCH_PATH = ROOT / "docs/evals/requests/phase-13-jev-calibration.v1.json"
LIVE_RECEIPT_PATH = ROOT / "docs/evals/receipts/phase-13-jev-calibration.live.v1.json"
FROZEN_BASELINE_PATH = ROOT / "docs/evals/phase-13-lexical-baseline.frozen.v1.json"


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

    def test_question_set_is_pinned_locked_and_non_production(self):
        question_set = json.loads(QUESTION_SET_PATH.read_text(encoding="utf-8"))
        question_schema = json.loads(QUESTION_SET_SCHEMA_PATH.read_text(encoding="utf-8"))
        summary = validate_question_set(question_set)
        self.assertEqual(summary["model"], "jev-1.13.0")
        self.assertEqual(summary["question_count"], 6)
        self.assertEqual(len(question_set_sha256(question_set)), 64)
        self.assertEqual(question_schema["properties"]["schema_version"]["const"], question_set["schema_version"])

        alias = copy.deepcopy(question_set)
        alias["model"] = "jev-latest"
        with self.assertRaisesRegex(QuestionSetError, "pinned Jev version"):
            validate_question_set(alias)

    def test_calibration_batch_excludes_holdout_and_evaluation_labels(self):
        frozen = json.loads(FROZEN_DATASET_PATH.read_text(encoding="utf-8"))
        question_set = json.loads(QUESTION_SET_PATH.read_text(encoding="utf-8"))
        batch = build_request_batch(frozen, question_set)
        self.assertEqual(batch["record_count"], 17)
        self.assertTrue(all(record["split"] == "calibration" for record in batch["records"]))
        serialized = json.dumps(batch)
        self.assertNotIn("sim-hold-", serialized)
        self.assertNotIn('"expected"', serialized)
        self.assertNotIn("reviewer_labels", serialized)
        self.assertEqual(batch["production_effect"], "none")

    def test_holdout_batch_requires_explicit_unlock(self):
        frozen = json.loads(FROZEN_DATASET_PATH.read_text(encoding="utf-8"))
        question_set = json.loads(QUESTION_SET_PATH.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(QuestionSetError, "explicit allow_holdout"):
            build_request_batch(frozen, question_set, split="holdout")
        batch = build_request_batch(frozen, question_set, split="holdout", allow_holdout=True)
        self.assertEqual(batch["record_count"], 9)
        self.assertTrue(all(record["split"] == "holdout" for record in batch["records"]))

    def test_question_batch_requires_frozen_dataset(self):
        question_set = json.loads(QUESTION_SET_PATH.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(QuestionSetError, "adjudicated frozen dataset"):
            build_request_batch(self.dataset, question_set)

    def test_disabled_provider_writes_skipped_receipt_without_transport(self):
        batch = json.loads(CALIBRATION_BATCH_PATH.read_text(encoding="utf-8"))
        question_set = json.loads(QUESTION_SET_PATH.read_text(encoding="utf-8"))
        calls = []
        receipt = run_provider_batch(
            batch,
            question_set,
            enabled=False,
            live_authorized=False,
            api_key=None,
            transport=lambda *args: calls.append(args),
            executed_at="2026-10-03T00:00:00+00:00",
        )
        self.assertEqual(receipt["status"], "disabled")
        self.assertEqual(calls, [])
        self.assertEqual(len(receipt["records"]), 17)
        self.assertTrue(all(item["status"] == "skipped" for item in receipt["records"]))
        self.assertEqual(receipt["production_effect"], "none")

    def test_enabled_provider_requires_authorization_and_key(self):
        batch = json.loads(CALIBRATION_BATCH_PATH.read_text(encoding="utf-8"))
        question_set = json.loads(QUESTION_SET_PATH.read_text(encoding="utf-8"))
        kwargs = {"transport": lambda *args: {}, "executed_at": "2026-10-03T00:00:00+00:00"}
        with self.assertRaisesRegex(ProviderError, "explicit authorization"):
            run_provider_batch(batch, question_set, enabled=True, live_authorized=False, api_key="secret", **kwargs)
        with self.assertRaisesRegex(ProviderError, "TYPESAFE_API_KEY"):
            run_provider_batch(batch, question_set, enabled=True, live_authorized=True, api_key=None, **kwargs)

    def test_fake_provider_responses_are_typed_and_receipted(self):
        batch = json.loads(CALIBRATION_BATCH_PATH.read_text(encoding="utf-8"))
        question_set = json.loads(QUESTION_SET_PATH.read_text(encoding="utf-8"))
        calls = []

        def transport(endpoint, headers, request, timeout):
            calls.append((endpoint, headers["Authorization"], timeout))
            answers = {}
            for question_id, question in request["questions"].items():
                if question["type"] == "choice":
                    options = list(question["criteria"])
                    probabilities = {option: 0.0 for option in options}
                    probabilities[options[0]] = 1.0
                    answers[question_id] = {"type": "choice", "choice": options[0], "confidence": 1.0, "probabilities": probabilities}
                else:
                    answers[question_id] = {"type": "noul", "noul": 0.0}
            return {"model": request["model"], "answers": answers, "usage": {"input_tokens": 10, "output_tokens": 2}}

        receipt = run_provider_batch(
            batch,
            question_set,
            enabled=True,
            live_authorized=True,
            api_key="test-only",
            transport=transport,
            executed_at="2026-10-03T00:00:00+00:00",
        )
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(len(calls), 17)
        self.assertTrue(all(item["status"] == "completed" for item in receipt["records"]))
        self.assertNotIn("test-only", json.dumps(receipt))

    def test_provider_rejects_model_answer_and_batch_drift(self):
        batch = json.loads(CALIBRATION_BATCH_PATH.read_text(encoding="utf-8"))
        question_set = json.loads(QUESTION_SET_PATH.read_text(encoding="utf-8"))

        def wrong_model(endpoint, headers, request, timeout):
            return {"model": "jev-other", "answers": {}, "usage": {"input_tokens": 0, "output_tokens": 0}}

        with self.assertRaisesRegex(ProviderError, "model drift"):
            run_provider_batch(
                {**batch, "records": batch["records"][:1], "record_count": 1},
                question_set,
                enabled=True,
                live_authorized=True,
                api_key="test-only",
                transport=wrong_model,
                executed_at="2026-10-03T00:00:00+00:00",
                fail_fast=True,
            )

        drifted = copy.deepcopy(batch)
        drifted["records"][0]["request"]["questions"] = {}
        with self.assertRaisesRegex(ProviderError, "drifted from the locked question set"):
            run_provider_batch(
                drifted,
                question_set,
                enabled=False,
                live_authorized=False,
                api_key=None,
                transport=lambda *args: {},
                executed_at="2026-10-03T00:00:00+00:00",
            )

    def test_live_calibration_report_is_non_production_and_reproducible(self):
        frozen = json.loads(FROZEN_DATASET_PATH.read_text(encoding="utf-8"))
        receipt = json.loads(LIVE_RECEIPT_PATH.read_text(encoding="utf-8"))
        baseline = json.loads(FROZEN_BASELINE_PATH.read_text(encoding="utf-8"))
        report = evaluate_calibration(frozen, receipt, baseline)
        self.assertFalse(report["acceptance_evidence"])
        self.assertEqual(report["production_effect"], "none")
        self.assertEqual(report["case_count"], 17)
        self.assertEqual(report["metrics"]["semantic_label_matches"], 13)
        self.assertEqual(report["metrics"]["action_matches"], 16)
        self.assertEqual(report["metrics"]["confusion"], {"tp": 9, "fp": 1, "tn": 7, "fn": 0})
        self.assertEqual(report["metrics"]["review_rate"], 0.176)
        self.assertEqual(report["lexical_baseline_comparison"]["match_delta"], 6)
        by_id = {item["case_id"]: item for item in report["results"]}
        self.assertEqual(by_id["sim-cal-012"]["predicted_action"], "review")
        self.assertEqual(by_id["claim-cal-005"]["routing_reasons"], [
            "below-high-confidence-band",
            "companion-answer-contradiction",
        ])

    def test_calibration_evaluation_rejects_incomplete_or_holdout_receipts(self):
        frozen = json.loads(FROZEN_DATASET_PATH.read_text(encoding="utf-8"))
        receipt = json.loads(LIVE_RECEIPT_PATH.read_text(encoding="utf-8"))
        baseline = json.loads(FROZEN_BASELINE_PATH.read_text(encoding="utf-8"))
        receipt["split"] = "holdout"
        with self.assertRaisesRegex(EvaluationError, "calibration-only"):
            evaluate_calibration(frozen, receipt, baseline)


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
