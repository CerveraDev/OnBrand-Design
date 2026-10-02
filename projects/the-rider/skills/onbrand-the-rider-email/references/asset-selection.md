# Asset Selection

Use existing approved Rider imagery whenever it satisfies the campaign. Do not generate new imagery merely for novelty.

## Image Sources

- Permanent Rider asset library
- Temporary campaign or event folder
- User-specified image
- Generated or edited image from the Rider image-generation workflow

## Master Manifest

Normal campaign generation must consume a configured Rider master `manifest.json` and approved public asset URLs. It must not require Dropbox app credentials, print credential-like values, or run `tools/dropbox-manifest/build_manifest.py` unless the user explicitly asks for a manifest refresh.

Use the shared selector from the repository root once the manifest path is known:

```bash
python3 -m tools.asset_selection.select_assets \
  --manifest /path/to/manifest.json \
  --media-type image \
  --approved-for email_hero \
  --category exterior \
  --orientation landscape \
  --pretty
```

The selector validates the manifest before returning candidates. It rejects malformed curated metadata, including non-array `category` or `approved_for` values, so manual classifications are fixed intentionally rather than coerced.

Agent headshots are resolved by exact `dropbox_id`, not shortlisted by filename. Require `media_type=image`, `approved_for=agent-footer`, and the `/20. People/In-house Agents/` path boundary. Diego Ojeda likeness references use `image-generation-reference` and are never valid agent-footer assets.

## Selection Criteria

Choose images that support:

- Campaign goal
- Audience
- Desired tone
- Visual hierarchy
- Project accuracy
- Premium architectural feel

Avoid overusing near-duplicate images. For event recaps, prefer a mix of turnout, people, building/progress, and strong hero candidates.

Map the campaign brief to explicit selector inputs:

- `--media-type`: `image` for email imagery or `pdf` for an approved document.
- `--approved-for`: required approval labels, such as `email_hero`, `email_body`, `event`, or `attachment`, matching the manifest exactly.
- `--category`: desired overlaps such as exterior, amenity, residence, event, lifestyle, map, or floorplan.
- `--orientation`: desired orientation when manifest metadata is available. Missing orientation is not invented.

Use the returned score and reasons to explain recommendations. Duplicate filenames must be identified by Dropbox ID and path, not by filename alone.

## Approval And Selection

Return a compact shortlist for user or LLM review. Show filename, Dropbox path or ID, category, `approved_for`, orientation, public URL, score, and reasons.

If `review_required` is true, or if several materially different top candidates remain, ask for approval before selecting a final image. Do not silently choose among different viable hero or campaign-defining assets.

Only selected and approved assets should be downloaded or copied into a campaign workspace. Do not download rejected candidates, unused alternates, or the whole source library.

## Packaging Rule

Track each selected image as soon as it enters the final design. At delivery, copy every final used image into the campaign package and record its source, packaged filename, role, and HTML variants in the asset manifest. Never move, rename, or modify the corpus original.

Do not package rejected candidates, unused alternates, or the whole source folder. Include only final images referenced by at least one delivered HTML file, plus any explicitly requested alternates.

## When To Use The Image Workflow

Hand off to `onbrand-the-rider-image` when an image must be created, composited, or edited. Generated or edited imagery remains a separate explicit workflow even when the email skill has already selected existing approved assets.
