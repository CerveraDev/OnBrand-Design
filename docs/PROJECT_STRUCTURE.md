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
- `adapter.json` with versioned core/adapter/project/runtime binding; null-runtime scaffolds are reference-only.
- `LICENSE`, `NOTICE`, `AUTHORS.md`, and `THIRD_PARTY_NOTICES.md` so the package retains its license and attribution when distributed independently.
- `skills/onbrand-<slug>-email/` for strategy, copy, asset selection, HTML, variants, packaging, and QA.
- `skills/onbrand-<slug>-image/` for separately invoked image generation and editing.
- A project README explaining invocation and calibration status.

Project folders may later add approved brand assets, template fixtures, locked footer partials, manifest configuration, tests, and release packages. Those additions must remain specific to that project.

## Invocation Contract

Skill IDs include the project slug. Canonical frontmatter remains portable. Codex workspace wrappers at `.agents/skills` set `policy.allow_implicit_invocation: false` in `agents/openai.yaml`; only Claude wrappers at `.claude/skills` set `disable-model-invocation: true`. Ordinary requests must not activate skills automatically. See [adapter installation](COMPATIBILITY.md).

## Distribution Contract

A pack must not depend on another project folder, but campaign execution requires the shared core. Keep references with the project and runtime logic in the core; do not copy rules into adapters or claim a project folder includes the shared runtime. Phase 12 sanitized/restricted distribution stays deferred.

## Isolation Checks

Before release:

1. Search the project for names and technical IDs belonging to other projects.
2. Confirm both skill IDs use the project's registered slug.
3. Confirm project-specific assets and footer partials are not shared by path with another project.
4. Confirm no credentials, private `.env`, source corpus, or generated campaign package is tracked.
5. Validate the project metadata, YAML frontmatter, links, and explicit-invocation policies.
