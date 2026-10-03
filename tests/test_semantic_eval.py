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


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "docs/evals/data/phase-13-rider-copy-pairs.v1.json"
SCHEMA_PATH = ROOT / "tools/semantic_eval/dataset.schema.json"


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
        with self.assertRaisesRegex(DatasetError, "cannot claim reviewer labels"):
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


if __name__ == "__main__":
    unittest.main()
