import json
from pathlib import Path
import tempfile
import unittest

from tools.rider_campaign_runtime.composition import (
    CompositionError,
    build_hero_configurations,
    build_module_catalog,
    create_composition_plan,
    validate_composition_contract,
    write_catalog_artifacts,
)
from tools.rider_campaign_runtime.runtime import ROOT
from tools.rider_campaign_runtime.scaffold import load_scaffold


class RiderCompositionTests(unittest.TestCase):
    def setUp(self):
        self.scaffold = load_scaffold(
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.canonical.html",
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.slot-map.json",
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.module-metadata.json",
        )

    def test_catalog_uses_stable_codes_and_excludes_footers(self):
        catalog = build_module_catalog(self.scaffold)
        entries = {entry["code"]: entry for entry in catalog["entries"]}
        self.assertEqual(len(entries), 18)
        self.assertEqual(entries["H-01"]["scaffold_module_id"], "header-two-column-dark")
        self.assertEqual(entries["AI-01"]["scaffold_module_id"], "hero-ai-generated")
        self.assertEqual(entries["HR-01"]["scaffold_module_id"], "hero-dark-framed")
        self.assertEqual(entries["HH-01"]["scaffold_module_id"], "hero-header-full-width")
        self.assertEqual(entries["S-04"]["scaffold_module_id"], "static-opportunity")
        self.assertNotIn("BRANDED FOOTER", {entry["scaffold_module_id"] for entry in entries.values()})
        self.assertTrue(entries["HH-01"]["includes_header"])
        self.assertTrue(entries["HR-01"]["image_required"])
        self.assertTrue(entries["HR-01"]["live_text_support"])

    def test_catalog_artifacts_include_review_and_isolated_previews(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifacts = write_catalog_artifacts(self.scaffold, Path(tmp))
            catalog = json.loads(artifacts["catalog"].read_text())
            self.assertEqual(catalog["catalog_version"], "1.0")
            self.assertTrue(artifacts["review"].is_file())
            self.assertTrue((artifacts["preview_dir"] / "HH-01.html").is_file())
            self.assertIn("Design Proof", artifacts["review"].read_text())
            self.assertTrue(artifacts["hero_gallery"].is_file())
            self.assertTrue((artifacts["hero_configuration_dir"] / "CFG-01.html").is_file())
            configurations = json.loads(artifacts["hero_configurations"].read_text())
            self.assertEqual(configurations["option_count"], 14)
            self.assertIn("CFG-01", artifacts["hero_gallery"].read_text())

    def test_labeled_gallery_contains_only_compatible_complete_configurations(self):
        catalog = build_module_catalog(self.scaffold)
        configurations = build_hero_configurations(catalog)
        entries = {entry["code"]: entry for entry in catalog["entries"]}
        self.assertEqual(configurations["gallery_version"], "1.0")
        self.assertEqual(len(configurations["options"]), 14)
        for option in configurations["options"]:
            selected = [entries[code] for code in option["selected_module_codes"]]
            self.assertEqual(sum(entry["module_type"] == "hero" for entry in selected), 1)
            self.assertLessEqual(sum(entry["module_type"] == "header" for entry in selected), 1)
            if selected[-1]["includes_header"]:
                self.assertEqual(len(selected), 1)
            self.assertTrue(option["label"])
            self.assertTrue(option["group_label"])
            self.assertTrue(option["preview_path"].endswith(f"{option['id']}.html"))

    def test_create_plan_records_slots_assets_and_compatibility(self):
        selection = approved_selection(["H-02", "HR-01", "B-04", "S-01"])
        selection["selected_hero_configuration"] = "CFG-09"
        plan = create_composition_plan(self.scaffold, selection)
        self.assertEqual(plan["status"], "approved")
        self.assertEqual(plan["compatibility"]["standalone_header_count"], 1)
        self.assertEqual(plan["compatibility"]["hero_count"], 1)
        self.assertIn("image-generation", plan["approval_required_before"])
        self.assertIn("background_image", {asset["slot"] for asset in plan["required_assets"]})
        self.assertIn("headline", {slot["slot"] for slot in plan["editable_slots"]})
        self.assertEqual(plan["selected_hero_configuration"], "CFG-09")

    def test_plan_rejects_configuration_that_does_not_match_selected_codes(self):
        selection = approved_selection(["H-02", "HR-01", "B-04"])
        selection["selected_hero_configuration"] = "CFG-01"
        with self.assertRaisesRegex(CompositionError, "requires module codes"):
            create_composition_plan(self.scaffold, selection)

    def test_plan_rejects_header_with_header_bearing_hero(self):
        with self.assertRaisesRegex(CompositionError, "incompatible"):
            create_composition_plan(self.scaffold, approved_selection(["H-01", "HH-01"]))

    def test_plan_rejects_static_selection_without_include_decision(self):
        selection = approved_selection(["HH-01", "S-01"])
        for item in selection["static_block_decisions"]:
            if item["code"] == "S-01":
                item["decision"] = "exclude"
        with self.assertRaisesRegex(CompositionError, "Selected static block"):
            create_composition_plan(self.scaffold, selection)

    def test_runtime_contract_rejects_missing_approval_for_release(self):
        spec = {
            "build": {"mode": "release-build", "variant_policy": "all"},
            "modules": [{"id": "hero-header-full-width", "slots": {}}],
            "static_blocks": [
                {"id": "static-authority", "decision": "exclude"},
                {"id": "static-design", "decision": "exclude"},
                {"id": "static-opportunity", "decision": "exclude"},
            ],
        }
        with self.assertRaisesRegex(CompositionError, "composition approval is required"):
            validate_composition_contract(spec, self.scaffold)


def approved_selection(selected_codes):
    return {
        "plan_id": "unit-test-composition",
        "status": "approved",
        "approved_by": "unit test",
        "approved_at": "2026-10-03",
        "representative_variant": "branded",
        "selected_module_codes": selected_codes,
        "static_block_decisions": [
            {"code": "S-01", "decision": "include" if "S-01" in selected_codes else "exclude"},
            {"code": "S-02", "decision": "include" if "S-02" in selected_codes else "exclude"},
            {"code": "S-04", "decision": "include" if "S-04" in selected_codes else "exclude"},
        ],
    }


if __name__ == "__main__":
    unittest.main()
