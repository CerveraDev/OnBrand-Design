# Campaign Distribution Package

Every completed Rider campaign must be delivered as both an ordinary folder and a ZIP archive of that folder. The package must be self-contained for internal review and easy handoff to the user's team.

## Required Structure

```text
campaign-slug/
|-- html/
|   |-- campaign-slug-branded.html
|   |-- campaign-slug-outside-broker-customizable.html
|   `-- campaign-slug-agent-name.html
|-- images/
|   |-- hero.jpg
|   `-- supporting-image.jpg
|-- documents/
|   `-- selected-supporting-document.pdf
|-- asset-manifest.json
|-- campaign-metadata.json
`-- qa-report.json
```

Composition Preview and ordinary Smoke Test builds render one representative HTML file. Release Build renders the full internal matrix, including one agent HTML file for each active in-house agent record. Use concise lowercase filenames with hyphens. The final ZIP must be named `campaign-slug.zip` and contain the top-level `campaign-slug/` directory.

`campaign-metadata.json` preserves the approved subject line, preview text, ordered modules, approved composition plan summary, generated-image workflow summary when present, build mode, representative variant, effective variant scope, expansion reason, and complete rendered variant list for handoff.

Create `documents/` only when the approved campaign explicitly selects one or more PDFs by manifest asset ID. Each PDF must be approved for body use and is recorded in the same asset manifest with checksum provenance.

## Image Collection

- Copy every final image referenced by at least one delivered HTML file into `images/`.
- Copy assets; never move, rename, overwrite, or otherwise modify corpus originals.
- Include approved generated or edited images used in the final design.
- Record generated or edited image provenance through `image_workflow`; ordinary manifest selections remain `asset_id` slots.
- Include footer or logo images when the delivered HTML depends on local copies of them.
- Store a shared image once even when every HTML variant references it.
- Exclude unused corpus images, rejected generation candidates, and temporary working files unless the user explicitly requests them.
- Preserve the final file format and useful resolution unless optimization is required and approved.

## HTML References

For the portable preview set, use relative references from `html/` to `images/`, for example `../images/hero.jpg`. Do not leave absolute filesystem paths or source-corpus paths in delivered HTML.

Relative image paths are suitable for package review but usually must become hosted URLs or platform-managed assets before a deployed email is sent. If final hosted URLs are available, the package may also include a deployment-ready HTML set. Do not invent hosting URLs.

## Asset Manifest

Create `asset-manifest.json` with:

- Campaign slug and title
- Each packaged image filename
- Image role, such as hero, logo, gallery, or footer
- Original source URL, canonical manifest identity, and Dropbox path when applicable
- HTML variants that use it
- Relative package path
- SHA-256 checksum and byte size
- `image_workflow_id` for packaged generated or edited outputs

When generated or edited imagery is used, `asset-manifest.json` also records the approved `image_workflow` summary so source assets, prompt records, output checksum/dimensions, and placement constraints travel with the package.

Use valid JSON and stable relative paths. Do not include secrets or inaccessible temporary URLs.

## Validation

Before creating the ZIP:

1. Confirm the selected build mode and effective variant scope match the request.
2. Enumerate every `src`, CSS background image, and other image reference in every HTML file.
3. Confirm each local reference resolves inside the package.
4. Confirm every packaged image is either referenced or explicitly requested as an alternate.
5. Confirm no HTML references an absolute local path, source-corpus path, or temporary directory.
6. Confirm the manifest matches the files and usage.
7. Confirm generated or edited images have approved workflow records, valid source assets, matching output checksums/dimensions, and valid intended module/slot references.
8. Open representative HTML variants from the package and verify that images render.
9. Create the ZIP only after the folder passes these checks.

The Rider runtime performs these checks and writes `qa-report.json`. A blocked report prevents ZIP creation. Generate the package with `python3 -m tools.rider_campaign_runtime.cli <campaign.json>` rather than assembling delivery files manually.

If an external asset cannot legally or technically be copied, leave its approved external URL intact and identify it clearly in the manifest. Do not claim the package is fully self-contained in that case.
