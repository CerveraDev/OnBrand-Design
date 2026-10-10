import hashlib
import json
import re
import unittest
from pathlib import Path

SCAFFOLD = Path(__file__).resolve().parents[1] / "projects" / "the-rider" / "social" / "scaffold"


class RiderSocialScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((SCAFFOLD / "frame-catalog.json").read_text(encoding="utf-8"))
        cls.html = (SCAFFOLD / "scaffold.html").read_text(encoding="utf-8")
        cls.css = (SCAFFOLD / "scaffold.css").read_text(encoding="utf-8")

    def test_catalog_is_bound_to_committed_files(self):
        for name, record in self.catalog["files"].items():
            digest = hashlib.sha256((SCAFFOLD / name).read_bytes()).hexdigest()
            self.assertEqual(digest, record["sha256"], name)

    def test_import_matched_the_live_page(self):
        self.assertEqual(self.catalog["verification"]["differences"], 0)

    def test_frame_ids_are_unique_and_present_in_markup(self):
        ids = [frame["id"] for frame in self.catalog["frames"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(re.findall(r'data-frame-id="([^"]+)"', self.html), ids)
        for frame_id in ids:
            self.assertRegex(frame_id, r"^S[PCG]-\d{2}$")
            self.assertTrue((SCAFFOLD / "previews" / f"{frame_id}.jpg").is_file(), frame_id)

    def test_every_frame_has_one_canvas_and_matching_slots(self):
        sections = re.split(r'(?=<div[^>]*data-frame-id=")', self.html)[1:]
        self.assertEqual(len(sections), len(self.catalog["frames"]))
        for section, frame in zip(sections, self.catalog["frames"]):
            canvas = frame["canvas"]
            self.assertEqual(section.count("data-frame-canvas="), 1, frame["id"])
            self.assertIn(f'data-frame-canvas="{canvas["width"]}x{canvas["height"]}"', section)
            observed = frame["observed"]
            expected = [slot["slot"] for slot in observed["image_slots"] + observed["text_slots"]]
            if observed["logo"]:
                expected.append(observed["logo"]["slot"])
            self.assertEqual(sorted(re.findall(r'data-slot="([^"]+)"', section)), sorted(expected), frame["id"])

    def test_scaffold_carries_no_site_code(self):
        self.assertNotIn("<script", self.html)
        self.assertNotIn("<style", self.html)
        for text in (self.html, self.css):
            for marker in ("wp-content", "wp-includes", "start-up.local", "jet-", "admin-bar"):
                self.assertNotIn(marker, text)


if __name__ == "__main__":
    unittest.main()
