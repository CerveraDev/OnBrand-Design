# Project Packages

Each directory in this folder is a self-contained OnBrand Design implementation for one real estate project. A project folder is the unit that can be distributed to a team or installed independently.

## Required Structure

```text
project-slug/
|-- README.md
|-- LICENSE
|-- NOTICE
|-- AUTHORS.md
|-- project.json
`-- skills/
    |-- onbrand-project-slug-email/
    `-- onbrand-project-slug-image/
```

The email and image skill IDs must include the same project slug. Both skills must remain explicit-only. Every standalone package retains the Apache-2.0 license, notice, and authorship files. Project-specific brands, asset manifests, templates, footer partials, campaign examples, and generated outputs belong inside or alongside that project package; they must not be copied into another project.

## Add A Project

Run the generator from the repository root:

```bash
python3 scripts/create_project.py --name "Project Name" --slug project-name
```

The generator renders `templates/project-starter/`, creates `project.json`, and adds the project to `registry.json`. After generation, calibrate the scaffold with that project's approved HTML, brand materials, footer partials, and asset-manifest location.

Do not create a project by copying an existing branded project. That can silently carry campaign assumptions or another property's identity into the new package.
