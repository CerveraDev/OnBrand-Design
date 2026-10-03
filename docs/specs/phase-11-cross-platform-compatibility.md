# Phase 11: Cross-Platform Compatibility

**Status:** Deterministic implementation/parity complete; live Codex/Claude agent invocation unverified
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
- [Committed report](../evals/phase-11-parity-report.json) passes 13 critical components at 100; [evaluation](../evals/phase-11-cross-platform-compatibility.md) separates that evidence from unverified live behavior.

### Reconciled Phase 11 Gates

- COMPAT-009: Versioned request/project contracts identify core, adapter, project, runtime, and campaign schema; reject unsupported versions and unknown fields.
- COMPAT-010: A HUMAN invocation record plus explicit dispatch flag is mandatory. This is an attestation, not an authentication/security boundary.
- COMPAT-011: One approved campaign JSON is authoritative. Optional brief/selection/approval files are checksum-bound; separate composition/image/copy files must equal their embedded canonical sections. No approvals or text are synthesized.
- COMPAT-012: Emit/build adapters use the shared runtime API; provenance stays in a separate sidecar outside the campaign folder and ZIP.
- COMPAT-013: Codex wrappers live under `.agents/skills`, Claude wrappers under `.claude/skills`; canonical project skills contain no Claude-only fields. Project IDs remain collision-safe.
- COMPAT-014: CLI, Codex, and Claude deterministic runs compare campaign, build, variants, composition, image provenance, copy owners/claims/reuse/scoring, HTML hashes, asset identity/checksums, complete metadata, QA checks/outcomes, ZIP inventory/bytes, integrity, and adapter provenance.
- COMPAT-015: All critical components require 100%; a mean score cannot override a failure. Only named normalizations in the compatibility contract are allowed; missing components, extra fields, nonpassing QA, stale/tampered ZIPs, and unexplained differences fail.
- COMPAT-015a: JSON comparison is recursively type-sensitive across every parity component and approval/selection boundary. Boolean/number/null/string/array/object distinctions must survive; object key order may differ. Finite numbers compare by their parsed value (1 = 1.0; 0 = -0.0), without tolerance; non-finite values fail. Semantic comparison and report/inventory hashing use the same representation, so equal values cannot report differing semantic hashes. Explicit numeric semantics and precision boundaries are documented in the compatibility guide.
- COMPAT-016: Realistic evidence independently rebuilds the Phase 10 Rider preview with checksum-verified cached real asset bytes. Cached transport is evaluation-only, not mocked rendering/QA and not live model equivalence.
- COMPAT-017: Installed CLI/authentication and bounded manual agent checks are reported separately. No installation, login, credential disclosure, or claim of unobserved live Claude behavior.
- COMPAT-018: Cassia/future scaffolds install references but reject builds until their own runtime/calibration is registered. Phase 12 distribution remains deferred.

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
