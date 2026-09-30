# Project Folder Contract

OnBrand Design supports an unbounded number of isolated real estate projects. The repository contains shared governance and tooling, while every runtime skill remains project-specific.

## Repository Boundary

- `projects/` contains distributable project packages.
- `templates/project-starter/` is the neutral source used to create new projects.
- `scripts/create_project.py` renders and registers a new project.
- `tools/` contains shared development utilities and no project credentials.
- `docs/`, `STATUS.md`, `ROADMAP.md`, and `AUDIT_LOG.md` govern the framework portfolio.

## Project Boundary

Every `projects/<slug>/` directory must contain:

- `project.json` with framework, owner, author, lifecycle, calibration, and skill-ID metadata.
- `LICENSE`, `NOTICE`, and `AUTHORS.md` so the package retains its license and attribution when distributed independently.
- `skills/onbrand-<slug>-email/` for strategy, copy, asset selection, HTML, variants, packaging, and QA.
- `skills/onbrand-<slug>-image/` for separately invoked image generation and editing.
- A project README explaining invocation and calibration status.

Project folders may later add approved brand assets, template fixtures, locked footer partials, manifest configuration, tests, and release packages. Those additions must remain specific to that project.

## Invocation Contract

Skill IDs are globally unique because they include the project slug. Codex metadata must set `policy.allow_implicit_invocation: false`; Claude-compatible skill frontmatter must set `disable-model-invocation: true`. Ordinary email or image requests must not activate a project skill automatically.

## Distribution Contract

A project folder is intended to be downloadable on its own. It must not depend on another project folder. Shared repository tools may prepare or validate a project, but runtime project behavior and project-specific references must travel with that project.

## Isolation Checks

Before release:

1. Search the project for names and technical IDs belonging to other projects.
2. Confirm both skill IDs use the project's registered slug.
3. Confirm project-specific assets and footer partials are not shared by path with another project.
4. Confirm no credentials, private `.env`, source corpus, or generated campaign package is tracked.
5. Validate the project metadata, YAML frontmatter, links, and explicit-invocation policies.
