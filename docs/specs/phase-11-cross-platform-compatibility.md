# Phase 11: Cross-Platform Compatibility

**Status:** Approved specification, not implemented
**Target:** 0.9.0
**Depends on:** Phases 7-10

## Goal

Create a vendor-neutral campaign-production core with thin Codex and Claude Code adapters that produce equivalent campaign specifications and deterministic runtime output.

## Non-Goals

- Do not claim Claude Code support is implemented before parity tests pass.
- Do not put Claude-only frontmatter or dynamic shell/context features into canonical shared skills.
- Do not fork project logic between platforms.

## Requirements

- COMPAT-001: Define a canonical core consisting of Markdown/reference data, JSON contracts, Python runtime, asset/image plans, QA, and packaging.
- COMPAT-002: Codex and Claude Code adapters write the same campaign specification and invoke the same runtime.
- COMPAT-003: Claude Code project skills live at `.claude/skills/<name>/SKILL.md`.
- COMPAT-004: Claude Code skills preserve manual-only invocation with `disable-model-invocation: true`.
- COMPAT-005: Canonical/shared skills use portable Agent Skills fields only.
- COMPAT-006: Claude-only frontmatter stays in the Claude adapter.
- COMPAT-007: Adapters document installation, explicit invocation, path/env handling, tool fallback, and output parity tests.
- COMPAT-008: Explicit-only invocation remains required in both Codex and Claude Code.

## Anticipated Data And Contracts

- `campaign.runtime.json`: canonical campaign input.
- `composition_plan.json`, `image_plan.json`, and content allocation plan.
- Adapter metadata for Codex and Claude Code installation paths.
- Parity report comparing outputs from both adapters.

## Workflow

1. Identify portable core instructions and platform-specific adapter instructions.
2. Move platform-neutral behavior into shared references and runtime contracts.
3. Create Codex adapter packaging rules.
4. Create Claude Code adapter packaging rules with `.claude/skills/<name>/SKILL.md`.
5. Run the same approved campaign through both adapters.
6. Compare campaign JSON, asset manifest, QA report, HTML variant list, and ZIP structure.

## Acceptance Criteria

- Both platforms generate byte-equivalent campaign JSON for the same approved inputs, or documented equivalent JSON with stable semantic diff.
- Runtime output parity is verified for at least one representative campaign.
- Claude Code documentation references official skill location and invocation controls without claiming unimplemented support.
- Platform-specific metadata does not leak into shared portable skill content.

## Tests And Evidence Required

- Adapter install smoke checks.
- Explicit invocation checks for both environments.
- Output parity fixtures.
- Documentation link check for official Claude references.

## Dependencies

- Stable build-mode contracts.
- Stable composition, image, and copy allocation plans.
- Existing deterministic runtime.

## Risks

- Codex and Claude Code expose different tool affordances, permissions, and runtime assumptions.
- Claude Code manual invocation semantics may change with product updates.
- Keeping adapters thin requires discipline when adding platform-specific conveniences.

## Out Of Scope

- Broker-only sanitization.
- Private repository split.
- Cloud-hosted deployment of campaign images.
