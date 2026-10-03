import copy
import unittest

from tools.rider_campaign_runtime.copy_allocation import (
    CopyAllocationError,
    similarity_score,
    validate_copy_allocation,
)
from tools.rider_campaign_runtime.runtime import MODULE_METADATA_PATH, ROOT, SCAFFOLD_PATH, SLOT_MAP_PATH
from tools.rider_campaign_runtime.scaffold import load_scaffold


class RiderCopyAllocationTests(unittest.TestCase):
    def setUp(self):
        self.scaffold = load_scaffold(SCAFFOLD_PATH, SLOT_MAP_PATH, MODULE_METADATA_PATH)

    def test_accepts_clean_approved_allocation(self):
        summary = validate_copy_allocation(clean_spec(), scaffold=self.scaffold)
        self.assertTrue(summary["passed"])
        self.assertEqual(summary["content_unit_count"], 6)

    def test_rejects_known_repeated_wellness_copy_pattern(self):
        spec = clean_spec()
        slot = spec["modules"][1]["slots"]
        slot["section_3_heading"] = {"kind": "text", "value": "Same routine."}
        slot["list_item_1"] = {"kind": "safe_rich_text", "value": "<em>Same routine.</em>"}
        spec["copy_allocation"]["content_units"].extend(
            [
                live_unit("wellness-routine-heading", "Same routine.", "BODY - DARK THEN LIGHT LAYOUT", "section_3_heading"),
                live_unit("wellness-routine-list", "<em>Same routine.</em>", "BODY - DARK THEN LIGHT LAYOUT", "list_item_1"),
            ]
        )
        with self.assertRaisesRegex(CopyAllocationError, "occurrence"):
            validate_copy_allocation(spec, scaffold=self.scaffold)

    def test_rejects_exact_repetition_across_live_and_baked_image_text(self):
        spec = clean_spec()
        spec["image_workflow"] = baked_image_workflow()
        spec["copy_allocation"]["content_units"].append(
            {
                "id": "baked-hero-copy",
                "text": "Miami's new epicenter of wellness",
                "content_role": "baked-image-heading",
                "source": "creator-declared OCR",
                "approval_status": "approved",
                "owner": {"channel": "baked-image-text", "image_workflow_id": "baked-hero"},
                "declared_text_source": "creator-declared",
                "reuse_policy": "single-use",
                "max_occurrences": 1,
                "claim_policy": "none",
            }
        )
        with self.assertRaisesRegex(CopyAllocationError, "occurrence"):
            validate_copy_allocation(spec, scaffold=self.scaffold)
        spec["copy_allocation"]["content_units"][-1]["text"] = "Recovery finds its own pace."
        result = validate_copy_allocation(spec, scaffold=self.scaffold)
        self.assertTrue(result["passed"])
        self.assertEqual(result["runtime_copy_owner_count"], 7)

    def test_rejects_near_duplicate_overlap_threshold(self):
        spec = clean_spec()
        spec["modules"][1]["slots"]["section_1_copy"] = {
            "kind": "text",
            "value": "The wellness routine now travels with you in Miami every day.",
        }
        spec["modules"][1]["slots"]["section_2_copy"] = {
            "kind": "text",
            "value": "The wellness routine now travels with you in Miami each day.",
        }
        spec["copy_allocation"]["content_units"].extend(
            [
                live_unit(
                    "wellness-copy-a",
                    "The wellness routine now travels with you in Miami every day.",
                    "BODY - DARK THEN LIGHT LAYOUT",
                    "section_1_copy",
                ),
                live_unit(
                    "wellness-copy-b",
                    "The wellness routine now travels with you in Miami each day.",
                    "BODY - DARK THEN LIGHT LAYOUT",
                    "section_2_copy",
                ),
            ]
        )
        self.assertGreaterEqual(
            similarity_score(
                "the wellness routine now travels with you in miami every day",
                "the wellness routine now travels with you in miami each day",
            ),
            0.82,
        )
        with self.assertRaisesRegex(CopyAllocationError, "copy-similarity"):
            validate_copy_allocation(spec, scaffold=self.scaffold)

    def test_allows_intentional_approved_refrain(self):
        spec = clean_spec()
        spec["modules"][1]["slots"]["section_3_heading"] = {"kind": "text", "value": "Same routine."}
        spec["modules"][1]["slots"]["list_item_1"] = {"kind": "safe_rich_text", "value": "<em>Same routine.</em>"}
        spec["copy_allocation"]["content_units"].extend(
            [
                {
                    **live_unit("approved-refrain-a", "Same routine.", "BODY - DARK THEN LIGHT LAYOUT", "section_3_heading"),
                    "reuse_policy": "intentional-refrain",
                    "max_occurrences": 2,
                },
                {
                    **live_unit(
                        "approved-refrain-b",
                        "<em>Same routine.</em>",
                        "BODY - DARK THEN LIGHT LAYOUT",
                        "list_item_1",
                    ),
                    "reuse_policy": "intentional-refrain",
                    "max_occurrences": 2,
                },
            ]
        )
        spec["copy_allocation"]["dedupe_exemptions"] = [
            {
                "id": "approved-routine-refrain",
                "reason": "User approved this short refrain as deliberate campaign rhythm.",
                "scope": "BODY - DARK THEN LIGHT LAYOUT section_3/list_item_1 only",
                "applies_to": ["approved-refrain-a", "approved-refrain-b"],
                "approved_by": "unit test",
                "approved_at": "2026-10-03",
                "evidence": "test fixture approval",
            }
        ]
        self.assertTrue(validate_copy_allocation(spec, scaffold=self.scaffold)["passed"])

    def test_static_and_legal_exemptions_are_explicit(self):
        spec = clean_spec()
        spec["modules"].append({"id": "STATIC BLOCK 1", "slots": {}})
        spec["static_blocks"][0]["decision"] = "include"
        spec["copy_allocation"]["content_units"].append(
            {
                "id": "static-brand-message",
                "text": "From the creators of The Bond",
                "content_role": "locked-static-brand-message",
                "source": "locked static block",
                "approval_status": "approved",
                "owner": {"channel": "static", "static_block_id": "STATIC BLOCK 1"},
                "reuse_policy": "static-brand",
                "max_occurrences": 1,
                "claim_policy": "approved-no-evidence-required",
            }
        )
        spec["copy_allocation"]["dedupe_exemptions"] = [
            {
                "id": "static-brand-approved",
                "reason": "Locked static block copy is included by explicit static-block decision.",
                "scope": "STATIC BLOCK 1 only",
                "applies_to": ["static-brand-message"],
                "approved_by": "unit test",
                "approved_at": "2026-10-03",
            }
        ]
        self.assertTrue(validate_copy_allocation(spec, scaffold=self.scaffold)["passed"])

    def test_exemption_does_not_bypass_occurrence_cap(self):
        spec = clean_spec()
        unit = spec["copy_allocation"]["content_units"][0]
        unit["reuse_policy"] = "metadata-required"
        spec["campaign"]["preview_text"] = unit["text"]
        spec["copy_allocation"]["content_units"][1]["text"] = unit["text"]
        spec["copy_allocation"]["dedupe_exemptions"] = [exemption([unit["id"]])]
        with self.assertRaisesRegex(CopyAllocationError, "occurrence"):
            validate_copy_allocation(spec, scaffold=self.scaffold)

    def test_rejects_missing_baked_text_and_stale_slot_allocation(self):
        spec = clean_spec()
        spec["image_workflow"] = baked_image_workflow()
        with self.assertRaisesRegex(CopyAllocationError, "missing declared copy"):
            validate_copy_allocation(spec, scaffold=self.scaffold)
        del spec["image_workflow"]
        spec["copy_allocation"]["slot_allocation"] = [{
            "module_id": "BODY - DARK THEN LIGHT LAYOUT", "slot": "wrong",
            "content_unit_id": "primary-cta", "rendering_type": "live-html",
        }]
        with self.assertRaisesRegex(CopyAllocationError, "Stale slot_allocation"):
            validate_copy_allocation(spec, scaffold=self.scaffold)

    def test_rejects_unallocated_alt_and_stale_exemption(self):
        spec = clean_spec()
        spec["copy_allocation"]["content_units"].pop()
        with self.assertRaisesRegex(CopyAllocationError, "Unallocated"):
            validate_copy_allocation(spec, scaffold=self.scaffold)
        spec = clean_spec()
        spec["copy_allocation"]["dedupe_exemptions"] = [exemption(["missing-unit"])]
        with self.assertRaisesRegex(CopyAllocationError, "Unknown dedupe exemption"):
            validate_copy_allocation(spec, scaffold=self.scaffold)

    def test_metadata_alt_and_live_share_normalized_corpus(self):
        spec = clean_spec()
        text = "Wellness arrives at The Rider"
        spec["modules"][0]["slots"]["background_image"]["alt"] = text.upper() + "."
        spec["copy_allocation"]["content_units"][3]["text"] = text.upper() + "."
        with self.assertRaisesRegex(CopyAllocationError, "occurrence"):
            validate_copy_allocation(spec, scaffold=self.scaffold)

    def test_supported_claim_evidence_is_preserved(self):
        spec = clean_spec()
        unit = spec["copy_allocation"]["content_units"][0]
        unit["claim_policy"] = "requires-evidence"
        unit["claim_references"] = ["approved project brief section 2"]
        result = validate_copy_allocation(spec, scaffold=self.scaffold)
        self.assertEqual(result["content_units"][0]["claim_references"], unit["claim_references"])

    def test_required_name_legal_and_footer_exemptions(self):
        spec = clean_spec()
        units = spec["copy_allocation"]["content_units"]
        for channel, text, policy in [
            ("legal", "ORAL REPRESENTATIONS CANNOT BE RELIED UPON", "required-legal"),
            ("footer", "305-432-9969", "footer-contact"),
        ]:
            units.append({
                **live_unit(channel, text, "BRANDED FOOTER", channel),
                "owner": {"channel": channel, "module_id": "BRANDED FOOTER", "slot": channel},
                "reuse_policy": policy,
            })
        for index, slot in enumerate(["section_1_copy", "section_2_copy"]):
            text = "The Rider"
            spec["modules"][1]["slots"][slot] = {"kind": "text", "value": text}
            units.append({**live_unit(f"name-{index}", text, "BODY - DARK THEN LIGHT LAYOUT", slot),
                          "reuse_policy": "required-name", "max_occurrences": 2})
        spec["copy_allocation"]["dedupe_exemptions"] = [exemption(["legal", "footer", "name-0", "name-1"])]
        self.assertTrue(validate_copy_allocation(spec, scaffold=self.scaffold)["passed"])

    def test_similarity_warning_is_reviewable_without_blocking(self):
        spec = clean_spec()
        texts = ["Wellness routines bring calm to daily life in Miami",
                 "Wellness routines bring energy to daily life in Miami"]
        for index, text in enumerate(texts):
            slot = f"section_{index + 1}_copy"
            spec["modules"][1]["slots"][slot] = {"kind": "text", "value": text}
            spec["copy_allocation"]["content_units"].append(live_unit(f"warn-{index}", text, "BODY - DARK THEN LIGHT LAYOUT", slot))
        result = validate_copy_allocation(spec, scaffold=self.scaffold)
        pair = next(item for item in result["similarity"] if item["left"] == "warn-0")
        self.assertGreaterEqual(pair["score"], 0.65)
        self.assertFalse(pair["blocking"])

    def test_rejects_unsupported_claim_without_evidence(self):
        spec = clean_spec()
        spec["copy_allocation"]["content_units"][0]["claim_policy"] = "requires-evidence"
        with self.assertRaisesRegex(CopyAllocationError, "unsupported claim"):
            validate_copy_allocation(spec, scaffold=self.scaffold)

    def test_rejects_duplicate_name_or_authority_phrase(self):
        spec = clean_spec()
        spec["modules"][1]["slots"]["section_1_copy"] = {
            "kind": "text",
            "value": "From the creators of The Bond, a wellness address takes shape.",
        }
        spec["modules"][1]["slots"]["section_2_copy"] = {
            "kind": "text",
            "value": "From the creators of The Bond, life stays connected to Miami.",
        }
        spec["copy_allocation"]["content_units"].extend(
            [
                live_unit(
                    "authority-a",
                    "From the creators of The Bond, a wellness address takes shape.",
                    "BODY - DARK THEN LIGHT LAYOUT",
                    "section_1_copy",
                ),
                live_unit(
                    "authority-b",
                    "From the creators of The Bond, life stays connected to Miami.",
                    "BODY - DARK THEN LIGHT LAYOUT",
                    "section_2_copy",
                ),
            ]
        )
        spec["copy_allocation"]["restricted_phrases"] = [
            {
                "id": "from-creators-authority",
                "phrase": "From the creators of The Bond",
                "max_occurrences": 1,
                "reason": "Authority phrase should have one owner.",
            }
        ]
        with self.assertRaisesRegex(CopyAllocationError, "restricted-phrase:from-creators-authority"):
            validate_copy_allocation(spec, scaffold=self.scaffold)

    def test_rejects_unknown_ambiguous_and_stale_owner(self):
        spec = clean_spec()
        stale = copy.deepcopy(spec)
        stale["copy_allocation"]["content_units"][0]["text"] = "Old subject"
        with self.assertRaisesRegex(CopyAllocationError, "does not match"):
            validate_copy_allocation(stale, scaffold=self.scaffold)

        unknown = copy.deepcopy(spec)
        unknown["copy_allocation"]["content_units"][0]["owner"]["metadata_field"] = "missing"
        with self.assertRaisesRegex(CopyAllocationError, "unknown or stale"):
            validate_copy_allocation(unknown, scaffold=self.scaffold)

        ambiguous = copy.deepcopy(spec)
        ambiguous["copy_allocation"]["content_units"].append(copy.deepcopy(ambiguous["copy_allocation"]["content_units"][0]))
        ambiguous["copy_allocation"]["content_units"][-1]["id"] = "duplicate-owner"
        with self.assertRaisesRegex(CopyAllocationError, "Ambiguous"):
            validate_copy_allocation(ambiguous, scaffold=self.scaffold)

    def test_runtime_preserves_approved_user_copy_contract(self):
        spec = clean_spec()
        user_text = "A quieter way to arrive in Miami."
        spec["modules"][1]["slots"]["section_1_copy"] = {"kind": "text", "value": user_text}
        spec["copy_allocation"]["content_units"].append(
            live_unit("user-approved-copy", user_text, "BODY - DARK THEN LIGHT LAYOUT", "section_1_copy")
        )
        summary = validate_copy_allocation(spec, scaffold=self.scaffold)
        self.assertTrue(summary["passed"])
        self.assertEqual(
            spec["modules"][1]["slots"]["section_1_copy"]["value"],
            user_text,
        )


