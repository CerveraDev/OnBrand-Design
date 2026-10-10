# Project Packages

Each directory is an isolated project-specific OnBrand Design pack. Campaign execution requires the shared core; a folder alone is not a standalone runtime. See [cross-platform installation](../docs/COMPATIBILITY.md). Restricted distribution profiles remain deferred.

## Required Structure

```text
project-slug/
|-- README.md
|-- LICENSE
|-- NOTICE
|-- AUTHORS.md
|-- THIRD_PARTY_NOTICES.md
|-- project.json
|-- profile.json
|-- adapter.json
`-- skills/
    |-- onbrand-project-slug-email/
    `-- onbrand-project-slug-image/
```

The email and image skill IDs must include the same project slug. Both skills must remain explicit-only. Every standalone package retains the Apache-2.0 license, notice, authorship, and research-attribution files. Project-specific brands, asset manifests, templates, footer partials, campaign examples, and generated outputs belong inside or alongside that project package; they must not be copied into another project.

## Add A Project

Run the generator from the repository root:

```bash
python3 scripts/create_project.py --name "Project Name" --slug project-name
```

The generator renders `templates/project-starter/`, creates `project.json`, and adds the project to `registry.json`.

## Project Profile

`profile.json` is where the project's admin records the facts every skill can reuse: `official_name`, `nickname`, `phone`, `email`, `sales_gallery_address` and `project_site_address` (each a list of address lines), and under `social` the `instagram_handle` (the handle alone, without `@`) and `avatar` (a PNG or JPEG path relative to the project folder). Leave a field `null` until it is known. More fields may be added; readers keep the ones they do not recognise. The social runtime reads it for the feed simulator's account name and picture. After generation, calibrate the scaffold with that project's approved HTML, brand materials, footer partials, and asset-manifest location.

Do not create a project by copying an existing branded project. That can silently carry campaign assumptions or another property's identity into the new package.
