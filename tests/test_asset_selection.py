import unittest

from tools.asset_selection import ManifestError, SelectionNeeds, select_candidates, validate_manifest


def asset(
    filename,
    dropbox_id,
    dropbox_path,
    *,
    category=None,
    approved_for=None,
    orientation="landscape",
    public_url=None,
):
    return {
        "filename": filename,
        "dropbox_id": dropbox_id,
        "dropbox_path": dropbox_path,
        "category": [] if category is None else category,
        "orientation": orientation,
        "approved_for": [] if approved_for is None else approved_for,
        "public_url": public_url or f"https://assets.example/{dropbox_id or filename}",
    }


class AssetSelectionTests(unittest.TestCase):
    def test_valid_selection_scores_and_shortlists_candidates(self):
        manifest = validate_manifest(
            [
                asset(
                    "hero.jpg",
                    "id:1",
                    "/rider/hero.jpg",
                    category=["exterior", "architecture"],
                    approved_for=["email_hero"],
                    orientation="landscape",
                ),
                asset(
                    "floorplan.pdf",
                    "id:2",
                    "/rider/floorplan.pdf",
                    category=["floorplan"],
                    approved_for=["attachment"],
                    orientation="portrait",
                ),
            ]
        )

        result = select_candidates(
            manifest,
            SelectionNeeds(
                media_type="image",
                approved_for=("email_hero",),
                categories=("exterior",),
                orientation="landscape",
            ),
        )

        self.assertEqual(result["matched_assets"], 1)
        self.assertEqual(result["candidates"][0]["filename"], "hero.jpg")
        self.assertIn("category overlap: exterior", result["candidates"][0]["reasons"])

    def test_rejects_malformed_curated_arrays(self):
        with self.assertRaisesRegex(ManifestError, "non-array category"):
            validate_manifest(
                [
                    asset(
                        "hero.jpg",
                        "id:1",
                        "/rider/hero.jpg",
                        category="exterior",
                        approved_for=["email_hero"],
                    )
                ]
            )

    def test_excludes_assets_without_required_approval(self):
        manifest = validate_manifest(
            [
                asset(
                    "hero.jpg",
                    "id:1",
                    "/rider/hero.jpg",
                    category=["exterior"],
                    approved_for=["social"],
                )
            ]
        )
        result = select_candidates(
            manifest,
            SelectionNeeds(media_type="image", approved_for=("email_hero",)),
        )

        self.assertEqual(result["matched_assets"], 0)
        self.assertEqual(result["excluded_assets"], 1)

    def test_requires_category_overlap_when_categories_are_requested(self):
        manifest = validate_manifest(
            [
                asset(
                    "amenity.jpg",
                    "id:1",
                    "/rider/amenity.jpg",
                    category=["amenity"],
                    approved_for=["email_hero"],
                ),
                asset(
                    "exterior.jpg",
                    "id:2",
                    "/rider/exterior.jpg",
                    category=["exterior"],
                    approved_for=["email_hero"],
                ),
            ]
        )
        result = select_candidates(
            manifest,
            SelectionNeeds(
                media_type="image",
                approved_for=("email_hero",),
                categories=("amenity",),
            ),
        )

        self.assertEqual([item["filename"] for item in result["candidates"]], ["amenity.jpg"])

    def test_ordering_is_deterministic_for_equal_scores(self):
        manifest = validate_manifest(
            [
                asset("zeta.jpg", "id:z", "/rider/zeta.jpg", approved_for=["email_hero"]),
                asset("alpha.jpg", "id:a", "/rider/alpha.jpg", approved_for=["email_hero"]),
            ]
        )
        result = select_candidates(
            manifest,
            SelectionNeeds(media_type="image", approved_for=("email_hero",)),
        )

        self.assertEqual([item["filename"] for item in result["candidates"]], ["alpha.jpg", "zeta.jpg"])

    def test_duplicate_filenames_are_distinguished_by_stable_identity(self):
        manifest = validate_manifest(
            [
                asset(
                    "hero.jpg",
                    "id:1",
                    "/rider/exterior/hero.jpg",
                    category=["exterior"],
                    approved_for=["email_hero"],
                ),
                asset(
                    "hero.jpg",
                    "id:2",
                    "/rider/amenity/hero.jpg",
                    category=["amenity"],
                    approved_for=["email_hero"],
                ),
            ]
        )
        result = select_candidates(
            manifest,
            SelectionNeeds(media_type="image", approved_for=("email_hero",), limit=10),
        )

        self.assertEqual(result["matched_assets"], 2)
        self.assertNotEqual(result["candidates"][0]["dropbox_path"], result["candidates"][1]["dropbox_path"])

    def test_missing_optional_orientation_does_not_invent_or_exclude_metadata(self):
        manifest = validate_manifest(
            [
                asset(
                    "unknown.jpg",
                    "id:1",
                    "/rider/unknown.jpg",
                    category=["exterior"],
                    approved_for=["email_hero"],
                    orientation="",
                ),
                asset(
                    "portrait.jpg",
                    "id:2",
                    "/rider/portrait.jpg",
                    category=["exterior"],
                    approved_for=["email_hero"],
                    orientation="portrait",
                ),
            ]
        )
        result = select_candidates(
            manifest,
            SelectionNeeds(
                media_type="image",
                approved_for=("email_hero",),
                categories=("exterior",),
                orientation="landscape",
            ),
        )

        self.assertEqual(result["matched_assets"], 1)
        self.assertEqual(result["candidates"][0]["filename"], "unknown.jpg")
        self.assertIn(
            "orientation metadata unavailable; no orientation score",
            result["candidates"][0]["reasons"],
        )


if __name__ == "__main__":
    unittest.main()
