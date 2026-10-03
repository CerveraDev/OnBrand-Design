import json
from pathlib import Path
import re
import unittest

from tools.email_scaffold import (
    STATIC_END_MARKER_COLOR,
    STATIC_START_MARKER_COLOR,
    analyze_style_colors,
    apply_canonical_text_corrections,
    find_module_boundaries,
    parse_rows,
    render_without_marker_rows,
)


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_DIR = ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold"
AGENTS_DIR = ROOT / "projects/the-rider/skills/onbrand-the-rider-email/data/agents"


class RiderScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_html = (SCAFFOLD_DIR / "rider-scaffolding.source.html").read_text()
        cls.canonical_html = (SCAFFOLD_DIR / "rider-scaffolding.canonical.html").read_text()
        cls.rows = parse_rows(cls.canonical_html)

    def test_canonical_copy_applies_expected_text_corrections(self):
        self.assertEqual(
            apply_canonical_text_corrections(self.source_html),
            self.canonical_html,
        )
        self.assertEqual(self.source_html.count("REQUEST MORE INFORMAITON"), 0)
        self.assertEqual(self.source_html.count("ARTTS"), 0)
        self.assertEqual(self.source_html.count("UNBRANDED FOOTER"), 2)
        self.assertNotIn("REQUEST MORE INFORMAITON", self.canonical_html)
        self.assertNotIn("ARTTS", self.canonical_html)
        self.assertNotIn("UNBRANDED FOOTER", self.canonical_html)
        self.assertTrue((SCAFFOLD_DIR / "provenance/rider-scaffolding.source.legacy-2026-09-30.html").is_file())

    def test_scaffold_has_expected_marker_pairs(self):
        self.assertEqual(len(self.rows), 102)
        modules = find_module_boundaries(self.rows)
        self.assertEqual(
            [(module.label, module.start_marker_row, module.end_marker_row) for module in modules],
            [
                ("TWO-COLUMN HEADER", 2, 4),
                ("AI GENERATED IMAGE BASED ON PROMPT", 5, 7),
                ("BODY - MASONRY LAYOUT", 8, 12),
                ("ONE-COLUMN HEADER DARK", 13, 15),
                ("HERO - LIVE TEXT HEADING - DARK FRAMED LAYOUT", 16, 18),
                ("BODY - LIGHT THEN DARK LAYOUT", 19, 27),
                ("INVITE - TWO-COLUMN HEADER - COLLABORATION", 28, 31),
                ("INVITE - DARK BODY", 32, 36),
                ("HEADER & HERO - LIVE TEXT HEADING - FULL-WIDTH", 37, 39),
                ("ONE-COLUMN HEADER LIGHT", 40, 42),
                ("HERO - LIVE TEXT HEADING - LIGHT LAYOUT - FRAMED", 43, 45),
                ("STATIC BLOCK", 53, 55),
                ("STATIC BLOCK", 57, 59),
                ("STATIC BLOCK", 62, 64),
                ("STATIC BLOCK", 65, 67),
                ("BODY - DARK THEN LIGHT LAYOUT", 46, 72),
                ("BRANDED FOOTER", 73, 82),
                ("OUTSIDE-BROKER CUSTOMIZABLE FOOTER", 83, 92),
                ("IN-HOUSE AGENT FOOTER", 93, 102),
            ],
        )
        for module in modules:
            if module.label == "STATIC BLOCK":
                self.assertIn(
                    STATIC_START_MARKER_COLOR,
                    self.rows[module.start_marker_row - 1].style_colors,
                )
                self.assertIn(
                    STATIC_END_MARKER_COLOR,
                    self.rows[module.end_marker_row - 1].style_colors,
                )

    def test_marker_rows_are_excluded_from_rendered_outputs(self):
        rendered = render_without_marker_rows(self.canonical_html)
        self.assertNotIn("#55ebb9", rendered.lower())
        self.assertNotIn("#ff81fb", rendered.lower())
        self.assertNotIn("#ffd675", rendered.lower())
        self.assertNotIn("#75edff", rendered.lower())
        self.assertNotIn("START - ", rendered)
        self.assertNotIn("END - ", rendered)
        self.assertIn("row-1", rendered)
        self.assertIn("row-3", rendered)
        self.assertIn("row-54", rendered)

    def test_brand_color_analysis_excludes_authoring_marker_colors(self):
        colors = analyze_style_colors(self.rows)
        self.assertNotIn("#55ebb9", colors)
        self.assertNotIn("#ff81fb", colors)
        self.assertNotIn("#ffd675", colors)
        self.assertNotIn("#75edff", colors)
        self.assertNotIn("#393d47", colors)
        self.assertEqual(colors["#000000"], 156)
        self.assertEqual(colors["#ffffff"], 101)
        self.assertEqual(colors["#dddddd"], 6)
        self.assertEqual(colors["#636565"], 3)
        self.assertEqual(colors["#999999"], 2)
        self.assertEqual(colors["#f7f7f7"], 2)
        self.assertEqual(colors["#6b6b6b"], 1)


