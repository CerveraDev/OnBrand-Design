# Phase 8: Composition Preview

**Status:** Approved specification, not implemented
**Target:** 0.8.0
**Depends on:** Phase 7

## Goal

Add a user-facing approval gate for module composition before expensive image generation, HTML assembly, and package generation.

## Non-Goals

- Do not replace automated smoke tests.
- Do not make the model silently choose among materially different module compositions.
- Do not create new scaffold modules in this phase unless a selected approved module cannot support the campaign.

## Requirements

- PREVIEW-001: Build a labeled module catalog with stable human-readable codes such as `H-01`, `HR-01`, `HH-01`, and `AI-01`.
- PREVIEW-002: Each catalog entry documents module type, compatibility, header behavior, live-text support, image requirement, image aspect ratio, and companion-module rules.
- PREVIEW-003: Each catalog entry defines thumbnail or isolated-preview expectations.
- PREVIEW-004: The user chooses exact modules before generated image work begins.
- PREVIEW-005: The composition plan lists selected modules, selected static blocks, required assets, expected editable slots, and representative variant.
- PREVIEW-006: The selection gate must be skipped only when the user explicitly asks for a technical smoke run or provides an already approved module plan.
- PREVIEW-007: User-facing language uses "Composition Preview" or "Design Proof"; automated runtime language may continue to use "smoke test."

## Anticipated Data And Contracts

- `module_catalog.json`: stable code, scaffold module ID, type, header inclusion, lock state, aspect ratio, and slot summary.
- `composition_plan.json`: selected module codes, static-block decisions, copy-slot ownership, image requirements, and approval status.
- Thumbnail artifacts or isolated preview HTML snippets for each eligible module.

## Workflow

1. Load scaffold metadata and slot map.
2. Present compatible module options with stable codes and preview expectations.
3. Identify incompatible pairings before the user selects.
4. Ask the user to approve exact modules, static blocks, and representative variant.
5. Create a composition plan from the approved selection.
6. Pass the plan to asset selection, image generation, copy allocation, and final rendering.

## Acceptance Criteria

- A user can choose a full campaign composition without reading scaffold row names.
- A header-bearing hero cannot be paired with a standalone header in the offered options.
- The plan records whether hero text is live HTML or baked into imagery.
- Expensive image generation never starts before the selected hero/image module is approved.

## Tests And Evidence Required

- Catalog generation snapshot tests.
- Compatibility filtering tests.
- Golden composition-plan examples.
- UX copy review showing "Composition Preview" and "Design Proof" are used for user-facing selection.

## Dependencies

- Rider module metadata.
- Slot map.
- Future build-mode runtime contract.

## Risks

- Catalog labels could drift from scaffold module IDs if not generated deterministically.
- Thumbnail previews may imply visual fidelity that email-client rendering cannot guarantee.
- Too many options could slow directed builds if the user already supplied exact modules.

## Out Of Scope

- Final release packaging.
- Cross-platform adapter implementation.
- Private broker distribution profiles.
