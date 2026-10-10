# Social Runtime

Phase 17 sibling of `tools/rider_campaign_runtime/`. It builds reviewable static-post and carousel packages from a canonical social spec, the project's social approval overlay, and templates that sequence the frames of the project's social scaffold. It imports nothing from the email runtime and never reads `data/agents/`.

```bash
python3 -m tools.social_runtime.cli build --spec projects/the-rider/social/examples/feature-carousel.preview.json
```

Exit code 0 means blocking QA passed, 1 means QA failed, and 2 means the build was refused before packaging, with the specific reason on stderr.

## What a build produces

`<output_dir>/<slug>/` holds `social-package.json` (slides, copy, and image references per variant), `asset-manifest.json` (used records and crop provenance, without Dropbox identifiers or paths), `preview.html` (a review sheet), and `qa-report.json`. A ZIP is written only when QA passes and the mode is not `smoke-test`.

The runtime does not render pixels. It does not crop images or composite on-image text; it records where approved text and approved images go. See LIM-023.

## Inputs

| Input | Location |
|---|---|
| Format sidecar | `tools/social_runtime/platform-formats.json` |
| Templates | `projects/<slug>/social/templates/<CODE>.json` |
| Frame definitions | `projects/<slug>/social/templates/frames.json`, generated from `social/scaffold/frame-catalog.json` |
| Social approvals | `projects/<slug>/asset-approvals.social.json` |
| Manifest | the `local_cache_path` in `projects/<slug>/manifest-source.json` |

## Frames and templates

A frame is one slide layout from the owner's scaffold: its image slots with their sizes and shapes, its text slots with draft line and character limits, and its locked content such as the logo. A template says which frames may appear at each position. Each slide in a spec names its `frame` and fills every image slot under `images` and every text slot under `text`.

After the scaffold is re-imported with `tools/social_scaffold/import_scaffold.cjs`, regenerate the definitions; a test fails while they are out of date:

```bash
python3 -m tools.social_runtime.cli frames --project the-rider
```

An image slot takes a directly approved asset only when the asset's orientation equals the slot's shape. Any other use needs a declared crop whose geometry matches the slot and whose output is the slot's size in export pixels. Every image slot cover-fits its image. 4:5 formats export at 1200x1500, the scaffold canvas at 2x.

### Supplied images

A template whose `image_sources` lists `user-supplied` lets a slide take a local file that is not in the approved catalog, which is how event photography reaches the gallery template `GAL-01`:

```json
"images": {"image-1": {"supplied": "~/Pictures/top-off/crowd-toast.jpg"}}
```

The path may be absolute or relative to the spec. The file must be a PNG or JPEG whose orientation, after the JPEG EXIF orientation tag is applied, equals the slot's shape. It is copied into the package as `images/supplied-<hash>` and listed under `supplied` in `asset-manifest.json`; the original path is not recorded. A supplied image is not an owner-approved record: every build that uses one carries a warning that rights and approval rest with the person who supplied it, and an image smaller than its slot is reported as enlarged.

## Build modes

| Mode | Variants built | Draft template, draft copy, unverified format, planned crop | ZIP |
|---|---|---|---|
| `composition-preview` | Representative only | Allowed, reported as warnings | Yes |
| `smoke-test` | All | Draft copy and planned crops refused | Never |
| `release` | All | All refused | Yes |

An `outside-broker` build needs an approved template that lists that audience, resolves images only from the filtered broker catalog, and cannot declare `cross_medium`.

## Modules

- `schema.py`: spec shape validation, no file access.
- `formats.py`: the pinned sidecar; an absent format fails rather than defaulting.
- `frames.py`: frame definitions derived from the scaffold catalog, with estimated draft text limits.
- `templates.py`: frame sequences with audience availability; resolves each slide to its frame.
- `assets.py`: resolution against the overlay, and the broker-safe catalog filter.
- `supplied.py`: format and orientation checks for an image supplied outside the approved catalog.
- `crops.py`: provenance validation, against the image slot it fills, for a crop produced elsewhere.
- `copy_allocation.py`: one approved owner per text surface, in-carousel repetition, and cross-medium repetition against an email campaign spec.
- `qa.py`, `runtime.py`, `cli.py`: blocking QA, packaging, and the command line.
