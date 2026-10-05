import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.asset_selection.manifest_source import validate_manifest_source_config
from tools.rider_campaign_runtime.grounded_images import (
    GroundedImageError,
    validate_grounded_image_workflow,
)
from tools.rider_campaign_runtime.runtime import (
    MODULE_METADATA_PATH,
    ROOT,
    SCAFFOLD_PATH,
    SLOT_MAP_PATH,
    build_campaign_from_spec,
)
from tools.rider_campaign_runtime.scaffold import load_scaffold
from tools.rider_campaign_runtime.schema import validate_campaign_spec


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)
PNG_1X1_SHA = "ebf4f635a17d10d6eb46ba680b70142419aa3220f228001a036d311a22ee9d2a"


class RiderGroundedImageTests(unittest.TestCase):
    def setUp(self):
        self.scaffold = load_scaffold(SCAFFOLD_PATH, SLOT_MAP_PATH, MODULE_METADATA_PATH)

    def test_manifest_source_config_validates_local_cache_fallback(self):
        summary = validate_manifest_source_config(ROOT / "projects/the-rider/manifest-source.json")
        self.assertEqual(summary["active_source"], "local-cache")
        self.assertFalse(summary["public_url_configured"])
        self.assertGreater(summary["validated_asset_count"], 100)

    def test_existing_manifest_asset_selection_needs_no_image_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_image = write_png(tmp_path / "hero.png")
            spec = existing_asset_spec(tmp_path, output_image)
            validate_campaign_spec(spec)
            with patch("tools.rider_campaign_runtime.assets._read_asset") as read_asset:
                read_asset.side_effect = lambda source: (output_image.read_bytes(), Path(source).name or "asset.png")
                result = build_campaign_from_spec(spec, base_dir=tmp_path)
            asset_manifest = json.loads(result.asset_manifest.read_text())
            self.assertTrue(result.qa.passed)
            self.assertEqual(asset_manifest["image_workflow"], {})
            self.assertFalse(any("image_workflow_id" in item for item in asset_manifest["assets"]))

    def test_grounded_workflow_records_package_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_image = write_png(tmp_path / "assets" / "generated.png")
            spec = generated_image_spec(tmp_path, output_image)
            validate_campaign_spec(spec)
            with patch("tools.rider_campaign_runtime.assets._read_asset") as read_asset:
                read_asset.side_effect = lambda source: (output_image.read_bytes(), Path(source).name or "asset.png")
                result = build_campaign_from_spec(spec, base_dir=tmp_path)
            metadata = json.loads((result.package_dir / "campaign-metadata.json").read_text())
            asset_manifest = json.loads(result.asset_manifest.read_text())
            qa = json.loads(result.qa_report.read_text())
            self.assertTrue(result.qa.passed)
            self.assertEqual(metadata["image_workflow"]["items"][0]["image_id"], "wellness-gym-hero")
            self.assertEqual(asset_manifest["image_workflow"], metadata["image_workflow"])
            self.assertIn("wellness-gym-hero", {item.get("image_workflow_id") for item in asset_manifest["assets"]})
            self.assertEqual(qa["image_workflow"], metadata["image_workflow"])

    def test_grounded_workflow_rejects_unapproved_runtime_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_image = write_png(tmp_path / "assets" / "generated.png")
            spec = generated_image_spec(tmp_path, output_image)
            spec["image_workflow"]["items"][0]["status"] = "candidate"
            with self.assertRaisesRegex(GroundedImageError, "status must be approved"):
                validate_grounded_image_workflow(
                    spec,
                    base_dir=tmp_path,
                    manifest_assets=manifest_assets(output_image),
                    scaffold=self.scaffold,
                )

    def test_grounded_workflow_rejects_untracked_source_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_image = write_png(tmp_path / "assets" / "generated.png")
            spec = generated_image_spec(tmp_path, output_image)
            spec["image_workflow"]["items"][0]["source_assets"][0]["asset_id"] = "id:missing"
            with self.assertRaisesRegex(GroundedImageError, "not in manifest"):
                validate_grounded_image_workflow(
                    spec,
                    base_dir=tmp_path,
                    manifest_assets=manifest_assets(output_image),
                    scaffold=self.scaffold,
                )

    def test_grounded_workflow_rejects_source_that_does_not_match_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_image = write_png(tmp_path / "assets" / "generated.png")
            spec = generated_image_spec(tmp_path, output_image)
            spec["image_workflow"]["items"][0]["environment"]["keywords"] = ["lobby"]
            with self.assertRaisesRegex(GroundedImageError, "not grounded"):
                validate_grounded_image_workflow(
                    spec,
                    base_dir=tmp_path,
                    manifest_assets=manifest_assets(output_image),
                    scaffold=self.scaffold,
                )