class RiderAgentDataTests(unittest.TestCase):
    EXPECTED = {
        "paulie-hankin": ("Paulie Hankin", "Sales Director", "+1 786 385 4450", "Paulie@TheRiderResidences.com", "id:31E0v0XEN2IAAAAAAAABlQ"),
        "angelica-cruz": ("Angelica Cruz", "In-house Sales Agent", "+1 786 329 1549", "Angelica@TheRiderResidences.com", "id:31E0v0XEN2IAAAAAAAABkQ"),
        "julian-oliveros": ("Julian Oliveros", "In-house Sales Agent", "+1 239 384 0836", "Julian@TheRiderResidences.com", "id:31E0v0XEN2IAAAAAAAABkg"),
        "omar-santana": ("Omar Santana", "In-house Sales Agent", "+1 305 797 6337", "Omar@TheRiderResidences.com", "id:31E0v0XEN2IAAAAAAAABlA"),
        "pablo-rodriguez": ("Pablo Rodriguez", "In-house Sales Agent", "+1 561 980 6876", "Pablo@TheRiderResidences.com", "id:31E0v0XEN2IAAAAAAAABkA"),
        "yessika-arevalo": ("Yessika Arevalo", "In-house Sales Agent", "+1 786 277 6103", "Yessika@TheRiderResidences.com", "id:31E0v0XEN2IAAAAAAAABkw"),
    }

    def test_agent_index_is_deterministic_and_references_existing_records(self):
        index = json.loads((AGENTS_DIR / "index.json").read_text())
        expected_order = list(self.EXPECTED)
        self.assertEqual(index["active_agent_ids"], expected_order)
        self.assertEqual(index["output_order"], expected_order)
        for agent_id in index["output_order"]:
            self.assertIn(agent_id, index["active_agent_ids"])
            self.assertTrue((AGENTS_DIR / f"{agent_id}.json").exists())
        self.assertNotIn("jake-lecce", index["active_agent_ids"])
        self.assertFalse((AGENTS_DIR / "jake-lecce.json").exists())
        self.assertTrue((AGENTS_DIR / "archived/jake-lecce.json").exists())

    def test_agent_records_match_required_schema_shape(self):
        schema = json.loads((AGENTS_DIR / "agent.schema.json").read_text())
        allowed = set(schema["properties"])
        required = set(schema["required"])
        email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        for path in sorted(AGENTS_DIR.glob("*.json")):
            if path.name in {"agent.schema.json", "index.json"}:
                continue
            agent = json.loads(path.read_text())
            self.assertEqual(set(agent) - allowed, set(), path.name)
            self.assertLessEqual(required, set(agent), path.name)
            self.assertRegex(agent["id"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertRegex(agent["email"], email_re)
            self.assertRegex(agent["headshot"]["asset_id"], r"^id:.+")
            self.assertNotIn("src", agent["headshot"])

    def test_agent_records_match_verified_roster(self):
        for agent_id, expected in self.EXPECTED.items():
            agent = json.loads((AGENTS_DIR / f"{agent_id}.json").read_text())
            actual = (
                agent["display_name"],
                agent["title"],
                agent["phone"],
                agent["email"],
                agent["headshot"]["asset_id"],
            )
            self.assertEqual(actual, expected)
        julian = json.loads((AGENTS_DIR / "julian-oliveros.json").read_text())
        self.assertEqual(julian["headshot"]["alt"], "Julian Oliveros, In-house Sales Agent")


if __name__ == "__main__":
    unittest.main()
