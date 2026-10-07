"""Phase 17: social approval overlay validation and merge."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from tools.asset_selection.selector import load_manifest
from tools.asset_selection.social_approvals import (
    SocialApprovalError,
    apply_social_approvals,
    load_social_approvals,
    manifest_matches,
    social_candidates,
    validate_social_approvals,
)


ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "projects" / "the-rider" / "asset-approvals.social.json"
MANIFEST = ROOT / "tools" / "dropbox-manifest" / "manifest.json"

RESTRICTED_ROLES = {"agent-footer", "image-generation-reference"}


def _minimal_overlay():
    return {
        "schema_version": "1.0",
        "project_slug": "demo",
        "medium": "social",
        "approver": "Owner",
        "approved_date": "2026-10-06",
        "role_vocabulary": ["social-post", "social-carousel", "social-crop-source"],
        "never_social_roles": ["agent-footer", "image-generation-reference"],
        "source_manifest": {"path": "m.json", "sha256": "a" * 64, "record_count": 1},
        "entries": [
            {
                "filename": "a.jpg",
                "dropbox_id": "id:A",
                "cluster": "demo",
                "orientation": "square",
                "approved_for_social": ["social-post"],
            }
        ],
        "excluded": [],
    }


def _assets(*records):
    return [
        {
            "filename": r.get("filename", "a.jpg"),
            "dropbox_id": r.get("dropbox_id", "id:A"),
            "approved_for": r.get("approved_for", []),
            "category": r.get("category", []),
            "orientation": r.get("orientation", "square"),
        }
        for r in records
    ]


class SocialOverlayValidationTests(unittest.TestCase):
    def test_minimal_overlay_validates(self):
        result = validate_social_approvals(_minimal_overlay())
        self.assertEqual(result["medium"], "social")
        self.assertEqual(len(result["entries"]), 1)

    def test_unknown_top_level_field_is_rejected(self):
        data = _minimal_overlay()
        data["sneaky"] = True
        with self.assertRaises(SocialApprovalError):
            validate_social_approvals(data)

    def test_unknown_entry_field_is_rejected(self):
        data = _minimal_overlay()
        data["entries"][0]["notes"] = "hello"
        with self.assertRaises(SocialApprovalError):
            validate_social_approvals(data)

    def test_unknown_social_role_is_rejected(self):
        data = _minimal_overlay()
        data["entries"][0]["approved_for_social"] = ["social-reel"]
        with self.assertRaises(SocialApprovalError):
            validate_social_approvals(data)

    def test_duplicate_dropbox_id_is_rejected(self):
        data = _minimal_overlay()
        data["entries"].append(copy.deepcopy(data["entries"][0]))
        with self.assertRaises(SocialApprovalError):
            validate_social_approvals(data)

    def test_record_cannot_be_both_approved_and_excluded(self):
        data = _minimal_overlay()
        data["excluded"] = [{"filename": "a.jpg", "dropbox_id": "id:A", "reason": "restricted"}]
        with self.assertRaises(SocialApprovalError):
            validate_social_approvals(data)

    def test_wrong_medium_is_rejected(self):
        data = _minimal_overlay()
        data["medium"] = "email"
        with self.assertRaises(SocialApprovalError):
            validate_social_approvals(data)

    def test_empty_entries_is_rejected(self):
        data = _minimal_overlay()
        data["entries"] = []
        with self.assertRaises(SocialApprovalError):
            validate_social_approvals(data)


class SocialMergeTests(unittest.TestCase):
    def test_approved_asset_receives_roles_without_touching_approved_for(self):
        overlay = validate_social_approvals(_minimal_overlay())
        assets = _assets({"approved_for": ["body"]})
        merged = apply_social_approvals(assets, overlay)
        self.assertEqual(merged[0]["social_roles"], ["social-post"])
        self.assertEqual(merged[0]["approved_for"], ["body"], "email roles must be untouched")

    def test_unapproved_asset_gets_no_social_roles(self):
        overlay = validate_social_approvals(_minimal_overlay())
        assets = _assets({"approved_for": ["body"]}, {"filename": "b.jpg", "dropbox_id": "id:B"})
        merged = apply_social_approvals(assets, overlay)
        self.assertEqual(merged[1]["social_roles"], [])

    def test_restricted_record_can_never_resolve_to_a_social_role(self):
        for role in sorted(RESTRICTED_ROLES):
            with self.subTest(role=role):
                overlay = validate_social_approvals(_minimal_overlay())
                assets = _assets({"approved_for": [role]})
                with self.assertRaises(SocialApprovalError) as ctx:
                    apply_social_approvals(assets, overlay)
                self.assertIn("restricted", str(ctx.exception))

    def test_approval_for_missing_record_is_blocked(self):
        overlay = validate_social_approvals(_minimal_overlay())
        assets = _assets({"filename": "other.jpg", "dropbox_id": "id:OTHER"})
        with self.assertRaises(SocialApprovalError):
            apply_social_approvals(assets, overlay)

    def test_social_candidates_filters_and_sorts(self):
        overlay = validate_social_approvals(_minimal_overlay())
        merged = apply_social_approvals(_assets({"approved_for": ["body"]}), overlay)
        self.assertEqual([a["filename"] for a in social_candidates(merged, "social-post")], ["a.jpg"])
        self.assertEqual(social_candidates(merged, "social-crop-source"), [])

    def test_unknown_role_lookup_is_rejected(self):
        with self.assertRaises(SocialApprovalError):
            social_candidates([], "social-reel")


class RiderOverlayTests(unittest.TestCase):
    """The committed Rider overlay must stay consistent with its manifest."""

    def setUp(self):
        if not MANIFEST.is_file():
            self.skipTest("local manifest cache is not present")
        self.overlay = load_social_approvals(OVERLAY)
        self.assets = load_manifest(MANIFEST)

    def test_overlay_validates_and_merges(self):
        merged = apply_social_approvals(self.assets, self.overlay)
        self.assertEqual(len(merged), len(self.assets))
        approved = [a for a in merged if a["social_roles"]]
        self.assertEqual(len(approved), len(self.overlay["entries"]))

    def test_no_restricted_asset_is_social_approved(self):
        merged = apply_social_approvals(self.assets, self.overlay)
        leaked = [
            a["filename"]
            for a in merged
            if a["social_roles"] and set(a.get("approved_for") or []) & RESTRICTED_ROLES
        ]
        self.assertEqual(leaked, [], "restricted records must never carry a social role")

    def test_no_pdf_is_social_approved(self):
        merged = apply_social_approvals(self.assets, self.overlay)
        pdfs = [a["filename"] for a in merged if a["social_roles"] and a["media_type"] == "pdf"]
        self.assertEqual(pdfs, [], "PDFs await the conversion pipeline")

    def test_landscape_assets_are_crop_sources_only(self):
        merged = apply_social_approvals(self.assets, self.overlay)
        wrong = [
            a["filename"]
            for a in merged
            if a["social_roles"]
            and a.get("orientation") == "landscape"
            and a["social_roles"] != ["social-crop-source"]
        ]
        self.assertEqual(wrong, [], "landscape assets cannot be directly usable")

    def test_overlay_is_bound_to_current_manifest(self):
        self.assertTrue(
            manifest_matches(self.overlay, MANIFEST),
            "overlay sha256 no longer matches the manifest; re-confirm approvals after a refresh",
        )

    def test_every_approved_record_exists_and_is_an_image(self):
        by_id = {a["dropbox_id"]: a for a in self.assets}
        for entry in self.overlay["entries"]:
            with self.subTest(filename=entry["filename"]):
                asset = by_id.get(entry["dropbox_id"])
                self.assertIsNotNone(asset)
                self.assertEqual(asset["media_type"], "image")


if __name__ == "__main__":
    unittest.main()
