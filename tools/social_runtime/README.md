# Social Runtime

Phase 17 sibling of `tools/rider_campaign_runtime/`. It builds reviewable static-post and carousel packages from a canonical social spec, the project's social approval overlay, and data-file templates. It imports nothing from the email runtime and never reads `data/agents/`.

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
| Social approvals | `projects/<slug>/asset-approvals.social.json` |
| Manifest | the `local_cache_path` in `projects/<slug>/manifest-source.json` |

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
- `templates.py`: slide-sequenced templates with typed slots, locked content, and audience availability.
- `assets.py`: resolution against the overlay, and the broker-safe catalog filter.
- `crops.py`: provenance validation for a crop produced elsewhere.
- `copy_allocation.py`: one approved owner per text surface, in-carousel repetition, and cross-medium repetition against an email campaign spec.
- `qa.py`, `runtime.py`, `cli.py`: blocking QA, packaging, and the command line.
