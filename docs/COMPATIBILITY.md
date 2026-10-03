# Compatibility Plan

**Status:** Approved specification, not implemented
**Updated:** 2026-10-03

## Purpose

OnBrand Design should produce equivalent campaign specifications and deterministic runtime output from Codex and Claude Code without duplicating project logic.

## Canonical Core

The canonical core is vendor-neutral:

- Markdown references and project rules.
- JSON campaign, composition, image, and copy-allocation contracts.
- Python runtime and package builder.
- Asset selection, image provenance, QA, and ZIP packaging.
- Documentation and fixtures that can be exercised outside a single agent surface.

Adapters may guide a platform-specific agent, but they must write the same canonical campaign specification and call the same deterministic runtime.

## Codex Adapter

Codex support is the current implemented path. Existing project skills remain explicit-only and continue to use repository-local references, runtime tools, and package QA.

Expected Codex behavior:

- User invokes the project-specific skill explicitly.
- The adapter reads project references progressively.
- The adapter writes canonical JSON plans/specs.
- The adapter calls the shared runtime.
- The adapter reports package paths, QA, and limitations.

## Claude Code Adapter

Claude Code support is planned, not implemented.

Official references:

- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Anthropic Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

Planning assumptions from official docs:

- Project skills can live at `.claude/skills/<skill-name>/SKILL.md`.
- Claude Code skills use `SKILL.md` with YAML frontmatter and Markdown instructions.
- `disable-model-invocation: true` is the planned control for manual-only invocation.
- Claude Code custom skills are filesystem-based and distinct from claude.ai/API skill uploads.

Expected Claude Code behavior after implementation:

- User invokes the adapter manually with `/skill-name`.
- Claude-only frontmatter stays in `.claude/skills/<name>/SKILL.md`.
- The shared/canonical skill content avoids Claude-only fields and dynamic shell/context features.
- The adapter writes the same canonical campaign specification and calls the same runtime.

## Capability Matrix

| Capability | Codex current | Claude Code planned | Canonical core |
|---|---|---|---|
| Explicit project invocation | Implemented | Planned | Required |
| Campaign JSON runtime | Implemented | Reused | Implemented |
| Composition Preview | Planned | Planned | Planned |
| Grounded image plan | Planned | Planned | Planned |
| Package QA and ZIP | Implemented | Reused | Implemented |
| Platform-specific skill metadata | Codex skill metadata | Claude frontmatter | Excluded |
| Output parity validation | Not yet required | Planned | Required before support claim |

## Portability Constraints

- Keep platform-specific metadata out of shared references.
- Do not depend on a platform-only shell variable in canonical instructions.
- Do not assume identical network, filesystem, or browser permissions.
- Treat local credentials and ignored manifests as maintainer tools, not portable skill inputs.
- Use relative repository paths in specs where possible and resolve them through the runtime.

## Planned Parity Validation

Before claiming Claude Code support:

1. Install the Claude adapter at `.claude/skills/<name>/SKILL.md`.
2. Invoke it manually.
3. Generate the same representative campaign spec as Codex from the same approved inputs.
4. Run the shared runtime.
5. Compare campaign JSON, campaign metadata, HTML variant list, asset manifest, QA report, and ZIP integrity.
6. Record any accepted semantic differences.

Until that validation passes, Claude Code support remains planned only.
