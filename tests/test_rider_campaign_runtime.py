import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.rider_campaign_runtime.composition import create_composition_plan
from tools.rider_campaign_runtime.copy_allocation import CopyAllocationError
from tools.rider_campaign_runtime.agents import load_agents
from tools.rider_campaign_runtime.assets import package_documents, rewrite_and_package_assets
from tools.rider_campaign_runtime.runtime import (
    ROOT,
    RuntimeError,
    _effective_build_plan,
    _resolve_path,
    _validate_static_rendering,
    build_campaign_from_spec,
)
from tools.rider_campaign_runtime.schema import CampaignSpecError, validate_campaign_spec
from tools.rider_campaign_runtime.scaffold import catalog, load_scaffold, module_rows
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

    def test_requires_explicit_static_block_decisions(self):
        spec = minimal_spec()
        del spec["static_blocks"]
        with self.assertRaisesRegex(CampaignSpecError, "static_blocks"):
            validate_campaign_spec(spec)

    def test_requires_explicit_build_mode_contract(self):
        spec = minimal_spec()
        del spec["build"]
        with self.assertRaisesRegex(CampaignSpecError, "build"):
            validate_campaign_spec(spec)

    def test_rejects_invalid_build_mode_policy_combinations(self):
        spec = minimal_spec()
        spec["build"]["mode"] = "composition-preview"
        spec["build"]["variant_policy"] = "all"
        with self.assertRaisesRegex(CampaignSpecError, "composition-preview requires"):
            validate_campaign_spec(spec)

        spec = minimal_spec()
        spec["build"]["mode"] = "release-build"
        spec["build"]["variant_policy"] = "single"
        with self.assertRaisesRegex(CampaignSpecError, "release-build requires"):
            validate_campaign_spec(spec)

        spec = minimal_spec()
        spec["build"] = {
            "mode": "smoke-test",
            "variant_policy": "changed-surface-expanded",
            "changed_surfaces": ["unknown"],
        }
        with self.assertRaisesRegex(CampaignSpecError, "unknown value"):
            validate_campaign_spec(spec)

        spec = minimal_spec()
        spec["build"] = {
            "mode": "smoke-test",
            "variant_policy": "changed-surface-expanded",
            "changed_surfaces": [],
        }
        with self.assertRaisesRegex(CampaignSpecError, "requires at least one"):
            validate_campaign_spec(spec)

    def test_accepts_selected_hero_configuration_in_composition_contract(self):
        spec = minimal_spec()
        spec["composition"] = {
            "plan_version": "1.0",
            "plan_id": "cfg-05-schema-regression",
            "status": "approved",
            "approved_by": "unit test",
            "approved_at": "2026-10-03",
            "representative_variant": "branded",
            "selected_module_codes": ["H-01", "AI-01"],
            "selected_hero_configuration": "CFG-05",
            "static_block_decisions": [],
        }
        validate_campaign_spec(spec)


