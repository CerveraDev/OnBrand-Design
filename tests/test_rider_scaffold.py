import json
from pathlib import Path
import re
import unittest

from tools.email_scaffold import (
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
        self.assertEqual(self.source_html.count("REQUEST MORE INFORMAITON"), 2)
        self.assertEqual(self.source_html.count("ARTTS"), 3)
        self.assertNotIn("REQUEST MORE INFORMAITON", self.canonical_html)
        self.assertNotIn("ARTTS", self.canonical_html)
        self.assertNotIn("UNBRANDED FOOTER", self.canonical_html)

    def test_scaffold_has_expected_marker_pairs(self):
        self.assertEqual(len(self.rows), 90)
        modules = find_module_boundaries(self.rows)
        self.assertEqual(
            [(module.label, module.start_marker_row, module.end_marker_row) for module in modules],
            [
                ("TWO-COLUMN HEADER", 2, 4),
                ("AI GENERATED IMAGE BASED ON PROMPT", 5, 7),
                ("BODY - MASONRY LAYOUT", 8, 12),
                ("HERO - DARK FRAMED LAYOUT", 13, 16),
                ("BODY - LIGHT THEN DARK LAYOUT", 17, 25),
                ("INVITE - TWO-COLUMN HEADER - COLLABORATION", 26, 29),
                ("INVITE - DARK BODY", 30, 34),
                ("HERO - FULL-WIDTH WITH LIVE TEXT HEADING AND LOGO", 35, 37),
                ("HERO - LIGHT LAYOUT - FRAMED", 38, 41),
                ("BODY - DARK THEN LIGHT LAYOUT", 42, 60),
                ("BRANDED FOOTER", 61, 70),
                ("OUTSIDE-BROKER CUSTOMIZABLE FOOTER", 71, 80),
                ("IN-HOUSE AGENT FOOTER", 81, 90),
            ],
        )

    def test_marker_rows_are_excluded_from_rendered_outputs(self):
        rendered = render_without_marker_rows(self.canonical_html)
        self.assertNotIn("#55ebb9", rendered.lower())
        self.assertNotIn("#ff81fb", rendered.lower())
        self.assertNotIn("START - ", rendered)
        self.assertNotIn("END - ", rendered)
        self.assertIn("row-1", rendered)
        self.assertIn("row-3", rendered)

    def test_brand_color_analysis_excludes_authoring_marker_colors(self):
        colors = analyze_style_colors(self.rows)
        self.assertNotIn("#55ebb9", colors)
        self.assertNotIn("#ff81fb", colors)
        self.assertNotIn("#393d47", colors)
        self.assertEqual(colors["#000000"], 156)
        self.assertEqual(colors["#ffffff"], 102)
        self.assertEqual(colors["#dddddd"], 6)
        self.assertEqual(colors["#636565"], 3)
        self.assertEqual(colors["#999999"], 2)
        self.assertEqual(colors["#6b6b6b"], 1)
        self.assertEqual(colors["#f7f7f7"], 1)


class RiderAgentDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical_html = (SCAFFOLD_DIR / "rider-scaffolding.canonical.html").read_text()

    def test_agent_index_is_deterministic_and_references_existing_records(self):
        index = json.loads((AGENTS_DIR / "index.json").read_text())
        self.assertEqual(index["active_agent_ids"], ["jake-lecce"])
        self.assertEqual(index["output_order"], ["jake-lecce"])
        for agent_id in index["output_order"]:
            self.assertIn(agent_id, index["active_agent_ids"])
            self.assertTrue((AGENTS_DIR / f"{agent_id}.json").exists())

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
            self.assertIsInstance(agent["headshot"]["src"], str)
            self.assertTrue(agent["headshot"]["src"])

    def test_jake_record_uses_only_scaffold_facts(self):
        agent = json.loads((AGENTS_DIR / "jake-lecce.json").read_text())
        self.assertEqual(agent["display_name"], "Jake Lecce")
        self.assertEqual(agent["title"], "Sales Director")
        self.assertEqual(agent["phone"], "305 432 9969")
        self.assertEqual(agent["email"], "jake@theriderresidences.com")
        self.assertIn(agent["headshot"]["src"], self.canonical_html)


if __name__ == "__main__":
    unittest.main()
