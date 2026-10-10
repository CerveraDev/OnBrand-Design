"""Phase 17: social runtime for static posts and carousels."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

from tools.platform_adapters.contract import RUNTIMES
from tools.rider_campaign_runtime import copy_allocation as email_copy
from tools.social_runtime import SocialRuntimeError, SocialSpecError, build_social_from_spec
from tools.social_runtime import copy_allocation as social_copy
from tools.social_runtime.assets import broker_safe_assets
from tools.social_runtime.formats import FormatError, load_formats, require_format
from tools.social_runtime.frames import build_frame_definitions, load_frames
from tools.social_runtime.render import RenderError, render_package
from tools.social_runtime.supplied import load_supplied_image
from tools.social_runtime.templates import TemplateError, load_template, match_slides


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "tools" / "social_runtime"
RIDER_SOCIAL = ROOT / "projects" / "the-rider" / "social"
RIDER_PREVIEW = RIDER_SOCIAL / "examples" / "feature-carousel.preview.json"

ASSETS = (
    ("sq-1.jpg", "square", ["hero"], ["social-post", "social-carousel"]),
    ("sq-2.jpg", "square", ["body"], ["social-post", "social-carousel"]),
    ("sq-3.jpg", "square", ["body"], ["social-post", "social-carousel"]),
    ("wide-1.jpg", "landscape", ["hero"], ["social-crop-source"]),
    ("plain.jpg", "square", ["body"], None),
    ("agent.jpg", "square", ["agent-footer"], None),
)
SLOT_CHANNELS = {"headline": "on-image-text", "body": "slide-text", "action": "on-image-text"}
BACKGROUND = {"slot": "background", "width": 600, "height": 600, "shape": "square", "fit": "cover"}


def _text_slot(channel="on-image-text", required=True, max_chars=40) -> dict:
    return {"channel": channel, "required": required, "max_lines": 2, "max_chars": max_chars, "italic_accent": False}


def _frame(text_slots: dict, *, locked=None, images=(BACKGROUND,)) -> dict:
    return {"family": "carousel", "canvas": {"width": 600, "height": 600}, "image_slots": list(images),
            "text_slots": text_slots, "locked": locked or {}}


FRAMES = {
    "TA-01": _frame({"headline": _text_slot(), "subhead": _text_slot(required=False, max_chars=70)},
                    locked={"wordmark": "The Rider"}),
    "TB-01": _frame({"headline": _text_slot(), "body": _text_slot("slide-text", False, 110)}),
    "TC-01": _frame({"headline": _text_slot(), "action": _text_slot(max_chars=30)}, locked={"wordmark": "The Rider"}),
    "TD-01": _frame({"headline": _text_slot()},
                    images=(BACKGROUND, {"slot": "image-1", "width": 300, "height": 200, "shape": "landscape", "fit": "cover"})),
}
TEMPLATE = {
    "schema_version": "2.0", "code": "CAR-01", "label": "Feature Carousel", "kind": "carousel",
    "formats": ["carousel-1x1"], "approval_status": "approved", "audiences": ["in-house", "outside-broker"],
    "image_sources": ["approved"],
    "min_slides": 3, "max_slides": 6,
    "sequence": [
        {"role": "opener", "min": 1, "max": 1, "frames": ["TA-01"]},
        {"role": "feature", "min": 1, "max": 4, "frames": ["TB-01", "TD-01"]},
        {"role": "call-to-action", "min": 1, "max": 1, "frames": ["TC-01"]},
    ],
}


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
        self.template = json.loads(json.dumps(TEMPLATE))
        self._write_template()
        (self.project / "social" / "templates" / "frames.json").write_text(
            json.dumps({"schema_version": "1.0", "frames": FRAMES}), encoding="utf-8")
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
            {"role": "opener", "frame": "TA-01", "images": {"background": {"asset": "sq-1.jpg"}},
             "text": {"headline": "Arrive at the tower"},
             "alt_text": "Tower exterior seen from the street"},
            {"role": "feature", "frame": "TB-01", "images": {"background": {"asset": "sq-2.jpg"}},
             "text": {"headline": "Kitchens built for hosting", "body": "Stone counters and integrated appliances in every plan"},
             "alt_text": "Kitchen with an island and pendant lights"},
            {"role": "call-to-action", "frame": "TC-01", "images": {"background": {"asset": "sq-3.jpg"}},
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
        self.assertEqual(package["variants"]["branded"]["slides"][1]["images"][0]["src"], "https://cdn.example.com/sq-2.jpg")

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
            match_slides(load_template(self.project / "social" / "templates", "CAR-01"),
                         [{"role": "opener", "frame": "TA-01"}] + [{"role": "call-to-action", "frame": "TC-01"}] * 2)

    def test_slide_frame_must_be_one_the_template_allows_for_its_role(self):
        spec = self.spec()
        spec["slides"][1]["frame"] = "TC-01"
        self.refused(spec, "does not allow frame 'TC-01' for role 'feature' at slide 2; allowed: TB-01, TD-01")
        self.template["sequence"][1]["frames"].append("ZZ-99")
        self._write_template()
        self.refused(self.spec(), "names undefined frame(s): ZZ-99")

    def test_frame_canvas_must_fit_the_format(self):
        self.template["formats"].append("carousel-4x5")
        self._write_template()
        spec = self.spec()
        spec["composition"]["format"] = "carousel-4x5"
        self.refused(spec, "Frame TA-01 is 600x600 and does not fit format 'carousel-4x5'")

    def test_every_image_slot_of_a_frame_must_be_filled_and_no_other(self):
        spec = self.spec()
        spec["slides"][1]["frame"] = "TD-01"
        del spec["slides"][1]["text"]["body"]
        self.refused(self.allocate(spec), "Slide 2 leaves image slot(s) empty: image-1")
        spec["slides"][1]["images"]["image-1"] = {"asset": "sq-3.jpg"}
        self.refused(self.allocate(spec), "cannot be used directly in the landscape 'image-1' slot")
        spec["slides"][0]["images"]["image-1"] = {"asset": "sq-3.jpg"}
        self.refused(self.allocate(spec), "Slide 1 fills image slot(s) frame TA-01 does not define: image-1")

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
        spec["slides"][1]["images"]["background"] = {"asset": "plain.jpg"}
        self.refused(spec, "'plain.jpg' is not approved for 'social-carousel' (approved for: no social role)")

    def test_crop_source_cannot_be_used_directly(self):
        spec = self.spec()
        spec["slides"][1]["images"]["background"] = {"asset": "wide-1.jpg"}
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
        spec["slides"][1]["images"]["background"] = {"asset": "agent.jpg"}
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
        crop = {"id": "crop-1", "source_asset": "wide-1.jpg", "format": "carousel-1x1",
                "source_dimensions": {"width": 3000, "height": 2000},
                "geometry": {"x": 500, "y": 0, "width": 2000, "height": 2000},
                "focal_point": {"x": 1500, "y": 1000}, "approval_status": status}
        if status == "approved":
            data = data or _png(1080, 1080)
            (self.base / "crop-1.png").write_bytes(data)
            crop["output"] = {"src": "crop-1.png", "sha256": hashlib.sha256(data).hexdigest(), "width": 1080, "height": 1080}
        spec["crops"] = [crop]
        for slide in spec["slides"]:
            slide["images"]["background"] = {"crop": "crop-1"}
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
        self.refused(self.crop_spec(data=_png(1080, 1350)), "dimensions do not match the local file")

    def test_geometry_must_match_the_image_slot_and_stay_inside_the_source(self):
        spec = self.crop_spec()
        spec["crops"][0]["geometry"]["width"] = 1500
        self.refused(spec, "does not match the 1080x1080 'background' slot")
        spec = self.crop_spec()
        spec["crops"][0]["geometry"]["x"] = 2000
        self.refused(spec, "extends outside")

    def test_crop_is_sized_to_the_image_slot_it_fills(self):
        spec = self.spec()
        spec["slides"][1]["frame"] = "TD-01"
        del spec["slides"][1]["text"]["body"]
        data = _png(540, 360)
        (self.base / "wide-crop.png").write_bytes(data)
        spec["crops"] = [{"id": "wide-crop", "source_asset": "wide-1.jpg", "format": "carousel-1x1",
                          "source_dimensions": {"width": 3000, "height": 2000},
                          "geometry": {"x": 0, "y": 0, "width": 3000, "height": 2000},
                          "focal_point": {"x": 1500, "y": 1000}, "approval_status": "approved",
                          "output": {"src": "wide-crop.png", "sha256": hashlib.sha256(data).hexdigest(),
                                     "width": 540, "height": 360}}]
        spec["slides"][1]["images"]["image-1"] = {"crop": "wide-crop"}
        result = self.build(self.allocate(spec))
        self.assertTrue(result.qa.passed, [c for c in result.qa.checks if not c["passed"]])
        slide = json.loads(result.package_manifest.read_text())["variants"]["branded"]["slides"][1]
        self.assertEqual([(i["slot"], i["width"], i["height"]) for i in slide["images"]],
                         [("background", 1080, 1080), ("image-1", 540, 360)])
        spec["slides"][0]["images"]["background"] = {"crop": "wide-crop"}
        self.refused(spec, "Crop 'wide-crop' is used in image slots of different sizes")

    def test_crop_source_must_be_approved_as_a_crop_source(self):
        spec = self.crop_spec()
        spec["crops"][0]["source_asset"] = "sq-1.jpg"
        self.refused(spec, "is not approved for 'social-crop-source'")

    def test_planned_crop_is_allowed_only_in_composition_preview(self):
        result = self.build(self.crop_spec(status="planned"))
        self.assertTrue(result.qa.passed)
        self.assertTrue(any("planned" in warning for warning in result.qa.warnings))
        self.refused(self.crop_spec(mode="release", status="planned"), "requires an approved crop with output")


class SuppliedImageTests(SocialRuntimeCase):
    def supplied_spec(self, data=None, name="event.png") -> dict:
        self.template["image_sources"] = ["approved", "user-supplied"]
        self._write_template()
        (self.base / name).write_bytes(data or _png(1600, 1600))
        spec = self.spec()
        spec["slides"][1]["images"]["background"] = {"supplied": name}
        return spec

    def test_supplied_image_is_packaged_and_recorded_as_user_supplied(self):
        result = self.build(self.supplied_spec())
        self.assertTrue(result.qa.passed, [c for c in result.qa.checks if not c["passed"]])
        record = json.loads(result.asset_manifest.read_text())["supplied"][0]
        self.assertEqual((record["source_name"], record["width"], record["height"]), ("event.png", 1600, 1600))
        self.assertTrue((result.package_dir / "images" / record["name"]).is_file())
        self.assertTrue(any("not in the approved catalog" in w for w in result.qa.warnings))
        delivered = result.package_manifest.read_text() + result.asset_manifest.read_text()
        self.assertNotIn(str(self.base), delivered)

    def test_template_must_allow_supplied_images(self):
        spec = self.supplied_spec()
        self.template["image_sources"] = ["approved"]
        self._write_template()
        self.refused(spec, "Template CAR-01 takes approved images only")

    def test_supplied_image_must_match_the_slot_orientation_and_be_readable(self):
        self.refused(self.supplied_spec(data=_png(2000, 1200)), "is landscape (2000x1200) and cannot fill the square 'background' slot")
        self.refused(self.supplied_spec(data=b"not an image"), "is not a readable PNG or JPEG")
        spec = self.supplied_spec()
        spec["slides"][1]["images"]["background"] = {"supplied": "missing.png"}
        self.refused(spec, "Supplied image 'missing.png' was not found")

    def test_phone_photo_orientation_tag_decides_the_shape(self):
        exif = b"Exif\x00\x00MM\x00\x2a\x00\x00\x00\x08\x00\x01\x01\x12\x00\x03\x00\x00\x00\x01\x00\x06\x00\x00"
        sof = b"\x00\x11\x08" + struct.pack(">HH", 3000, 4000) + b"\x03" + bytes(9)
        jpeg = (b"\xff\xd8\xff\xe1" + struct.pack(">H", len(exif) + 2) + exif
                + b"\xff\xc0" + sof + b"\xff\xd9")
        record = load_supplied_image("phone.jpg", base_dir=self._write("phone.jpg", jpeg),
                                     slot={"slot": "image-1", "shape": "portrait"})
        self.assertEqual((record["width"], record["height"]), (3000, 4000))

    def _write(self, name: str, data: bytes) -> Path:
        (self.base / name).write_bytes(data)
        return self.base

    def test_small_supplied_image_warns_that_it_will_be_enlarged(self):
        result = self.build(self.supplied_spec(data=_png(400, 400)))
        self.assertTrue(any("it will be enlarged" in w for w in result.qa.warnings))


class RenderTests(SocialRuntimeCase):
    def setUp(self):
        super().setUp()
        scaffold = self.project / "social" / "scaffold"
        scaffold.mkdir()
        (scaffold / "scaffold.html").write_text("<!doctype html>", encoding="utf-8")
        (scaffold / "scaffold.css").write_text("", encoding="utf-8")
        self.jobs = []

    def renderer(self, *, size=(1080, 1080), lines=1, inside=True, error=None):
        def run(job: dict) -> dict:
            self.jobs.append(job)
            slides = []
            for slide in job["slides"]:
                if error:
                    slides.append({"output": slide["output"], "error": error})
                    continue
                Path(slide["output"]).parent.mkdir(parents=True, exist_ok=True)
                Path(slide["output"]).write_bytes(_png(*size))
                slides.append({
                    "output": slide["output"], "logo_loaded": None,
                    "images": [{"slot": i["slot"], "natural_width": 2000, "natural_height": 2000} for i in slide["images"]],
                    "text": {t["slot"]: {"lines": lines, "inside_canvas": inside} for t in slide["text"]},
                })
            return {"slides": slides}
        return run

    def render(self, spec=None, **renderer):
        built = self.build(spec or self.spec())
        return built, render_package(built.package_dir, project_dir=self.project, formats_path=self.formats,
                                     renderer=self.renderer(**renderer))

    def test_every_slide_is_rendered_at_the_format_size_and_packaged(self):
        built, result = self.render()
        self.assertTrue(result.passed, [c for c in result.checks if not c["passed"]])
        self.assertEqual([p.relative_to(built.package_dir).as_posix() for p in result.slides],
                         [f"slides/branded/slide-0{n}.jpg" for n in (1, 2, 3)])
        job = self.jobs[0]
        self.assertEqual(job["scale"], 1080 / 600)
        self.assertEqual(job["slides"][0]["frame"], "TA-01")
        self.assertEqual(job["slides"][0]["images"], [{"slot": "background", "url": "https://cdn.example.com/sq-1.jpg"}])
        report = json.loads(result.report.read_text())
        self.assertTrue(report["passed"])
        self.assertNotIn(str(self.base), result.report.read_text())
        with zipfile.ZipFile(result.zip_path) as archive:
            self.assertIn("demo-carousel/slides/branded/slide-01.jpg", archive.namelist())

    def test_text_that_wraps_past_its_line_limit_or_leaves_the_slide_fails(self):
        _, result = self.render(lines=3)
        self.assertFalse(result.passed)
        self.assertIsNone(result.zip_path)
        self.assertIn("3 of 2 lines", [c["message"] for c in result.checks if not c["passed"]])
        _, result = self.render(inside=False)
        self.assertTrue(any("runs outside the slide" in c["message"] for c in result.checks if not c["passed"]))

    def test_wrong_output_size_and_renderer_errors_fail(self):
        _, result = self.render(size=(1080, 1350))
        self.assertFalse(result.passed)
        _, result = self.render(error="image for slot 'background' could not be loaded")
        self.assertEqual({c["message"] for c in result.checks}, {"image for slot 'background' could not be loaded"})

    def test_packaged_images_are_passed_as_local_files_and_planned_crops_warn(self):
        spec = CropTests.crop_spec(self)
        _, result = self.render(spec)
        self.assertTrue(self.jobs[0]["slides"][0]["images"][0]["url"].endswith("/images/crop-1.png"))
        self.assertEqual(result.warnings, [])
        _, result = self.render(CropTests.crop_spec(self, status="planned"))
        self.assertEqual(self.jobs[1]["slides"][0]["images"][0]["url"], "https://cdn.example.com/wide-1.jpg")
        self.assertTrue(all("rendered from its uncropped source" in w for w in result.warnings))

    def test_render_is_refused_for_a_failed_build_or_stale_frame_definitions(self):
        spec = self.spec()
        spec["slides"][0]["text"]["headline"] = "x" * 41
        failed = self.build(self.allocate(spec))
        with self.assertRaises(RenderError) as caught:
            render_package(failed.package_dir, project_dir=self.project, formats_path=self.formats, renderer=self.renderer())
        self.assertIn("failed blocking QA", str(caught.exception))
        built = self.build(self.spec())
        frames = self.project / "social" / "templates" / "frames.json"
        data = json.loads(frames.read_text())
        data["generated_from"] = {"scaffold_html_sha256": "0" * 64, "scaffold_css_sha256": "0" * 64}
        frames.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(RenderError) as caught:
            render_package(built.package_dir, project_dir=self.project, formats_path=self.formats, renderer=self.renderer())
        self.assertIn("out of date with scaffold.html", str(caught.exception))


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
            self.assertEqual(len(manifest["assets"]), 3)
            self.assertTrue(all("social-carousel" in a["social_roles"] for a in manifest["assets"]))

    @unittest.skipUnless(os.environ.get("ONBRAND_RENDER_TESTS") == "1",
                         "set ONBRAND_RENDER_TESTS=1 to render in Chromium; needs Node, Playwright, and network")
    def test_rider_composition_preview_renders_every_slide_from_the_scaffold(self):
        spec = json.loads(RIDER_PREVIEW.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            spec["campaign"]["output_dir"] = tmp
            built = build_social_from_spec(spec, base_dir=RIDER_PREVIEW.parent)
            result = render_package(built.package_dir)
            self.assertTrue(result.passed, [c for c in result.checks if not c["passed"]])
            self.assertEqual(len(result.slides), 3)

    def test_rider_frame_definitions_are_current_with_the_scaffold_catalog(self):
        catalog = json.loads((RIDER_SOCIAL / "scaffold" / "frame-catalog.json").read_text(encoding="utf-8"))
        committed = load_frames(RIDER_SOCIAL / "templates" / "frames.json")
        self.assertEqual(committed, build_frame_definitions(catalog, logo_label="The Rider logo"))
        self.assertEqual(sorted(committed["frames"]), sorted(frame["id"] for frame in catalog["frames"]))

    def test_rider_templates_cover_every_scaffold_frame_and_stay_draft(self):
        frames = load_frames(RIDER_SOCIAL / "templates" / "frames.json")["frames"]
        covered = set()
        for code in ("PST-01", "CAR-01", "GAL-01"):
            template = load_template(RIDER_SOCIAL / "templates", code)
            self.assertEqual(template["approval_status"], "draft")
            self.assertEqual(template["audiences"], ["in-house"])
            covered |= set(template["frame_definitions"])
        self.assertEqual(covered, set(frames))

    def test_rider_owner_decisions_of_2026_10_09_hold(self):
        formats = load_formats()["formats"]
        for format_id in ("post-4x5", "carousel-4x5"):
            self.assertEqual((formats[format_id]["width"], formats[format_id]["height"]), (1200, 1500))
        frames = load_frames(RIDER_SOCIAL / "templates" / "frames.json")["frames"]
        self.assertEqual({slot["fit"] for frame in frames.values() for slot in frame["image_slots"]}, {"cover"})
        sources = {code: load_template(RIDER_SOCIAL / "templates", code)["image_sources"]
                   for code in ("PST-01", "CAR-01", "GAL-01")}
        self.assertEqual(sources, {"PST-01": ["approved"], "CAR-01": ["approved"],
                                   "GAL-01": ["approved", "user-supplied"]})


if __name__ == "__main__":
    unittest.main()