class RiderCampaignSlotTests(unittest.TestCase):
    def test_safe_rich_text_allows_small_formatting_vocabulary(self):
        self.assertEqual(safe_rich_text("A<br><strong>B</strong>"), "A<br><strong>B</strong>")
        with self.assertRaisesRegex(SlotError, "not allowed"):
            safe_rich_text("<script>alert(1)</script>")

    def test_long_form_body_exposes_distinct_primary_and_secondary_copy_slots(self):
        scaffold = load_scaffold(
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.canonical.html",
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.slot-map.json",
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.module-metadata.json",
        )
        html, _ = apply_module_slots(
            "body-long-form",
            "".join(module_rows(scaffold, "body-long-form")),
            scaffold.slot_map["body-long-form"],
            {
                "body_copy_primary": {"kind": "text", "value": "PRIMARY CAMPAIGN MESSAGE"},
                "body_copy_secondary": {"kind": "text", "value": "SECONDARY CAMPAIGN MESSAGE"},
            },
            manifest_assets={},
        )
        self.assertEqual(html.count("PRIMARY CAMPAIGN MESSAGE"), 1)
        self.assertEqual(html.count("SECONDARY CAMPAIGN MESSAGE"), 1)

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

    def test_image_slot_escapes_query_string_once(self):
        rendered, _ = apply_module_slots(
            "TEST",
            '<img src="old.jpg">',
            {"image": [{"operation": "replace_image_src", "anchor": "old.jpg"}]},
            {
                "image": {
                    "kind": "image",
                    "src": "https://example.com/image.jpg?token=1&raw=1",
                }
            },
            manifest_assets={},
        )
        self.assertIn("token=1&amp;raw=1", rendered)
        self.assertNotIn("&amp;amp;", rendered)

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
            refresh_copy_allocation(spec)
            with self.assertRaisesRegex(RuntimeError, "Refusing to replace non-runtime"):
                build_campaign_from_spec(spec, base_dir=tmp_path)
            self.assertTrue((protected / "keep.txt").is_file())

    def test_build_plan_defaults_to_branded_representative(self):
        spec = minimal_spec()
        spec["variants"] = {"branded": True, "outside_broker": True, "agents": "all"}
        plan = _effective_build_plan(spec)
        self.assertEqual(plan["variants"], {"branded": True, "outside_broker": False, "agents": []})
        self.assertEqual(plan["metadata"]["mode"], "smoke-test")
        self.assertEqual(plan["metadata"]["representative_variant"], "branded")
        self.assertEqual(plan["metadata"]["variant_scope"], "single")

    def test_build_plan_allows_explicit_outside_broker_representative(self):
        spec = minimal_spec()
        spec["build"]["mode"] = "composition-preview"
        spec["build"]["representative_variant"] = "outside-broker-customizable"
        spec["build"]["variant_policy"] = "single"
        spec["variants"] = {"branded": True, "outside_broker": True, "agents": "all"}
        plan = _effective_build_plan(spec)
        self.assertEqual(plan["variants"], {"branded": False, "outside_broker": True, "agents": []})
        self.assertEqual(plan["metadata"]["mode"], "composition-preview")

    def test_build_plan_allows_explicit_agent_representative(self):
        spec = minimal_spec()
        spec["build"]["representative_variant"] = "agent-diana-kosov"
        spec["variants"] = {"branded": True, "outside_broker": True, "agents": "all"}
        plan = _effective_build_plan(spec)
        self.assertEqual(plan["variants"], {"branded": False, "outside_broker": False, "agents": ["diana-kosov"]})

    def test_build_plan_rejects_unauthorized_representative(self):
        spec = minimal_spec()
        spec["build"]["representative_variant"] = "outside-broker-customizable"
        spec["variants"] = {"branded": True, "outside_broker": False, "agents": []}
        with self.assertRaisesRegex(RuntimeError, "not authorized"):
            _effective_build_plan(spec)

    def test_smoke_changed_surface_expands_to_full_authorized_set(self):
        spec = minimal_spec()
        spec["build"] = {
            "mode": "smoke-test",
            "representative_variant": "branded",
            "variant_policy": "changed-surface-expanded",
            "changed_surfaces": ["agent-roster", "footer-renderer"],
        }
        spec["variants"] = {"branded": True, "outside_broker": True, "agents": "all"}
        plan = _effective_build_plan(spec)
        self.assertEqual(plan["variants"], {"branded": True, "outside_broker": True, "agents": "all"})
        self.assertEqual(plan["metadata"]["variant_scope"], "all")
        self.assertIn("agent-roster", plan["metadata"]["expansion_reason"])

    def test_release_build_requires_full_internal_authorized_set(self):
        spec = minimal_spec()
        spec["build"] = {"mode": "release-build", "variant_policy": "all"}
        spec["variants"] = {"branded": True, "outside_broker": True, "agents": []}
        with self.assertRaisesRegex(RuntimeError, "full authorized internal"):
            _effective_build_plan(spec)

    def test_failed_asset_download_preserves_last_passing_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            asset = tmp_path / "pixel.png"
            asset.write_bytes(b"image")
            spec = minimal_spec()
            spec["campaign"]["output_dir"] = str(tmp_path / "campaign-output")
            spec["manifest"]["path"] = str(write_manifest(tmp_path, asset))
            refresh_copy_allocation(spec)

            with patch(
                "tools.rider_campaign_runtime.assets._read_asset",
                return_value=(b"valid-image", "asset.png"),
            ):
                first = build_campaign_from_spec(spec, base_dir=tmp_path)

            sentinel = first.package_dir / "last-passing-package.txt"
            sentinel.write_text("preserve me", encoding="utf-8")
            first_html = next(iter(first.html_files.values())).read_bytes()

            with patch(
                "tools.rider_campaign_runtime.assets._read_asset",
                side_effect=OSError("simulated download failure"),
            ):
                with self.assertRaisesRegex(OSError, "simulated download failure"):
                    build_campaign_from_spec(spec, base_dir=tmp_path)

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve me")
            self.assertEqual(next(iter(first.html_files.values())).read_bytes(), first_html)

            first_zip = first.zip_path.read_bytes()
            spec["campaign"]["subject"] = "Unapproved replacement subject"
            with patch("tools.rider_campaign_runtime.assets._read_asset") as read_asset:
                with self.assertRaisesRegex(CopyAllocationError, "does not match"):
                    build_campaign_from_spec(spec, base_dir=tmp_path)
                read_asset.assert_not_called()
            self.assertEqual(next(iter(first.html_files.values())).read_bytes(), first_html)
            self.assertEqual(first.zip_path.read_bytes(), first_zip)

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
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.module-metadata.json",
        )
        modules = catalog(scaffold)
        self.assertEqual(len(modules), 21)
        self.assertEqual(modules["footer-branded"], (74, 75, 76, 77, 78, 79, 80, 81))
        self.assertEqual(modules["static-authority"], (55,))
        self.assertEqual(modules["static-design"], (58,))
        self.assertEqual(modules["static-opportunity"], (68,))
        self.assertEqual(
            modules["body-long-form"],
            (38, 39, 40, 42, 45, 48, 51),
        )
        self.assertNotIn("#55ebb9", "".join(scaffold.rows[number - 1].html for number in modules["footer-branded"]))
        self.assertEqual(scaffold.metadata["hero-header-full-width"].kind, "hero")
        self.assertTrue(scaffold.metadata["hero-header-full-width"].includes_header)
        self.assertTrue(scaffold.metadata["static-authority"].locked)

    def test_static_block_decisions_must_match_ordered_modules(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            asset = tmp_path / "pixel.png"
            asset.write_bytes(b"image")
            spec = minimal_spec()
            spec["campaign"]["output_dir"] = str(tmp_path / "campaign-output")
            spec["manifest"]["path"] = str(write_manifest(tmp_path, asset))
            spec["static_blocks"][0]["decision"] = "include"
            refresh_copy_allocation(spec)
            with self.assertRaisesRegex(RuntimeError, "missing from modules"):
                build_campaign_from_spec(spec, base_dir=tmp_path)

    def test_static_lock_rejects_mutated_content_before_asset_rewrite(self):
        decisions = [{"id": "static-authority", "decision": "include"}]
        with self.assertRaisesRegex(RuntimeError, "Static block lock failed"):
            _validate_static_rendering(
                decisions,
                {"static-authority": "<table>Locked copy</table>"},
                {"branded": "<table>Changed copy</table>"},
            )

    def test_rejects_standalone_header_with_header_bearing_hero(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            asset = tmp_path / "pixel.png"
            asset.write_bytes(b"image")
            spec = minimal_spec()
            spec["campaign"]["output_dir"] = str(tmp_path / "campaign-output")
            spec["manifest"]["path"] = str(write_manifest(tmp_path, asset))
            spec["modules"].insert(0, {"id": "header-one-column-dark", "slots": {}})
            refresh_copy_allocation(spec)
            with self.assertRaisesRegex(RuntimeError, "incompatible"):
                build_campaign_from_spec(spec, base_dir=tmp_path)

    def test_agent_loader_rejects_diego_reference_for_footer(self):
        manifest = [
            {
                "filename": "angelica.jpg",
                "dropbox_id": "id:31E0v0XEN2IAAAAAAAABkQ",
                "dropbox_path": "/20. people/diego ojeda/angelica.jpg",
                "category": ["people", "developer", "likeness-reference"],
                "orientation": "",
                "approved_for": ["image-generation-reference"],
                "public_url": "https://example.com/angelica.jpg",
                "media_type": "image",
                "stable_identity": "id:id:31E0v0XEN2IAAAAAAAABkQ",
            }
        ]
        with self.assertRaisesRegex(ValueError, "not approved for agent-footer"):
            load_agents(
                ROOT / "projects/the-rider/skills/onbrand-the-rider-email/data/agents",
                manifest,
                ["angelica-cruz"],
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
                    "id": "header-two-column-dark",
                    "slots": {
                        "headline": {"kind": "text", "value": "Internal Sample Headline"},
                        "logo_link": {"kind": "url", "href": "https://theriderresidences.com"},
                    },
                },
                {
                    "id": "hero-ai-generated",
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
            refresh_copy_allocation(spec)
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

    def test_composition_preview_build_renders_one_representative_variant(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            asset = write_png(tmp_path / "pixel.png")
            spec = minimal_spec()
            spec["build"] = {
                "mode": "composition-preview",
                "representative_variant": "outside-broker-customizable",
                "variant_policy": "single",
            }
            spec["variants"] = {"branded": True, "outside_broker": True, "agents": "all"}
            spec["campaign"]["output_dir"] = str(tmp_path / "campaign-output")
            spec["manifest"]["path"] = str(write_manifest(tmp_path, asset))
            spec["composition"] = approved_composition(
                selected_codes=["HH-01", "B-04"],
                representative_variant="outside-broker-customizable",
            )
            refresh_copy_allocation(spec)
            with patch("tools.rider_campaign_runtime.assets._read_asset") as read_asset:
                read_asset.side_effect = lambda source: (asset.read_bytes(), Path(source).name or "asset.png")
                result = build_campaign_from_spec(spec, base_dir=tmp_path)
            self.assertEqual(set(result.html_files), {"outside-broker-customizable"})
            metadata = json.loads((result.package_dir / "campaign-metadata.json").read_text())
            self.assertEqual(metadata["build"]["mode"], "composition-preview")
            self.assertEqual(metadata["build"]["variant_scope"], "single")
            self.assertEqual(metadata["build"]["rendered_variants"], ["outside-broker-customizable"])
            qa = json.loads(result.qa_report.read_text())
            self.assertEqual(qa["build"], metadata["build"])
            self.assertEqual(qa["copy_allocation"], metadata["copy_allocation"])
            self.assertEqual(qa["copy_allocation"]["content_units"], spec["copy_allocation"]["content_units"])

    def test_smoke_build_policy_all_renders_full_authorized_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            asset = write_png(tmp_path / "pixel.png")
            spec = release_spec(tmp_path, asset)
            spec["build"] = {
                "mode": "smoke-test",
                "representative_variant": "branded",
                "variant_policy": "all",
            }
            with patch("tools.rider_campaign_runtime.assets._read_asset") as read_asset:
                read_asset.side_effect = lambda source: (asset.read_bytes(), Path(source).name or "asset.png")
                result = build_campaign_from_spec(spec, base_dir=tmp_path)
            self.assertEqual(len(result.html_files), 9)
            metadata = json.loads((result.package_dir / "campaign-metadata.json").read_text())
            self.assertEqual(metadata["build"]["mode"], "smoke-test")
            self.assertEqual(metadata["build"]["variant_policy"], "all")
            self.assertEqual(metadata["build"]["variant_scope"], "all")

    def test_release_build_renders_full_current_internal_matrix(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            asset = write_png(tmp_path / "pixel.png")
            spec = release_spec(tmp_path, asset)
            with patch("tools.rider_campaign_runtime.assets._read_asset") as read_asset:
                read_asset.side_effect = lambda source: (asset.read_bytes(), Path(source).name or "asset.png")
                result = build_campaign_from_spec(spec, base_dir=tmp_path)
            self.assertTrue(result.qa.passed)
            self.assertTrue(result.zip_path.is_file())
            self.assertEqual(len(result.html_files), 9)
            self.assertIn("branded", result.html_files)
            self.assertIn("outside-broker-customizable", result.html_files)
            self.assertIn("agent-diana-kosov", result.html_files)
            self.assertNotIn("agent-jake-lecce", result.html_files)
            self.assertEqual(sum(1 for name in result.html_files if name.startswith("agent-")), 7)
            metadata = json.loads((result.package_dir / "campaign-metadata.json").read_text())
            self.assertEqual(metadata["build"]["mode"], "release-build")
            self.assertEqual(metadata["build"]["variant_policy"], "all")
            self.assertEqual(metadata["build"]["variant_scope"], "all")
            self.assertEqual(set(metadata["build"]["rendered_variants"]), set(result.html_files))

    def test_relative_local_image_slot_is_packaged_for_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "assets").mkdir()
            asset = tmp_path / "assets" / "local-hero.png"
            asset.write_bytes(
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
                b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
                b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            spec = minimal_spec()
            spec["campaign"]["output_dir"] = str(tmp_path / "campaign-output")
            spec["manifest"]["path"] = str(write_manifest(tmp_path, asset))
            spec["modules"][0]["slots"] = {
                "headline": {"kind": "text", "value": "Local hero headline"},
                "background_image": {
                    "kind": "image",
                    "src": "assets/local-hero.png",
                    "alt": "Local generated hero",
                    "role": "hero",
                }
            }
            refresh_copy_allocation(spec)
            with patch("tools.rider_campaign_runtime.assets._read_asset") as read_asset:
                read_asset.side_effect = lambda source: (asset.read_bytes(), Path(source).name or "asset.png")
                result = build_campaign_from_spec(spec, base_dir=tmp_path)
            html = next(iter(result.html_files.values())).read_text()
            self.assertTrue(result.qa.passed)
            self.assertIn("../images/local-hero-", html)
            self.assertNotIn(str(tmp_path), html)

    def test_wellness_smoke_fixture_schema_and_static_choices(self):
        fixture = ROOT / "projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-smoke.runtime.json"
        spec = json.loads(fixture.read_text(encoding="utf-8"))
        validate_campaign_spec(spec)
        self.assertEqual(spec["campaign"]["slug"], "rider-wellness-smoke")
        self.assertEqual(
            [module["id"] for module in spec["modules"]],
            [
                "header-two-column-dark",
                "hero-ai-generated",
                "body-long-form",
                "static-authority",
                "static-design",
                "pre-footer-cta",
            ],
        )
        self.assertEqual(
            {item["id"]: item["decision"] for item in spec["static_blocks"]},
            {
                "static-authority": "include",
                "static-design": "include",
                "static-opportunity": "exclude",
            },
        )
        self.assertEqual(
            spec["build"],
            {"mode": "smoke-test", "representative_variant": "branded", "variant_policy": "single"},
        )
        self.assertEqual(spec["variants"], {"branded": True, "outside_broker": True, "agents": "all"})
        self.assertEqual(
            spec["modules"][2]["slots"]["inline_image_primary"]["asset_id"],
            "id:31E0v0XEN2IAAAAAAAAAIA",
        )

    def test_release_build_fixture_declares_full_matrix(self):
        fixture = ROOT / "projects/the-rider/skills/onbrand-the-rider-email/examples/release-build.runtime.json"
        spec = json.loads(fixture.read_text(encoding="utf-8"))
        validate_campaign_spec(spec)
        self.assertEqual(spec["campaign"]["slug"], "rider-runtime-release-build")
        self.assertEqual(spec["build"], {"mode": "release-build", "variant_policy": "all"})
        self.assertEqual(spec["variants"], {"branded": True, "outside_broker": True, "agents": "all"})


def minimal_spec():
    return {
        "schema_version": "1.0",
        "build": {
            "mode": "smoke-test",
            "representative_variant": "branded",
            "variant_policy": "single",
        },
        "campaign": {
            "slug": "runtime-test",
            "title": "Runtime Test",
            "output_dir": "campaign-output/runtime-test",
            "subject": "Internal runtime test",
        },
        "copy_allocation": {
            "version": "1.0",
            "plan_id": "unit-test-copy-allocation",
            "status": "approved",
            "approved_by": "unit test",
            "approved_at": "2026-10-03",
            "content_units": [
                {
                    "id": "meta-subject",
                    "text": "Internal runtime test",
                    "content_role": "subject",
                    "source": "unit-test",
                    "approval_status": "approved",
                    "owner": {"channel": "metadata", "metadata_field": "subject"},
                    "reuse_policy": "single-use",
                    "max_occurrences": 1,
                    "claim_policy": "none",
                }
            ],
        },
        "manifest": {"path": "manifest.json"},
        "modules": [
            {
                "id": "hero-header-full-width",
                "slots": {
                    "headline": {"kind": "text", "value": "Internal Sample Headline"},
                    "background_image": {
                        "kind": "image",
                        "asset_id": "id:runtime-hero",
                        "alt": "Internal runtime hero",
                        "role": "hero",
                    },
                },
            },
            {
                "id": "body-long-form",
                "slots": {
                    "body_copy_primary": {
                        "kind": "text",
                        "value": "A concise approved body message.",
                    }
                },
            },
        ],
        "static_blocks": [
            {"id": "static-authority", "decision": "exclude"},
            {"id": "static-design", "decision": "exclude"},
            {"id": "static-opportunity", "decision": "exclude"}
        ],
        "variants": {"branded": True, "outside_broker": False, "agents": []},
        "deployment": {"asset_mode": "relative-review"},
    }


def release_spec(tmp_path, asset):
    spec = minimal_spec()
    spec["build"] = {"mode": "release-build", "variant_policy": "all"}
    spec["campaign"]["output_dir"] = str(tmp_path / "campaign-output")
    spec["manifest"]["path"] = str(write_manifest(tmp_path, asset))
    spec["variants"] = {"branded": True, "outside_broker": True, "agents": "all"}
    spec["composition"] = approved_composition(selected_codes=["HH-01", "B-04"])
    spec["outside_broker"] = {
        "name": "[OUTSIDE BROKER NAME]",
        "title": "[OUTSIDE BROKER TITLE]",
        "phone": "[OUTSIDE BROKER PHONE]",
        "email": "[OUTSIDE BROKER EMAIL]",
        "social": "[OUTSIDE BROKER SOCIAL]",
    }
    refresh_copy_allocation(spec)
    return spec


def refresh_copy_allocation(spec):
    units = []
    for field in ("subject", "preview_text"):
        value = spec.get("campaign", {}).get(field, "")
        if value:
            units.append(
                {
                    "id": f"meta-{field.replace('_', '-')}",
                    "text": value,
                    "content_role": field,
                    "source": "unit-test",
                    "approval_status": "approved",
                    "owner": {"channel": "metadata", "metadata_field": field},
                    "reuse_policy": "single-use",
                    "max_occurrences": 1,
                    "claim_policy": "none",
                }
            )
    for module in spec.get("modules", []):
        for slot_name, slot in module.get("slots", {}).items():
            if slot.get("kind") in {"text", "safe_rich_text"}:
                units.append(
                    {
                        "id": f"{module['id'].lower().replace(' ', '-').replace('&', 'and')}-{slot_name}",
                        "text": slot["value"],
                        "content_role": slot_name,
                        "source": "unit-test",
                        "approval_status": "approved",
                        "owner": {"channel": "live-html", "module_id": module["id"], "slot": slot_name},
                        "reuse_policy": "single-use",
                        "max_occurrences": 1,
                        "claim_policy": "none",
                    }
                )
            if slot.get("kind") == "image" and slot.get("alt"):
                units.append(
                    {
                        "id": f"{module['id'].lower().replace(' ', '-').replace('&', 'and')}-{slot_name}-alt",
                        "text": slot["alt"],
                        "content_role": "image-alt",
                        "source": "unit-test",
                        "approval_status": "approved",
                        "owner": {
                            "channel": "alt-text",
                            "module_id": module["id"],
                            "slot": slot_name,
                            **({"image_workflow_id": slot["image_workflow_id"]} if "image_workflow_id" in slot else {}),
                        },
                        "reuse_policy": "single-use",
                        "max_occurrences": 1,
                        "claim_policy": "none",
                    }
                )
    spec["copy_allocation"] = {
        "version": "1.0",
        "plan_id": "unit-test-copy-allocation",
        "status": "approved",
        "approved_by": "unit test",
        "approved_at": "2026-10-03",
        "content_units": units,
    }


def approved_composition(*, selected_codes, representative_variant="branded"):
    static_decisions = [
        {"code": "S-01", "decision": "include" if "S-01" in selected_codes else "exclude"},
        {"code": "S-02", "decision": "include" if "S-02" in selected_codes else "exclude"},
        {"code": "S-04", "decision": "include" if "S-04" in selected_codes else "exclude"},
    ]
    return create_composition_plan(
        load_scaffold(
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.canonical.html",
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.slot-map.json",
            ROOT / "projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.module-metadata.json",
        ),
        {
            "plan_id": "unit-test-composition",
            "status": "approved",
            "approved_by": "unit test",
            "approved_at": "2026-10-03",
            "representative_variant": representative_variant,
            "selected_module_codes": selected_codes,
            "static_block_decisions": static_decisions,
        },
    )


def write_png(path):
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return path


def write_manifest(tmp_path, asset_path):
    manifest = tmp_path / "manifest.json"
    records = []
    agent_ids = {
        "paulie-hankin-headshot.jpeg": "id:31E0v0XEN2IAAAAAAAABlQ",
        "angelica-cruz-headshot.jpeg": "id:31E0v0XEN2IAAAAAAAABkQ",
        "diana-kosov-headshot.jpeg": "id:31E0v0XEN2IAAAAAAAABlg",
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
