import copy
import json
from pathlib import Path
import unittest

from tools.email_scaffold import (
    ScaffoldError,
    find_annotation_boundaries,
    find_module_boundaries,
    load_block_metadata,
    parse_marker_elements,
    parse_rows,
    render_without_authoring_markers,
    validate_block_metadata,
)


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_DIR = ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold"
SCAFFOLD_PATH = SCAFFOLD_DIR / "rider-scaffolding.phase16-intake.html"
METADATA_PATH = SCAFFOLD_DIR / "rider-scaffolding.phase16-block-metadata.json"


class Phase16ScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = SCAFFOLD_PATH.read_text(encoding="utf-8")
        cls.rows = parse_rows(cls.html)
        cls.modules = find_module_boundaries(cls.rows)
        cls.annotations = find_annotation_boundaries(cls.html, cls.rows)

    def test_granular_parser_separates_modules_from_annotations(self):
        self.assertEqual(len(self.rows), 94)
        self.assertEqual(len(parse_marker_elements(self.html, self.rows)), 68)
        self.assertEqual(
            [(item.start_marker_row, item.end_marker_row) for item in self.modules],
            [
                (2, 4), (5, 7), (8, 12), (13, 15), (16, 18),
                (19, 22), (23, 27), (28, 30), (31, 33), (34, 36),
                (37, 45), (46, 48), (49, 51), (53, 55), (56, 58),
                (59, 61), (62, 64), (65, 74), (75, 84), (85, 94),
            ],
        )
        self.assertEqual(len(self.annotations), 14)
        self.assertNotIn(
            "IMAGE BLOCK TO BE USED ON INVITES - IMAGE MAY CHANGE",
            [item.label for item in self.modules],
        )

    def test_nested_annotations_retain_module_and_annotation_parents(self):
        by_label = {item.label: item for item in self.annotations}
        invite_image = by_label["IMAGE BLOCK TO BE USED ON INVITES - IMAGE MAY CHANGE"]
        self.assertEqual(invite_image.parent_module_label, "INVITE - DARK BODY")
        self.assertIsNone(invite_image.parent_annotation_label)

        amplification = by_label["AMPLIFICATION OF BULLET POINT."]
        self.assertEqual(amplification.depth, 1)
        self.assertEqual(
            amplification.parent_annotation_label,
            "LIST THAT HAS BULLET POINTS WITH AMPLIFICATION. REPEAT FOR AS MANY "
            "BULLET POINTS ARE NEEDED IN THE COPY.",
        )
        standalone = by_label[
            "ANOTHER IMAGE BLOCK TO BE USED BETWEEN COPY BLOCKS - NEVER USE THIS "
            "IMAGE, IT'S ONLY A PLACEHOLDER."
        ]
        self.assertIsNone(standalone.parent_module_label)

    def test_nested_parser_rejects_mismatched_labels(self):
        malformed = self.html.replace(
            "END - AMPLIFICATION OF BULLET POINT.",
            "END - WRONG AMPLIFICATION LABEL",
            1,
        )
        with self.assertRaisesRegex(ScaffoldError, "Marker mismatch"):
            find_annotation_boundaries(malformed)

    def test_authoring_marker_removal_keeps_annotated_content_rows(self):
        rendered = render_without_authoring_markers(self.html)
        self.assertNotIn("START - ", rendered)
        self.assertNotIn("END - ", rendered)
        self.assertNotIn("#55ebb9", rendered.lower())
        self.assertNotIn("#ff81fb", rendered.lower())
        self.assertNotIn("#ffd675", rendered.lower())
        self.assertNotIn("#75edff", rendered.lower())
        self.assertIn('class="row row-25"', rendered)
        self.assertIn('class="row row-52"', rendered)
        self.assertIn("SOHO HOUSE AND EQUINOX", rendered)
        self.assertIn("$500K's", rendered)

    def test_refined_metadata_covers_every_boundary_and_annotation(self):
        metadata = load_block_metadata(
            METADATA_PATH,
            SCAFFOLD_PATH,
            self.modules,
            self.annotations,
        )
        self.assertEqual(len(metadata["modules"]), 20)
        self.assertEqual(len(metadata["annotations"]), 14)
        self.assertEqual(
            next(item for item in metadata["modules"] if item["code"] == "B-04")["id"],
            "body-long-form",
        )
        self.assertEqual(
            next(
                item
                for item in metadata["annotations"]
                if item["id"] == "body-list-amplification"
            )["parent_annotation_id"],
            "body-amplified-list",
        )

    def test_refined_metadata_is_checksum_bound(self):
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        altered = copy.deepcopy(metadata)
        altered["source"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ScaffoldError, "checksum"):
            validate_block_metadata(altered, self.html, self.modules, self.annotations)


if __name__ == "__main__":
    unittest.main()
