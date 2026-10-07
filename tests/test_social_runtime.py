"""Phase 17: social runtime for static posts and carousels."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from tools.platform_adapters.contract import RUNTIMES
from tools.rider_campaign_runtime import copy_allocation as email_copy
from tools.social_runtime import SocialRuntimeError, SocialSpecError, build_social_from_spec
from tools.social_runtime import copy_allocation as social_copy
from tools.social_runtime.assets import broker_safe_assets
from tools.social_runtime.formats import FormatError, load_formats, require_format
from tools.social_runtime.templates import TemplateError, match_slides


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "tools" / "social_runtime"
RIDER_PREVIEW = ROOT / "projects" / "the-rider" / "social" / "examples" / "feature-carousel.preview.json"

ASSETS = (
    ("sq-1.jpg", "square", ["hero"], ["social-post", "social-carousel"]),
    ("sq-2.jpg", "square", ["body"], ["social-post", "social-carousel"]),
    ("sq-3.jpg", "square", ["body"], ["social-post", "social-carousel"]),
    ("wide-1.jpg", "landscape", ["hero"], ["social-crop-source"]),
    ("plain.jpg", "square", ["body"], None),
    ("agent.jpg", "square", ["agent-footer"], None),
)
SLOT_CHANNELS = {"headline": "on-image-text", "body": "slide-text", "action": "on-image-text"}


def _png(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height) + b"\x08\x02\x00\x00\x00"


class SocialRuntimeCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name).resolve()
        self.project = self.base / "project"
        (self.project / "social" / "templates").mkdir(parents=True)
        self.manifest = self.base / "manifest.json"
        records = [
            {
                "filename": name, "dropbox_id": f"id:SECRET{index}XYZ", "dropbox_path": f"/private-folder/{name}",
                "category": ["exterior"], "orientation": orientation, "approved_for": approved,
                "public_url": f"https://cdn.example.com/{name}",
            }
            for index, (name, orientation, approved, _) in enumerate(ASSETS)
        ]
        self.manifest.write_text(json.dumps(records), encoding="utf-8")
        self.overlay = {
            "schema_version": "1.0", "project_slug": "demo", "medium": "social", "approver": "Owner",
            "approved_date": "2026-10-06",
            "role_vocabulary": ["social-post", "social-carousel", "social-crop-source"],
            "never_social_roles": ["agent-footer", "image-generation-reference"],
            "source_manifest": {
                "path": "manifest.json", "record_count": len(records),
                "sha256": hashlib.sha256(self.manifest.read_bytes()).hexdigest(),
            },
            "entries": [
                {"filename": name, "dropbox_id": f"id:SECRET{index}XYZ", "cluster": "demo",
                 "orientation": orientation, "approved_for_social": roles}
                for index, (name, orientation, _, roles) in enumerate(ASSETS) if roles
            ],
            "excluded": [],
        }
        self._write_overlay()
        self.template = json.loads((ROOT / "projects/the-rider/social/templates/CAR-01.json").read_text())
        self.template["approval_status"] = "approved"
        self.template["audiences"] = ["in-house", "outside-broker"]
        self._write_template()
        self.formats = self.base / "formats.json"
        sidecar = load_formats()
        for entry in sidecar["formats"].values():
            entry["verified_date"] = "2026-10-06"
            entry["source"] = "test fixture"
        self.formats.write_text(json.dumps(sidecar), encoding="utf-8")

    def _write_overlay(self):
        (self.project / "asset-approvals.social.json").write_text(json.dumps(self.overlay), encoding="utf-8")

    def _write_template(self):
        (self.project / "social" / "templates" / "CAR-01.json").write_text(json.dumps(self.template), encoding="utf-8")

    def spec(self, **overrides) -> dict:
        slides = [
            {"role": "opener", "image": {"asset": "sq-1.jpg"}, "text": {"headline": "Arrive at the tower"},
             "alt_text": "Tower exterior seen from the street"},
            {"role": "feature", "image": {"asset": "sq-2.jpg"},
             "text": {"headline": "Kitchens built for hosting", "body": "Stone counters and integrated appliances in every plan"},
             "alt_text": "Kitchen with an island and pendant lights"},
            {"role": "call-to-action", "image": {"asset": "sq-3.jpg"},
             "text": {"headline": "See the residences", "action": "Book a private tour"},
             "alt_text": "Tower entrance at dusk"},
        ]
        spec = {
            "schema_version": "1.0", "medium": "social",
            "campaign": {"slug": "demo-carousel", "project": "demo", "output_dir": "out"},
            "audience": "in-house", "build": {"mode": "composition-preview"},
            "composition": {"template": "CAR-01", "format": "carousel-1x1"},
            "slides": slides, "caption": "A closer look at life above the city this season",
            "hashtags": ["#demo", "#carousel"],
            "copy_allocation": {"version": "1.0", "status": "approved", "content_units": []},
        }
        spec.update(overrides)
        return self.allocate(spec)

    def allocate(self, spec: dict) -> dict:
        units = [{"id": "caption", "text": spec["caption"], "owner": {"channel": "caption"}, "approval_status": "approved"}]
        if spec.get("hashtags"):
            units.append({"id": "hashtags", "text": " ".join(spec["hashtags"]), "owner": {"channel": "hashtags"},
                          "approval_status": "approved"})
        for index, slide in enumerate(spec["slides"], start=1):
            for slot, text in slide["text"].items():
                units.append({"id": f"s{index}-{slot}", "text": text, "approval_status": "approved",
                              "owner": {"channel": SLOT_CHANNELS.get(slot, "on-image-text"), "slide": index, "slot": slot}})
            units.append({"id": f"s{index}-alt", "text": slide["alt_text"], "approval_status": "approved",
                          "owner": {"channel": "alt-text", "slide": index}})
        spec["copy_allocation"]["content_units"] = units
        return spec

    def build(self, spec: dict):
        return build_social_from_spec(spec, base_dir=self.base, project_dir=self.project,
                                      manifest_path=self.manifest, formats_path=self.formats)

    def refused(self, spec: dict, message: str):
        with self.assertRaises((SocialRuntimeError, SocialSpecError)) as caught:
            self.build(spec)
        self.assertIn(message, str(caught.exception))


class BuildTests(SocialRuntimeCase):
    def test_preview_builds_and_passes_blocking_qa(self):
        result = self.build(self.spec())
        self.assertTrue(result.qa.passed, [c for c in result.qa.checks if not c["passed"]])
        self.assertTrue(result.zip_path.is_file())
        package = json.loads(result.package_manifest.read_text())
        self.assertEqual(list(package["variants"]), ["branded"])
        self.assertEqual(package["variants"]["branded"]["slides"][0]["locked"], {"wordmark": "The Rider"})
        self.assertEqual(package["variants"]["branded"]["slides"][1]["image"]["src"], "https://cdn.example.com/sq-2.jpg")

    def test_delivered_files_carry_no_private_identifiers(self):
        result = self.build(self.spec())
        for path in result.package_dir.iterdir():
            text = path.read_text(encoding="utf-8")
            for needle in ("SECRET", "private-folder", "dropbox_id", "dropbox_path", str(self.base)):
                self.assertNotIn(needle, text, path.name)

    def test_smoke_test_is_never_packaged_for_delivery(self):
        spec = self.spec()
        spec["build"]["mode"] = "smoke-test"
        result = self.build(spec)
        self.assertTrue(result.qa.passed)
        self.assertIsNone(result.zip_path)

    def test_release_builds_every_variant_with_broker_contact(self):
        spec = self.spec()
        spec["build"]["mode"] = "release"
        spec["variants"] = {"branded": {}, "broker-customizable": {"contact": {"name": "Pat Broker", "phone": "555-0100"}}}
        package = json.loads(self.build(spec).package_manifest.read_text())
        self.assertEqual(sorted(package["variants"]), ["branded", "broker-customizable"])
        self.assertEqual(package["variants"]["broker-customizable"]["contact"]["name"], "Pat Broker")
        self.assertEqual(package["variants"]["broker-customizable"]["slides"][0]["locked"]["wordmark"], "The Rider")

    def test_release_requires_approved_template_and_verified_format(self):
        spec = self.spec()
        spec["build"]["mode"] = "release"
        self.template["approval_status"] = "draft"
        self._write_template()
        self.refused(spec, "is a draft")
        self.template["approval_status"] = "approved"
        self._write_template()
        with self.assertRaises(SocialRuntimeError) as caught:
            build_social_from_spec(spec, base_dir=self.base, project_dir=self.project, manifest_path=self.manifest)
        self.assertIn("unverified", str(caught.exception))

    def test_text_over_a_slot_limit_fails_qa(self):
        spec = self.spec()
        spec["slides"][0]["text"]["headline"] = "A headline that runs well past the forty character slot limit"
        result = self.build(self.allocate(spec))
        self.assertFalse(result.qa.passed)
        self.assertIsNone(result.zip_path)
        self.assertIn("branded:slide-1:text:headline", [c["name"] for c in result.qa.checks if not c["passed"]])

    def test_refuses_to_replace_a_foreign_directory(self):
        target = self.base / "out" / "demo-carousel"
        target.mkdir(parents=True)
        (target / "notes.txt").write_text("keep")
        self.refused(self.spec(), "Refusing to replace")


class FormatAndTemplateTests(SocialRuntimeCase):
    def test_unpinned_format_fails_instead_of_defaulting(self):
        spec = self.spec()
        spec["composition"]["format"] = "carousel-9x16"
        self.refused(spec, "is not pinned")
        with self.assertRaises(FormatError):
            require_format(load_formats(), "reel-9x16")

    def test_shipped_sidecar_is_valid_and_unverified(self):
        sidecar = load_formats()
        self.assertEqual(sorted(sidecar["formats"]), ["carousel-1x1", "carousel-4x5", "post-1x1", "post-4x5"])
        self.assertTrue(all(entry["verified_date"] is None for entry in sidecar["formats"].values()))

    def test_slide_sequence_must_follow_the_template(self):
        spec = self.spec()
        spec["slides"][0], spec["slides"][1] = spec["slides"][1], spec["slides"][0]
        self.refused(self.allocate(spec), "expects role 'opener' at slide 1")
        with self.assertRaises(TemplateError):
            match_slides(self.template, ["opener", "call-to-action", "call-to-action"])

    def test_locked_content_and_required_slots_are_enforced(self):
        spec = self.spec()
        spec["slides"][0]["text"]["wordmark"] = "Someone Else"
        self.refused(spec, "overrides locked content")
        spec = self.spec()
        del spec["slides"][2]["text"]["action"]
        self.refused(self.allocate(spec), "leaves required slot(s) empty: action")


class AssetTests(SocialRuntimeCase):
    def test_asset_without_social_approval_fails_with_reason(self):
        spec = self.spec()
        spec["slides"][1]["image"] = {"asset": "plain.jpg"}
        self.refused(spec, "'plain.jpg' is not approved for 'social-carousel' (approved for: no social role)")

    def test_crop_source_cannot_be_used_directly(self):
        spec = self.spec()
        spec["slides"][1]["image"] = {"asset": "wide-1.jpg"}
        self.refused(spec, "is not approved for 'social-carousel'")

    def test_restricted_record_can_never_be_approved_into_a_build(self):
        self.overlay["entries"].append({"filename": "agent.jpg", "dropbox_id": "id:SECRET5XYZ", "cluster": "demo",
                                        "orientation": "square", "approved_for_social": ["social-carousel"]})
        self._write_overlay()
        self.refused(self.spec(), "restricted records may never resolve to a social role")

    def test_overlay_must_be_bound_to_the_current_manifest(self):
        self.manifest.write_text(self.manifest.read_text() + "\n", encoding="utf-8")
        self.refused(self.spec(), "not bound to the current manifest")


class BrokerTests(SocialRuntimeCase):
    def broker_spec(self) -> dict:
        spec = self.spec(audience="outside-broker")
        spec["variants"] = {"broker-customizable": {"contact": {"name": "Pat Broker"}}}
        return spec

    def test_broker_preview_builds_from_the_filtered_catalog(self):
        result = self.build(self.broker_spec())
        self.assertTrue(result.qa.passed, [c for c in result.qa.checks if not c["passed"]])

    def test_broker_catalog_omits_restricted_records_and_private_fields(self):
        from tools.asset_selection.selector import load_manifest
        from tools.asset_selection.social_approvals import apply_social_approvals, load_social_approvals
        overlay = load_social_approvals(self.project / "asset-approvals.social.json")
        safe = broker_safe_assets(apply_social_approvals(load_manifest(self.manifest), overlay), overlay["never_social_roles"])
        self.assertEqual(sorted(a["filename"] for a in safe), ["sq-1.jpg", "sq-2.jpg", "sq-3.jpg", "wide-1.jpg"])
        self.assertFalse(any({"dropbox_id", "dropbox_path", "stable_identity"} & set(a) for a in safe))

    def test_broker_build_cannot_reach_an_agent_record(self):
        spec = self.broker_spec()
        spec["slides"][1]["image"] = {"asset": "agent.jpg"}
        self.refused(spec, "'agent.jpg' is not in the social catalog for this audience")

    def test_broker_build_needs_an_approved_broker_template(self):
        self.template["audiences"] = ["in-house"]
        self._write_template()
        self.refused(self.broker_spec(), "not available to the outside-broker audience")
        self.template["audiences"] = ["in-house", "outside-broker"]
        self.template["approval_status"] = "draft"
        self._write_template()
        self.refused(self.broker_spec(), "is a draft")

    def test_broker_build_cannot_reference_the_email_medium(self):
        spec = self.broker_spec()
        spec["cross_medium"] = {"surfaces": [{"medium": "email", "campaign_spec": "email.json"}]}
        self.refused(spec, "email medium is absent from a broker bundle")

    def test_runtime_source_never_touches_agent_data_or_the_email_runtime(self):
        for path in RUNTIME_DIR.glob("*.py"):
            source = path.read_text(encoding="utf-8")
            if path.name != "qa.py":
                self.assertNotIn("data/agents", source, path.name)
            self.assertNotIn("import rider_campaign_runtime", source, path.name)
            self.assertNotIn("from tools.rider_campaign_runtime", source, path.name)
            self.assertNotIn("from ..rider_campaign_runtime", source, path.name)


class CropTests(SocialRuntimeCase):
    def crop_spec(self, mode="composition-preview", status="approved", data=None) -> dict:
        spec = self.spec()
        spec["build"]["mode"] = mode
        spec["composition"]["format"] = "carousel-4x5"
        crop = {"id": "crop-1", "source_asset": "wide-1.jpg", "format": "carousel-4x5",
                "source_dimensions": {"width": 3000, "height": 2000},
                "geometry": {"x": 700, "y": 0, "width": 1600, "height": 2000},
                "focal_point": {"x": 1500, "y": 1000}, "approval_status": status}
        if status == "approved":
            data = data or _png(1080, 1350)
            (self.base / "crop-1.png").write_bytes(data)
            crop["output"] = {"src": "crop-1.png", "sha256": hashlib.sha256(data).hexdigest(), "width": 1080, "height": 1350}
        spec["crops"] = [crop]
        for slide in spec["slides"]:
            slide["image"] = {"crop": "crop-1"}
        return spec

    def test_approved_crop_is_verified_and_packaged_with_provenance(self):
        result = self.build(self.crop_spec(mode="release"))
        self.assertTrue(result.qa.passed, [c for c in result.qa.checks if not c["passed"]])
        self.assertTrue((result.package_dir / "images" / "crop-1.png").is_file())
        record = json.loads(result.asset_manifest.read_text())["crops"][0]
        self.assertEqual(record["source_asset"], "wide-1.jpg")
        self.assertEqual(record["output"]["width"], 1080)
        self.assertNotIn("path", record["output"])

    def test_checksum_and_dimension_mismatches_are_rejected(self):
        spec = self.crop_spec()
        spec["crops"][0]["output"]["sha256"] = "0" * 64
        self.refused(spec, "checksum does not match")
        self.refused(self.crop_spec(data=_png(1080, 1080)), "dimensions do not match the local file")

    def test_geometry_must_match_the_format_and_stay_inside_the_source(self):
        spec = self.crop_spec()
        spec["crops"][0]["geometry"]["width"] = 2000
        self.refused(spec, "does not match the carousel-4x5 aspect ratio")
        spec = self.crop_spec()
        spec["crops"][0]["geometry"]["x"] = 2000
        self.refused(spec, "extends outside")

    def test_crop_source_must_be_approved_as_a_crop_source(self):
        spec = self.crop_spec()
        spec["crops"][0]["source_asset"] = "sq-1.jpg"
        self.refused(spec, "is not approved for 'social-crop-source'")

    def test_planned_crop_is_allowed_only_in_composition_preview(self):
        result = self.build(self.crop_spec(status="planned"))
        self.assertTrue(result.qa.passed)
        self.assertTrue(any("planned" in warning for warning in result.qa.warnings))
        self.refused(self.crop_spec(mode="release", status="planned"), "requires an approved crop with output")


class CopyAllocationTests(SocialRuntimeCase):
    def email_campaign(self, headline: str, policy: str = "single-use") -> None:
        (self.base / "email.json").write_text(json.dumps({
            "campaign": {"slug": "demo-email"},
            "copy_allocation": {"content_units": [
                {"id": "hero-headline", "text": f"<h1>{headline}</h1>", "reuse_policy": policy,
                 "owner": {"channel": "live-html", "module_id": "hero", "slot": "headline"}, "approval_status": "approved"},
                {"id": "legal", "text": "A closer look at life above the city this season",
                 "owner": {"channel": "legal"}, "approval_status": "approved"},
            ]},
        }), encoding="utf-8")

    def cross_spec(self, **cross) -> dict:
        return self.spec(cross_medium={"surfaces": [{"medium": "email", "campaign_spec": "email.json"}], **cross})

    def test_same_headline_in_email_and_carousel_is_detected_and_blocks(self):
        self.email_campaign("Kitchens built for hosting")
        result = self.build(self.cross_spec())
        self.assertFalse(result.qa.passed)
        failed = [c["name"] for c in result.qa.checks if not c["passed"]]
        self.assertEqual(failed, ["cross-medium-repetition:s2-headline:email:demo-email:hero-headline"])
        report = json.loads(result.qa_report.read_text())
        self.assertEqual(report["copy_allocation"]["cross_medium"]["surfaces"],
                         [{"medium": "email", "campaign": "demo-email", "units_compared": 1}])

    def test_distinct_copy_passes_and_recorded_exemption_is_honored(self):
        self.email_campaign("A different invitation entirely for subscribers")
        self.assertTrue(self.build(self.cross_spec()).qa.passed)
        self.email_campaign("Kitchens built for hosting")
        exempt = [{"social": "s2-headline", "other": "hero-headline", "reason": "Owner-approved campaign line"}]
        result = self.build(self.cross_spec(exemptions=exempt))
        self.assertTrue(result.qa.passed)
        self.assertTrue(result.qa.copy_allocation["cross_medium"]["pairs"][0]["exempt"])

    def test_unreadable_cross_medium_surface_is_refused(self):
        self.refused(self.cross_spec(), "Cross-medium surface is unreadable")

    def test_every_text_surface_needs_exactly_one_matching_owner(self):
        spec = self.spec()
        spec["copy_allocation"]["content_units"].pop()
        self.refused(spec, "Text surface(s) have no content unit: alt-text::3")
        spec = self.spec()
        spec["copy_allocation"]["content_units"][0]["text"] = "Stale caption"
        self.refused(spec, "text does not match its owner surface")

    def test_repeated_copy_inside_one_carousel_blocks(self):
        spec = self.spec()
        spec["slides"][2]["text"]["headline"] = spec["slides"][1]["text"]["headline"]
        result = self.build(self.allocate(spec))
        self.assertIn("copy-similarity:s2-headline:s3-headline", [c["name"] for c in result.qa.checks if not c["passed"]])

    def test_draft_copy_is_allowed_only_in_composition_preview(self):
        spec = self.spec()
        spec["copy_allocation"]["status"] = "draft"
        self.assertTrue(any("draft" in w for w in self.build(spec).qa.warnings))
        spec["build"]["mode"] = "release"
        self.refused(spec, "must be approved for a release build")

    def test_similarity_stays_in_parity_with_the_email_runtime(self):
        self.assertEqual(social_copy.NEAR_DUPLICATE_WARN_THRESHOLD, email_copy.NEAR_DUPLICATE_WARN_THRESHOLD)
        self.assertEqual(social_copy.NEAR_DUPLICATE_BLOCK_THRESHOLD, email_copy.NEAR_DUPLICATE_BLOCK_THRESHOLD)
        samples = [
            "Kitchens <b>built</b> for hosting — every night", "Kitchens built for hosting, every single night",
            "Wynwood’s “first” branded tower https://example.com/x", "Book a private tour today", "",
        ]
        for left in samples:
            self.assertEqual(social_copy.normalize_text(left), email_copy.normalize_text(left))
            for right in samples:
                a, b = social_copy.normalize_text(left), social_copy.normalize_text(right)
                self.assertEqual(social_copy.similarity_score(a, b), email_copy.similarity_score(a, b))


class IntegrationTests(unittest.TestCase):
    def test_social_runtime_is_registered_without_disturbing_email(self):
        self.assertEqual(sorted(RUNTIMES), ["rider-campaign", "social"])
        self.assertEqual(RUNTIMES["rider-campaign"][1].__module__, "tools.rider_campaign_runtime.schema")
        self.assertEqual(RUNTIMES["social"][2], build_social_from_spec)

    def test_rider_composition_preview_builds_from_approved_records(self):
        spec = json.loads(RIDER_PREVIEW.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            spec["campaign"]["output_dir"] = tmp
            result = build_social_from_spec(spec, base_dir=RIDER_PREVIEW.parent)
            self.assertTrue(result.qa.passed, [c for c in result.qa.checks if not c["passed"]])
            manifest = json.loads(result.asset_manifest.read_text())
            self.assertEqual(len(manifest["assets"]), 4)
            self.assertTrue(all("social-carousel" in a["social_roles"] for a in manifest["assets"]))


if __name__ == "__main__":
    unittest.main()
