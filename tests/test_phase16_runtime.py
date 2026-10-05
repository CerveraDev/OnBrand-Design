import json
from pathlib import Path
import tempfile
import unittest

from tools.rider_campaign_runtime.composition import (
    CompositionError,
    build_hero_configurations,
    build_module_catalog,
    build_sequence_configurations,
    create_composition_plan,
    write_catalog_artifacts,
)
from tools.rider_campaign_runtime.scaffold import catalog, load_scaffold, module_rows
from tools.rider_campaign_runtime.slots import SlotError, apply_module_slots


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_DIR = ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold"


class Phase16RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scaffold = load_scaffold(
            SCAFFOLD_DIR / "rider-scaffolding.phase16-intake.html",
            SCAFFOLD_DIR / "rider-scaffolding.phase16-slot-map.json",
            SCAFFOLD_DIR / "rider-scaffolding.phase16-block-metadata.json",
        )

    def test_refined_scaffold_uses_stable_ids_codes_and_synthetic_image_module(self):
        self.assertTrue(self.scaffold.refined)
        self.assertEqual(len(catalog(self.scaffold)), 21)
        module_catalog = build_module_catalog(self.scaffold)
        entries = {entry["code"]: entry for entry in module_catalog["entries"]}
        self.assertEqual(len(entries), 18)
        self.assertEqual(entries["B-04"]["scaffold_module_id"], "body-long-form")
        self.assertEqual(entries["I-02"]["scaffold_module_id"], "body-inline-image-secondary")
        self.assertEqual(entries["B-04"]["theme"]["default"], "dark")
        self.assertEqual(entries["B-03"]["theme"]["user_selectable"], False)
        self.assertEqual(build_hero_configurations(module_catalog)["option_count"], 14)

    def test_every_annotation_is_owned_by_a_slot_or_nested_owner(self):
        metadata = json.loads(
            (SCAFFOLD_DIR / "rider-scaffolding.phase16-block-metadata.json").read_text()
        )
        mapped = {
            definition["annotation_id"]
            for slots in self.scaffold.slot_map.values()
            for definition in slots.values()
            if isinstance(definition, dict) and definition.get("annotation_id")
        }
        nested = {
            item["id"]
            for item in metadata["annotations"]
            if item["parent_annotation_id"] in mapped
        }
        self.assertEqual(
            mapped | nested,
            {item["id"] for item in metadata["annotations"]},
        )

    def test_required_and_optional_annotation_slots_are_deterministic(self):
        html = "".join(module_rows(self.scaffold, "body-long-form"))
        with self.assertRaisesRegex(SlotError, "missing required slot"):
            apply_module_slots(
                "body-long-form",
                html,
                self.scaffold.slot_map["body-long-form"],
                {},
                manifest_assets={},
            )

        rendered, used = apply_module_slots(
            "body-long-form",
            html,
            self.scaffold.slot_map["body-long-form"],
            {"body_copy_primary": {"kind": "text", "value": "One approved campaign paragraph."}},
            manifest_assets={},
        )
        self.assertEqual(used, [])
        self.assertIn("One approved campaign paragraph.", rendered)
        for placeholder in (
            "SOHO HOUSE AND EQUINOX ARE MINUTES",
            "For anyone relocating",
            "BIG MOVES IN THE AREA",
            "LOREM IPSUM",
            "tower-front-facade-day-option-1.jpg",
            "START - ",
            "END - ",
        ):
            self.assertNotIn(placeholder, rendered)
        self.assertEqual(rendered.lower().count("<table"), rendered.lower().count("</table>"))
        self.assertEqual(rendered.lower().count("<tr"), rendered.lower().count("</tr>"))
        self.assertEqual(rendered.lower().count("<td"), rendered.lower().count("</td>"))

    def test_repeating_list_slots_render_each_approved_item_once(self):
        html = "".join(module_rows(self.scaffold, "body-long-form"))
        rendered, _ = apply_module_slots(
            "body-long-form",
            html,
            self.scaffold.slot_map["body-long-form"],
            {
                "body_copy_primary": {"kind": "text", "value": "Primary copy."},
                "leading_terms": {
                    "kind": "text_list",
                    "items": ["SAME ROUTINE", "SAME MEMBERSHIP", "NEW CITY"],
                },
                "list_eyebrow": {"kind": "text", "value": "MOVES THAT MATTER"},
                "amplified_list": {
                    "kind": "amplified_list",
                    "items": [
                        {"term": "SOHO HOUSE", "amplification": "A renewed social anchor."},
                        {"term": "EQUINOX", "amplification": "A familiar wellness routine."},
                    ],
                },
                "followup_list": {
                    "kind": "text_list",
                    "items": ["Five minutes away.", "One connected neighborhood."],
                },
            },
            manifest_assets={},
        )
        for text in (
            "SAME ROUTINE",
            "SAME MEMBERSHIP",
            "NEW CITY",
            "SOHO HOUSE",
            "A renewed social anchor.",
            "EQUINOX",
            "A familiar wellness routine.",
            "Five minutes away.",
            "One connected neighborhood.",
        ):
            self.assertEqual(rendered.count(text), 1, text)
        self.assertNotIn("75,000 SQFT", rendered)

    def test_generated_microcopy_word_limit_is_enforced(self):
        html = "".join(module_rows(self.scaffold, "body-long-form"))
        with self.assertRaisesRegex(SlotError, "at most 5 words"):
            apply_module_slots(
                "body-long-form",
                html,
                self.scaffold.slot_map["body-long-form"],
                {
                    "body_copy_primary": {"kind": "text", "value": "Primary copy."},
                    "list_eyebrow": {
                        "kind": "text",
                        "value": "THIS PHRASE CONTAINS FAR TOO MANY WORDS",
                    },
                },
                manifest_assets={},
            )

    def test_every_declared_slot_resolves_and_preserves_table_balance(self):
        for module_id, definitions in self.scaffold.slot_map.items():
            supplied = {}
            for slot_name, definition in definitions.items():
                if isinstance(definition, list):
                    operations = {rule["operation"] for rule in definition}
                    kind = "url" if "replace_href" in operations else "text"
                else:
                    kind = definition.get("allowed_kinds", ["text"])[0]
                supplied[slot_name] = sample_slot(kind, module_id, slot_name)
            rendered, _ = apply_module_slots(
                module_id,
                "".join(module_rows(self.scaffold, module_id)),
                definitions,
                supplied,
                manifest_assets={},
            )
            self.assertEqual(
                rendered.lower().count("<table"),
                rendered.lower().count("</table>"),
                module_id,
            )
            self.assertNotIn("START - ", rendered, module_id)
            self.assertNotIn("END - ", rendered, module_id)

    def test_standalone_placeholder_image_requires_replacement(self):
        html = "".join(module_rows(self.scaffold, "body-inline-image-secondary"))
        slot_map = self.scaffold.slot_map["body-inline-image-secondary"]
        with self.assertRaisesRegex(SlotError, "missing required slot"):
            apply_module_slots(
                "body-inline-image-secondary", html, slot_map, {}, manifest_assets={}
            )
        rendered, used = apply_module_slots(
            "body-inline-image-secondary",
            html,
            slot_map,
            {
                "image": {
                    "kind": "image",
                    "src": "https://example.com/approved-rider-image.jpg",
                    "alt": "Approved Rider campaign image",
                }
            },
            manifest_assets={},
        )
        self.assertIn("approved-rider-image.jpg", rendered)
        self.assertNotIn("37e1ce0b-0cad-4712-8c00-e57377eef994.jpg", rendered)
        self.assertEqual(len(used), 1)

    def test_sequence_rules_accept_valid_long_form_and_invite_paths(self):
        long_form = create_composition_plan(
            self.scaffold,
            approved_selection(["H-02", "HR-01", "B-04", "S-01"]),
        )
        self.assertEqual(long_form["selected_module_codes"][-1], "S-01")
        invite = create_composition_plan(
            self.scaffold,
            approved_selection(["H-03", "B-03"]),
        )
        self.assertEqual(invite["compatibility"]["hero_count"], 0)

    def test_refined_catalog_writes_module_and_sequence_galleries(self):
        sequences = build_sequence_configurations(build_module_catalog(self.scaffold))
        self.assertEqual(sequences["option_count"], 9)
        self.assertEqual(
            [option["id"] for option in sequences["options"]],
            [
                "SEQ-LF-01",
                "SEQ-LF-02",
                "SEQ-LF-03",
                "SEQ-LF-04",
                "SEQ-LF-05",
                "SEQ-LF-06",
                "SEQ-LF-07",
                "SEQ-IN-01",
                "SEQ-IN-02",
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            artifacts = write_catalog_artifacts(self.scaffold, Path(tmp))
            self.assertTrue(artifacts["module_gallery"].is_file())
            self.assertTrue(artifacts["sequence_gallery"].is_file())
            self.assertTrue((artifacts["sequence_configuration_dir"] / "SEQ-IN-02.html").is_file())
            self.assertIn("SEQ-LF-04", artifacts["sequence_gallery"].read_text())
            generated_html = "".join(
                path.read_text(encoding="utf-8")
                for path in Path(tmp).rglob("*.html")
            )
            self.assertNotIn("START - ", generated_html)
            self.assertNotIn("END - ", generated_html)

    def test_sequence_rules_reject_bad_order_and_multiple_static_messages(self):
        with self.assertRaisesRegex(CompositionError, "cannot precede"):
            create_composition_plan(
                self.scaffold,
                approved_selection(["H-02", "HR-01", "S-01", "B-04"]),
            )
        with self.assertRaisesRegex(CompositionError, "rider-static-message"):
            create_composition_plan(
                self.scaffold,
                approved_selection(["H-02", "HR-01", "B-04", "S-01", "S-02"]),
            )


def approved_selection(codes):
    return {
        "plan_id": "phase16-unit-test",
        "status": "approved",
        "approved_by": "unit test",
        "approved_at": "2026-10-04",
        "representative_variant": "branded",
        "selected_module_codes": codes,
        "static_block_decisions": [
            {"code": code, "decision": "include" if code in codes else "exclude"}
            for code in ("S-01", "S-02", "S-04")
        ],
    }


def sample_slot(kind, module_id, slot_name):
    if kind in {"text", "safe_rich_text"}:
        return {"kind": kind, "value": "Approved text"}
    if kind == "url":
        return {"kind": "url", "href": "https://example.com"}
    if kind == "image":
        return {
            "kind": "image",
            "src": f"https://example.com/{module_id}-{slot_name}.jpg",
            "alt": "Approved campaign image",
        }
    if kind == "text_list":
        return {"kind": "text_list", "items": ["First item", "Second item"]}
    if kind == "amplified_list":
        return {
            "kind": "amplified_list",
            "items": [
                {"term": "First term", "amplification": "First explanation"},
                {"term": "Second term", "amplification": "Second explanation"},
            ],
        }
    raise AssertionError(f"Unsupported test slot kind: {kind}")


if __name__ == "__main__":
    unittest.main()
