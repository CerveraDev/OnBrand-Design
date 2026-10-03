# Phase 7: Build Modes

**Status:** Implemented for The Rider runtime
**Target:** 0.8.0
**Depends on:** Phases 5 and 6

## Goal

Separate campaign production into explicit build modes so routine composition work stays fast, smoke tests stay technical, and release builds remain complete and traceable.

## Non-Goals

- Do not remove the existing smoke-test terminology from runtime and QA.
- Do not implement broker-only distribution profiles in this phase.
- Do not change current output contracts until the runtime mode contract is implemented and tested.

## Requirements

- MODE-001: Define three build modes: Composition Preview, Smoke Test, and Release Build.
- MODE-002: Composition Preview generates one representative version for user review.
- MODE-003: Ordinary smoke tests generate one representative version unless agent, footer, or scaffold footer data changed, or the user explicitly requests every variant.
- MODE-004: Release Build generates every authorized distribution variant for internal use.
- MODE-005: Full agent variant regeneration remains mandatory when roster data, footer rendering, scaffold footer rows, or footer asset resolution changes.
- MODE-006: Build output metadata records the selected mode, representative variant, and variant-expansion reason.
- MODE-007: Existing automated smoke tests keep the term "smoke test"; user-facing selection work uses "Composition Preview" or "Design Proof."

## Anticipated Data And Contracts

- `build.mode`: `composition-preview`, `smoke-test`, or `release-build`.
- `build.representative_variant`: `branded`, `outside-broker-customizable`, or `agent-<agent-id>`.
- `variant_policy`: `single`, `all`, or `changed-surface-expanded`.
- `changed_surfaces`: explicit values such as `agent-roster`, `agent-data`, `agent-footer-assets`, `footer-renderer`, `footer-data`, or `scaffold-footer-structure`.
- `expansion_reason`: human-readable reason when a non-release build expands to all variants.

## Implementation Evidence

- The Rider runtime schema requires an explicit `build` object.
- Composition Preview and ordinary Smoke Test render one representative variant by default.
- The default representative is `branded`; callers can explicitly choose `outside-broker-customizable` or `agent-<agent-id>`.
- Smoke Test expands to all authorized variants only with `variant_policy: "all"` or `variant_policy: "changed-surface-expanded"` plus a non-empty valid `changed_surfaces` array.
- Release Build requires the full internal matrix and renders branded, outside-broker customizable, and one variant per active in-house agent.
- `campaign-metadata.json` and `qa-report.json` record mode, representative variant, effective variant scope, changed surfaces, expansion reason, and rendered variants.

## Workflow

1. Determine whether the user is asking for selection, technical validation, or final distribution.
2. Select the build mode explicitly before rendering.
3. For Composition Preview, render only the chosen representative variant after the module and asset approvals are complete.
4. For Smoke Test, render one representative variant unless the changed surface requires footer or roster expansion.
5. For Release Build, render every authorized variant and package the full deliverable.
6. Record the mode and variant policy in campaign metadata and QA.

## Acceptance Criteria

- A copy-only campaign preview no longer generates every agent variant by default.
- A footer-data change still exercises all in-house agent variants during testing.
- Release Build output remains equivalent to the current full internal package behavior.
- User-facing documentation explains the difference between Composition Preview and Smoke Test.

## Tests And Evidence Required

- Unit tests for mode parsing and variant-policy decisions.
- Runtime tests proving representative-only and all-variant paths.
- QA metadata snapshots for each mode.
- Documentation examples showing when all variants regenerate.

## Dependencies

- Existing runtime variant generator.
- Campaign metadata writer.
- QA report schema.

## Risks

- A representative-only smoke could miss agent-footer regressions if expansion rules are too narrow.
- Users may confuse a Composition Preview with a final distribution package.
- Historical smoke fixtures may need migration once mode becomes required.

## Out Of Scope

- Broker-only package sanitization.
- Claude Code adapter implementation.
- Email-client compatibility matrix execution.