def clean_spec():
    return {
        "schema_version": "1.0",
        "build": {"mode": "composition-preview", "representative_variant": "branded", "variant_policy": "single"},
        "campaign": {
            "slug": "copy-allocation-test",
            "title": "Copy Allocation Test",
            "output_dir": "campaign-output/copy-allocation-test",
            "subject": "Wellness arrives at The Rider",
            "preview_text": "The Rider puts daily wellness minutes from home.",
        },
        "manifest": {"path": "manifest.json"},
        "modules": [
            {
                "id": "HEADER & HERO - LIVE TEXT HEADING - FULL-WIDTH",
                "slots": {
                    "headline": {"kind": "safe_rich_text", "value": "MIAMI'S NEW EPICENTER<br>OF WELLNESS."},
                    "logo_link": {"kind": "url", "href": "https://theriderresidences.com"},
                    "background_image": {
                        "kind": "image",
                        "asset_id": "id:runtime-hero",
                        "alt": "The Rider wellness hero",
                        "role": "hero",
                    },
                },
            },
            {
                "id": "BODY - DARK THEN LIGHT LAYOUT",
                "slots": {
                    "primary_cta": {"kind": "text", "value": "REQUEST MORE INFORMATION"},
                    "gallery_image": {
                        "kind": "image",
                        "asset_id": "id:runtime-hero",
                        "alt": "The Rider recovery spa",
                        "role": "body",
                    },
                },
            },
        ],
        "static_blocks": [
            {"id": "STATIC BLOCK 1", "decision": "exclude"},
            {"id": "STATIC BLOCK 2", "decision": "exclude"},
            {"id": "STATIC BLOCK 3", "decision": "exclude"},
            {"id": "STATIC BLOCK 4", "decision": "exclude"},
        ],
        "variants": {"branded": True, "outside_broker": False, "agents": []},
        "copy_allocation": {
            "version": "1.0",
            "plan_id": "copy-allocation-test",
            "status": "approved",
            "approved_by": "unit test",
            "approved_at": "2026-10-03",
            "content_units": [
                metadata_unit("subject", "Wellness arrives at The Rider"),
                metadata_unit("preview_text", "The Rider puts daily wellness minutes from home."),
                live_unit(
                    "hero-headline",
                    "MIAMI'S NEW EPICENTER<br>OF WELLNESS.",
                    "HEADER & HERO - LIVE TEXT HEADING - FULL-WIDTH",
                    "headline",
                ),
                alt_unit(
                    "hero-alt",
                    "The Rider wellness hero",
                    "HEADER & HERO - LIVE TEXT HEADING - FULL-WIDTH",
                    "background_image",
                ),
                live_unit("primary-cta", "REQUEST MORE INFORMATION", "BODY - DARK THEN LIGHT LAYOUT", "primary_cta"),
                alt_unit("gallery-alt", "The Rider recovery spa", "BODY - DARK THEN LIGHT LAYOUT", "gallery_image"),
            ],
        },
    }


