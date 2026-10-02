import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.rider_campaign_runtime.agents import load_agents
from tools.rider_campaign_runtime.assets import package_documents, rewrite_and_package_assets
from tools.rider_campaign_runtime.runtime import ROOT, RuntimeError, _resolve_path, build_campaign_from_spec
from tools.rider_campaign_runtime.schema import CampaignSpecError, validate_campaign_spec
from tools.rider_campaign_runtime.scaffold import catalog, load_scaffold
from tools.rider_campaign_runtime.slots import SlotError, UsedAsset, apply_module_slots, safe_rich_text


class RiderCampaignSchemaTests(unittest.TestCase):
    def test_rejects_unknown_fields_and_invalid_url_combinations(self):
        spec = minimal_spec()
        spec["extra"] = True
        with self.assertRaisesRegex(CampaignSpecError, "unknown field"):
            validate_campaign_spec(spec)

        spec = minimal_spec()
        spec["outside_broker"] = {"headshot": {"src": "https://example.com/a.jpg", "asset_id": "id:1"}}
        with self.assertRaisesRegex(CampaignSpecError, "exactly one"):
            validate_campaign_spec(spec)

    def test_rejects_unsafe_slot_url_scheme(self):
        spec = minimal_spec()
        spec["modules"][0]["slots"] = {"logo_link": {"kind": "url", "href": "javascript:alert(1)"}}
        with self.assertRaisesRegex(CampaignSpecError, "unsupported URL scheme"):
            validate_campaign_spec(spec)


class RiderCampaignSlotTests(unittest.TestCase):
    def test_safe_rich_text_allows_small_formatting_vocabulary(self):
        self.assertEqual(safe_rich_text("A<br><strong>B</strong>"), "A<br><strong>B</strong>")
        with self.assertRaisesRegex(SlotError, "not allowed"):
            safe_rich_text("<script>alert(1)</script>")

    def test_slot_anchor_must_resolve_once(self):
        with self.assertRaisesRegex(SlotError, "exactly once"):
            apply_module_slots(
                "TEST",
                "<p>Same</p><p>Same</p>",
                {"headline": [{"operation": "replace_text", "anchor": "Same"}]},
                {"headline": {"kind": "text", "value": "New"}},
                manifest_assets={},
            )

    def test_manifest_image_slot_requires_declared_approval(self):
        with self.assertRaisesRegex(SlotError, "not approved for hero"):
            apply_module_slots(
                "TEST",
                '<img src="old.jpg">',
                {
                    "hero": [
                        {
                            "operation": "replace_image_src",
                            "anchor": "old.jpg",
                            "required_approval": "hero",
                        }
                    ]
                },
                {"hero": {"kind": "image", "asset_id": "id:reference"}},
                manifest_assets={
                    "id:reference": {
                        "dropbox_id": "id:reference",
                        "dropbox_path": "/20. People/Diego Ojeda/reference.jpg",
                        "filename": "reference.jpg",
                        "media_type": "image",
                        "approved_for": ["image-generation-reference"],
                        "public_url": "https://example.com/reference.jpg",
                    }
                },
            )

    def test_contextual_text_rules_can_update_distinct_repeated_labels(self):
        rendered, _ = apply_module_slots(
            "TEST",
            '<span class="wide">Same</span><span class="narrow">Same</span>',
            {
                "cta": [
                    {
                        "operation": "replace_text_in_context",
                        "anchor": '<span class="wide">Same</span>',
                        "text_anchor": "Same",
                    },
                    {
                        "operation": "replace_text_in_context",
                        "anchor": '<span class="narrow">Same</span>',
                        "text_anchor": "Same",
                    },
                ]
            },
            {"cta": {"kind": "text", "value": "New"}},
            manifest_assets={},
        )
        self.assertEqual(rendered.count("New"), 2)


