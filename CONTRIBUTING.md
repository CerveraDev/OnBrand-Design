# Contribution Workflow

## Branches

Use short branches tied to a phase or issue, such as `phase-1-asset-selection` or `fix-manifest-rename-matching`.

## Commits

Keep commits focused and use imperative subjects. Suggested prefixes:

- `feat:` new behavior
- `fix:` defect correction
- `docs:` documentation only
- `test:` test coverage
- `chore:` maintenance without product behavior changes

Never commit `.env`, Dropbox credentials, virtual environments, generated campaign packages, or private campaign inputs.

Follow [docs/CREDENTIALS.md](docs/CREDENTIALS.md) for GitHub authentication, Dropbox refresh configuration, automation secrets, and rotation.

## Project Folders

Create new developments with `scripts/create_project.py`. Do not duplicate and hand-rename an existing project folder, because that can leak project-specific brand rules or produce invocation collisions.

Generated projects must keep unique `onbrand-<project-slug>-email` and `onbrand-<project-slug>-image` IDs. Calibrate each generated project from its own approved materials before marking it active.

## Pull Requests

Every pull request should:

1. Identify its roadmap phase and requirement IDs.
2. Explain user-visible behavior and compatibility effects.
3. List verification performed.
4. Update `STATUS.md` when progress changes.
5. Append `AUDIT_LOG.md` for material decisions or operational events.
6. Update `CHANGELOG.md` when release behavior changes.
7. Avoid changing locked assets or curated manifest fields without explicit authorization.
8. Check that changes to shared templates do not introduce one project's branding into another project.

## Definition Of Done

- Acceptance criteria for the relevant phase are satisfied.
- Changed scripts compile and their meaningful behavior is tested.
- Skill references are reachable from `SKILL.md` when required at runtime.
- Explicit-only invocation remains intact.
- No secret, private path, or unapproved asset is included.
- Project registry and metadata remain valid and collision-free.