def metadata_unit(field, text):
    return {
        "id": f"meta-{field.replace('_', '-')}",
        "text": text,
        "content_role": field,
        "source": "approved fixture",
        "approval_status": "approved",
        "owner": {"channel": "metadata", "metadata_field": field},
        "reuse_policy": "single-use",
        "max_occurrences": 1,
        "claim_policy": "none",
    }


def exemption(targets):
    return {
        "id": "explicit-approval", "reason": "Approved fixture repetition", "scope": "named units only",
        "applies_to": targets, "approved_by": "unit test", "approved_at": "2026-10-03",
    }


def live_unit(unit_id, text, module_id, slot):
    return {
        "id": unit_id,
        "text": text,
        "content_role": slot,
        "source": "approved fixture",
        "approval_status": "approved",
        "owner": {"channel": "live-html", "module_id": module_id, "slot": slot},
        "reuse_policy": "single-use",
        "max_occurrences": 1,
        "claim_policy": "none",
    }


def alt_unit(unit_id, text, module_id, slot):
    return {
        "id": unit_id,
        "text": text,
        "content_role": "image-alt",
        "source": "approved fixture",
        "approval_status": "approved",
        "owner": {"channel": "alt-text", "module_id": module_id, "slot": slot},
        "reuse_policy": "single-use",
        "max_occurrences": 1,
        "claim_policy": "none",
    }


def baked_image_workflow():
    return {
        "version": "1.0",
        "items": [
            {
                "image_id": "baked-hero",
                "workflow_type": "grounded-edit",
                "status": "approved",
                "approved_by": "unit test",
                "approved_at": "2026-10-03",
                "intended_use": {
                    "module_id": "HEADER & HERO - LIVE TEXT HEADING - FULL-WIDTH",
                    "slot": "background_image",
                    "role": "hero",
                },
                "environment": {"type": "real-rider", "description": "fixture", "keywords": ["hero"]},
                "source_assets": [{"asset_id": "id:runtime-hero", "role": "environment-base"}],
                "prompt_record": {
                    "tool": "unit-test",
                    "prompt": "Fixture",
                    "edit_steps": ["Fixture"],
                    "text_policy": "baked-approved",
                },
                "output": {"src": "hero.png", "sha256": "0" * 64, "width": 1, "height": 1, "format": "png"},
                "placement": {"aspect_ratio": "16:9", "crop": "fixture", "focal_point": {"x": 0.5, "y": 0.5}},
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()
