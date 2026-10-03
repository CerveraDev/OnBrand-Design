# OnBrand Design

OnBrand Design is an open, reusable framework for creating project-specific real estate email-production skills. Each project package keeps its own brand, asset catalog, templates, footers, campaign rules, and explicit invocation names isolated from every other development.

**Owner:** Cervera Real Estate, Inc.  
**Author:** Felix Mendoza  
**License:** Apache-2.0  
**Current version:** 0.1.0

## Project Model

OnBrand Design is the umbrella product. Every real estate development receives a self-contained folder under `projects/`:

```text
projects/
|-- the-rider/
|   |-- project.json
|   `-- skills/
|       |-- onbrand-the-rider-email/
|       `-- onbrand-the-rider-image/
|-- cassia/
|   |-- project.json
|   `-- skills/
|       |-- onbrand-cassia-email/
|       `-- onbrand-cassia-image/
`-- registry.json
```

The technical IDs include the project slug so multiple OnBrand Design projects can be installed together without invocation collisions.

## Current Projects

- **The Rider:** first implementation; revised Beefree scaffold calibration, separate header/hero metadata, locked optional static blocks, Composition Preview approval plans, grounded generated-image provenance, deterministic HTML assembly, explicit build modes, footer variants, portable asset packaging, and blocking QA are implemented.
- **Cassia:** generated project scaffold awaiting Cassia-specific brand assets, templates, footers, and asset catalog.

## Create Another Project

```bash
python3 scripts/create_project.py --name "Project Name" --slug project-name
```

The generator creates a complete project folder from `templates/project-starter/`, assigns unique explicit-invocation IDs, and registers the project. Generated brand guidance remains provisional until calibrated from that project's approved materials.

## Project Documents

- [Product requirements](docs/PRD.md)
- [Current status](STATUS.md)
- [Roadmap](ROADMAP.md)
- [Limitations register](LIMITATIONS.md)
- [Audit log](AUDIT_LOG.md)
- [Versioning policy](VERSIONING.md)
- [Project registry](projects/registry.json)
- [Project folder contract](docs/PROJECT_STRUCTURE.md)
- [Credential policy](docs/CREDENTIALS.md)
- [Compatibility plan](docs/COMPATIBILITY.md)
- [Distribution security plan](docs/DISTRIBUTION_SECURITY.md)
- [Project package guide](projects/README.md)
- [Contribution workflow](CONTRIBUTING.md)
- [Authorship](AUTHORS.md)
- [Legal notice](NOTICE)
- [Third-party research notices](THIRD_PARTY_NOTICES.md)
- [Apache License 2.0](LICENSE)

## Shared Tooling

`tools/dropbox-manifest/` maintains a project's master image/PDF catalog. Credentials remain in an untracked local `.env`. The tool is shared at the repository level; project-specific runtime skills consume their configured public manifest without receiving private Dropbox credentials.

`tools/asset_selection/` validates a local master manifest, validates project manifest-source configuration, and returns deterministic, explained asset shortlists for project email skills. It does not refresh Dropbox, require credentials, download source assets, or choose a final campaign image without approval when top candidates are materially different.

`tools/rider_campaign_runtime/` validates Rider campaign JSON, generates Composition Preview catalog/plan artifacts, validates grounded image provenance and approved copy allocation, blocks unintended cross-surface repetition before rendering, composes approved scaffold modules, applies explicit build-mode variant policy, packages only used images, runs blocking QA, and creates a portable ZIP. See its [runtime guide](tools/rider_campaign_runtime/README.md).

## Security

Never commit `.env`, Dropbox tokens, app secrets, virtual environments, generated campaign packages, private campaign inputs, or unapproved project assets.

## Public Reuse And License

The OnBrand Design source framework is licensed under the [Apache License 2.0](LICENSE). Project names, trademarks, logos, photographs, renderings, templates, and other campaign assets may carry separate rights and are not automatically licensed merely because they appear in or are referenced by a project package. See [NOTICE](NOTICE).

## Repository

The public source repository is [CerveraDev/OnBrand-Design](https://github.com/CerveraDev/OnBrand-Design). Project trademarks and assets remain subject to the rights described in [NOTICE](NOTICE).
