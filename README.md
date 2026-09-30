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

- **The Rider:** first implementation; workflow and Dropbox catalog foundations are active, while canonical Beefree HTML and locked footer integration remain pending.
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
- [Audit log](AUDIT_LOG.md)
- [Versioning policy](VERSIONING.md)
- [Project registry](projects/registry.json)
- [Project folder contract](docs/PROJECT_STRUCTURE.md)
- [Project package guide](projects/README.md)
- [Contribution workflow](CONTRIBUTING.md)
- [Authorship](AUTHORS.md)
- [Legal notice](NOTICE)
- [Apache License 2.0](LICENSE)

## Shared Tooling

`tools/dropbox-manifest/` maintains a project's master image/PDF catalog. Credentials remain in an untracked local `.env`. The tool is shared at the repository level; project-specific runtime skills consume their configured public manifest without receiving private Dropbox credentials.

## Security

Never commit `.env`, Dropbox tokens, app secrets, virtual environments, generated campaign packages, private campaign inputs, or unapproved project assets.

## Public Reuse And License

The OnBrand Design source framework is licensed under the [Apache License 2.0](LICENSE). Project names, trademarks, logos, photographs, renderings, templates, and other campaign assets may carry separate rights and are not automatically licensed merely because they appear in or are referenced by a project package. See [NOTICE](NOTICE).

## GitHub Readiness

The directory is structured for GitHub but has not been initialized, committed, connected to a remote, or pushed. Repository URL, visibility, support contact, and GitHub owner/organization remain release decisions.
