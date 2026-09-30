# Campaign Distribution Package

Every completed Cassia campaign must be delivered as both an ordinary folder and a ZIP archive of that folder. The package must be self-contained for internal review and easy handoff to the user's team.

## Required Structure

```text
campaign-slug/
|-- html/
|   |-- campaign-slug-branded.html
|   |-- campaign-slug-broker-neutral.html
|   `-- campaign-slug-agent-name.html
|-- images/
|   |-- hero.jpg
|   `-- supporting-image.jpg
`-- asset-manifest.json
```

Create one agent HTML file for each available in-house agent footer. Use concise lowercase filenames with hyphens. The final ZIP must be named `campaign-slug.zip` and contain the top-level `campaign-slug/` directory.

## Image Collection

- Copy every final image referenced by at least one delivered HTML file into `images/`.
- Copy assets; never move, rename, overwrite, or otherwise modify corpus originals.
- Include approved generated or edited images used in the final design.
- Include footer or logo images when the delivered HTML depends on local copies of them.
- Store a shared image once even when every HTML variant references it.
- Exclude unused corpus images, rejected generation candidates, and temporary working files unless the user explicitly requests them.
- Preserve the final file format and useful resolution unless optimization is required and approved.

## HTML References

For the portable preview set, use relative references from `html/` to `images/`, for example `../images/hero.jpg`. Do not leave absolute filesystem paths or source-corpus paths in delivered HTML.

Relative image paths are suitable for package review but usually must become hosted URLs or platform-managed assets before a deployed email is sent. If final hosted URLs are available, the package may also include a deployment-ready HTML set. Do not invent hosting URLs.

## Asset Manifest

Create `asset-manifest.json` with:

- Campaign name and package creation date
- Each packaged image filename
- Image role, such as hero, logo, gallery, or footer
- Original source path or source identifier
- Whether the image is original, selected, generated, or edited
- HTML variants that use it
- Relative package path
- Final hosted URL when known
- Notes about licensing, approval, or required deployment replacement when relevant

Use valid JSON and stable relative paths. Do not include secrets or inaccessible temporary URLs.

## Validation

Before creating the ZIP:

1. Enumerate every `src`, CSS background image, and other image reference in every HTML file.
2. Confirm each local reference resolves inside the package.
3. Confirm every packaged image is either referenced or explicitly requested as an alternate.
4. Confirm no HTML references an absolute local path, source-corpus path, or temporary directory.
5. Confirm the manifest matches the files and usage.
6. Open representative HTML variants from the package and verify that images render.
7. Create the ZIP only after the folder passes these checks.

If an external asset cannot legally or technically be copied, leave its approved external URL intact and identify it clearly in the manifest. Do not claim the package is fully self-contained in that case.