class RiderCampaignRuntimeTests(unittest.TestCase):
    def test_repo_relative_paths_resolve_from_repo_root(self):
        self.assertEqual(_resolve_path(Path("/tmp/examples"), "tools/example.json"), ROOT / "tools/example.json")

    def test_runtime_refuses_to_delete_an_unrecognized_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            asset = tmp_path / "pixel.png"
            asset.write_bytes(b"image")
            protected = tmp_path / "campaign-output" / "runtime-test"
            protected.mkdir(parents=True)
            (protected / "keep.txt").write_text("do not delete", encoding="utf-8")
            spec = minimal_spec()
            spec["campaign"]["output_dir"] = str(tmp_path / "campaign-output")
            spec["manifest"]["path"] = str(write_manifest(tmp_path, asset))
            with self.assertRaisesRegex(RuntimeError, "Refusing to replace non-runtime"):
                build_campaign_from_spec(spec, base_dir=tmp_path)
            self.assertTrue((protected / "keep.txt").is_file())

    def test_asset_rewrite_handles_html_escaped_query_strings(self):
        source = "https://example.com/headshot.jpg?token=1&raw=1"
        html = f'<img src="https://example.com/headshot.jpg?token=1&amp;raw=1">'
        with tempfile.TemporaryDirectory() as tmp:
            with patch("tools.rider_campaign_runtime.assets._read_asset", return_value=(b"image", "headshot.jpg")):
                rewritten, packaged = rewrite_and_package_assets(
                    {"agent": html},
                    [("agent", UsedAsset(source=source, role="agent-footer-headshot"))],
                    Path(tmp),
                    asset_mode="relative-review",
                    hosted_asset_base_url=None,
                )
        self.assertIn("../images/headshot-", rewritten["agent"])
        self.assertNotIn("example.com", rewritten["agent"])
        self.assertEqual(len(packaged), 1)

    def test_packages_selected_pdf_with_checksum_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "floor-plan.pdf"
            source.write_bytes(b"%PDF-1.4\nsmoke\n%%EOF\n")
            packaged = package_documents(
                [
                    UsedAsset(
                        source=source.as_uri(),
                        role="floor-plan",
                        identity="id:pdf",
                        filename=source.name,
                        dropbox_path="/Floor Plans/floor-plan.pdf",
                    )
                ],
                tmp_path / "package",
            )
            self.assertEqual(len(packaged), 1)
            self.assertTrue((tmp_path / "package" / packaged[0].package_path).is_file())
            self.assertEqual(packaged[0].identity, "id:pdf")

    def test_slot_map_covers_real_scaffold_catalog_without_marker_rows(self):
        scaffold = load_scaffold(
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.canonical.html",
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.slot-map.json",
        )
        modules = catalog(scaffold)
        self.assertEqual(len(modules), 13)
        self.assertEqual(modules["BRANDED FOOTER"], (62, 63, 64, 65, 66, 67, 68, 69))
        self.assertNotIn("#55ebb9", "".join(scaffold.rows[number - 1].html for number in modules["BRANDED FOOTER"]))

    def test_agent_loader_rejects_diego_reference_for_footer(self):
        manifest = [
            {
                "filename": "jake.jpg",
                "dropbox_id": "id:31E0v0XEN2IAAAAAAAABjw",
                "dropbox_path": "/20. people/diego ojeda/jake.jpg",
                "category": ["people", "developer", "likeness-reference"],
                "orientation": "",
                "approved_for": ["image-generation-reference"],
                "public_url": "https://example.com/jake.jpg",
                "media_type": "image",
                "stable_identity": "id:id:31E0v0XEN2IAAAAAAAABjw",
            }
        ]
        with self.assertRaisesRegex(ValueError, "not approved for agent-footer"):
            load_agents(
                ROOT / "projects/the-rider/skills/onbrand-the-rider-email/data/agents",
                manifest,
                ["jake-lecce"],
            )

    def test_builds_review_package_with_synthetic_file_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            asset = tmp_path / "pixel.png"
            asset.write_bytes(
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
                b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
                b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            spec = minimal_spec()
            spec["campaign"]["output_dir"] = str(tmp_path / "campaign-output")
            spec["manifest"]["path"] = str(write_manifest(tmp_path, asset))
            spec["modules"] = [
                {
                    "id": "TWO-COLUMN HEADER",
                    "slots": {
                        "headline": {"kind": "text", "value": "Internal Sample Headline"},
                        "logo_link": {"kind": "url", "href": "https://theriderresidences.com"},
                    },
                },
                {
                    "id": "AI GENERATED IMAGE BASED ON PROMPT",
                    "slots": {
                        "hero_image": {
                            "kind": "image",
                            "asset_id": "id:runtime-hero",
                            "alt": "Internal smoke placeholder",
                            "role": "hero",
                        }
                    },
                },
            ]
            spec["variants"] = {"branded": True, "outside_broker": False, "agents": []}
            with patch("tools.rider_campaign_runtime.assets._read_asset") as read_asset:
                read_asset.side_effect = lambda source: (asset.read_bytes(), Path(source).name or "asset.png")
                result = build_campaign_from_spec(spec, base_dir=tmp_path)
            self.assertTrue(result.qa.passed)
            self.assertTrue(result.zip_path.is_file())
            self.assertTrue((result.package_dir / "campaign-metadata.json").is_file())
            html = next(iter(result.html_files.values())).read_text()
            self.assertIn("Internal Sample Headline", html)
            self.assertNotIn("START - ", html)
            self.assertIn("../images/", html)


def minimal_spec():
    return {
        "schema_version": "1.0",
        "campaign": {
            "slug": "runtime-test",
            "title": "Runtime Test",
            "output_dir": "campaign-output/runtime-test",
        },
        "manifest": {"path": "manifest.json"},
        "modules": [{"id": "TWO-COLUMN HEADER", "slots": {}}],
        "variants": {"branded": True, "outside_broker": False, "agents": []},
        "deployment": {"asset_mode": "relative-review"},
    }


def write_manifest(tmp_path, asset_path):
    manifest = tmp_path / "manifest.json"
    records = []
    agent_ids = {
        "jake-lecce-headshot.jpg": "id:31E0v0XEN2IAAAAAAAABjw",
        "angelica-cruz-headshot.jpeg": "id:31E0v0XEN2IAAAAAAAABkQ",
        "julian-oliveros-headshot.jpeg": "id:31E0v0XEN2IAAAAAAAABkg",
        "omar-santana-headshot.jpeg": "id:31E0v0XEN2IAAAAAAAABlA",
        "pablo-rodriguez-headshot.jpeg": "id:31E0v0XEN2IAAAAAAAABkA",
        "yessika-arevalo-headshot.jpeg": "id:31E0v0XEN2IAAAAAAAABkw",
    }
    for filename, asset_id in agent_ids.items():
        records.append(
            {
                "filename": filename,
                "dropbox_id": asset_id,
                "dropbox_path": f"/20. people/in-house agents/{filename}",
                "category": ["people", "in-house-agent", "headshot"],
                "orientation": "portrait",
                "approved_for": ["agent-footer"],
                "public_url": asset_path.as_uri(),
            }
        )
    records.append(
        {
            "filename": "runtime-hero.png",
            "dropbox_id": "id:runtime-hero",
            "dropbox_path": "/runtime/hero.png",
            "category": ["runtime", "hero"],
            "orientation": "landscape",
            "approved_for": ["hero"],
            "public_url": asset_path.as_uri(),
        }
    )
    manifest.write_text(json.dumps(records), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    unittest.main()