def write_png(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(PNG_1X1)
    return path


def base_spec(tmp_path, output_image):
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
            "output_dir": str(tmp_path / "campaign-output"),
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
                },
                {
                    "id": "hero-alt",
                    "text": "The Rider gym",
                    "content_role": "image-alt",
                    "source": "unit-test",
                    "approval_status": "approved",
                    "owner": {
                        "channel": "alt-text",
                        "module_id": "hero-ai-generated",
                        "slot": "hero_image",
                    },
                    "reuse_policy": "single-use",
                    "max_occurrences": 1,
                    "claim_policy": "none",
                },
            ],
        },
        "manifest": {"path": str(write_manifest(tmp_path, output_image))},
        "modules": [
            {
                "id": "hero-ai-generated",
                "slots": {
                    "hero_image": {
                        "kind": "image",
                        "asset_id": "id:runtime-gym",
                        "alt": "The Rider gym",
                        "role": "hero",
                    }
                },
            }
        ],
        "static_blocks": [
            {"id": "static-authority", "decision": "exclude"},
            {"id": "static-design", "decision": "exclude"},
            {"id": "static-opportunity", "decision": "exclude"},
        ],
        "variants": {"branded": True, "outside_broker": False, "agents": []},
        "deployment": {"asset_mode": "relative-review"},
    }


def existing_asset_spec(tmp_path, output_image):
    return base_spec(tmp_path, output_image)


def generated_image_spec(tmp_path, output_image):
    spec = base_spec(tmp_path, output_image)
    spec["modules"][0]["slots"]["hero_image"] = {
        "kind": "image",
        "src": "assets/generated.png",
        "alt": "Woman framed inside The Rider gym environment",
        "role": "hero",
        "image_workflow_id": "wellness-gym-hero",
    }
    spec["copy_allocation"]["content_units"][1] = {
        "id": "hero-alt",
        "text": "Woman framed inside The Rider gym environment",
        "content_role": "image-alt",
        "source": "unit-test",
        "approval_status": "approved",
        "owner": {
            "channel": "alt-text",
            "module_id": "hero-ai-generated",
            "slot": "hero_image",
            "image_workflow_id": "wellness-gym-hero",
        },
        "reuse_policy": "single-use",
        "max_occurrences": 1,
        "claim_policy": "none",
    }
    spec["image_workflow"] = {
        "version": "1.0",
        "items": [
            {
                "image_id": "wellness-gym-hero",
                "workflow_type": "grounded-edit",
                "status": "approved",
                "approved_by": "unit test",
                "approved_at": "2026-10-03",
                "intended_use": {
                    "module_id": "hero-ai-generated",
                    "slot": "hero_image",
                    "role": "hero",
                    "variant_scope": "all",
                },
                "environment": {
                    "type": "real-rider",
                    "description": "The Rider gym and recovery environment",
                    "keywords": ["gym", "amenity"],
                    "conceptual_environment_approved": False,
                },
                "source_assets": [
                    {
                        "asset_id": "id:runtime-gym",
                        "role": "environment-base",
                        "required_approval": "hero",
                        "preserve": ["architecture", "lighting direction", "material identity"],
                    }
                ],
                "prompt_record": {
                    "tool": "manual-fixture",
                    "model": "deterministic-test",
                    "prompt": "Place a wellness subject inside the approved Rider gym without changing the room.",
                    "negative_prompt": "Do not invent a different gym or alter architecture.",
                    "edit_steps": ["Use approved gym source as environment base.", "Keep headline text live in HTML."],
                    "text_policy": "live-html",
                },
                "output": {
                    "src": "assets/generated.png",
                    "sha256": PNG_1X1_SHA,
                    "width": 1,
                    "height": 1,
                    "format": "png",
                },
                "placement": {
                    "aspect_ratio": "16:9",
                    "crop": "module-native hero crop",
                    "focal_point": {"x": 0.5, "y": 0.5},
                    "safe_area": "Subject centered; live HTML remains outside the image.",
                    "logo_overlay": "none",
                },
            }
        ],
    }
    return spec


def write_manifest(tmp_path, output_image):
    manifest = tmp_path / "manifest.json"
    records = [
        {
            "filename": "the-rider-gym-1.jpg",
            "dropbox_id": "id:runtime-gym",
            "dropbox_path": "/4. gym + recovery/the-rider-gym-1.jpg",
            "category": ["amenity", "gym"],
            "orientation": "landscape",
            "approved_for": ["hero", "body"],
            "public_url": output_image.as_uri(),
        }
    ]
    manifest.write_text(json.dumps(records), encoding="utf-8")
    return manifest


def manifest_assets(output_image):
    asset = {
        "filename": "the-rider-gym-1.jpg",
        "dropbox_id": "id:runtime-gym",
        "dropbox_path": "/4. gym + recovery/the-rider-gym-1.jpg",
        "category": ["amenity", "gym"],
        "orientation": "landscape",
        "approved_for": ["hero", "body"],
        "public_url": output_image.as_uri(),
        "media_type": "image",
        "stable_identity": "id:id:runtime-gym",
    }
    return {"id:runtime-gym": asset}


if __name__ == "__main__":
    unittest.main()
