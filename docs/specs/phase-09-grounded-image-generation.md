# Phase 9: Grounded Image Generation

**Status:** Approved specification, not implemented
**Target:** 0.8.0
**Depends on:** Phases 1, 4, and 8

## Goal

Ground campaign imagery in approved project environments whenever the request implies a real Rider space, building, or amenity.

## Non-Goals

- Do not ban fully generated conceptual environments when the user explicitly approves them.
- Do not alter real architecture, renderings, lighting, or project conditions without explicit approval.
- Do not upload generated assets to Dropbox unless a later workflow explicitly supports that.

## Requirements

- IMAGE-GROUND-001: Requests implying a real Rider environment default to an approved Dropbox corpus base image.
- IMAGE-GROUND-002: The workflow decomposes subject, environment, framing, crop, brand elements, and invariant areas before generation.
- IMAGE-GROUND-003: The system proposes one or two approved base assets and obtains user approval before compositing or editing.
- IMAGE-GROUND-004: Edits preserve architecture, lighting direction, material identity, and project context unless the user approves a conceptual treatment.
- IMAGE-GROUND-005: Approved logo references must come from manifest or scaffold assets and be recorded in provenance.
- IMAGE-GROUND-006: Generated environments require explicit user approval and must be labeled as conceptual.
- IMAGE-GROUND-007: The final asset records base asset identity, prompt, edit steps, crop, final dimensions, and approval status.
- IMAGE-GROUND-008: The wellness example is the cautionary reference: a real Rider gym rendering should have been selected, the woman should have been tightly framed, and the gym environment should have been preserved.

## Anticipated Data And Contracts

- `image_plan`: requested subject, approved base asset IDs, invariant regions, crop/aspect ratio, logo reference, and approval status.
- `image_provenance`: base asset source, generation prompt, compositing notes, final path, dimensions, checksum, and reviewer approval.
- `conceptual_environment_approved`: boolean with approval evidence when no real base asset is used.

## Workflow

1. Parse the image brief into subject, environment, action, framing, and brand elements.
2. Decide whether the environment implies a real project asset.
3. Select one or two candidate base assets from the approved manifest.
4. Present candidate base assets with relevance notes and get approval.
5. Generate or composite the subject into the approved base image while preserving invariant areas.
6. Apply requested crop and aspect ratio.
7. Perform visual approval before email assembly.
8. Package the final image and provenance with the campaign.

## Acceptance Criteria

- A "Rider gym" or "Rider lobby" request starts from approved Rider imagery by default.
- The image plan makes any fully generated environment explicit before generation.
- Logo-bearing objects use approved logo references rather than invented marks.
- Final image dimensions match the selected module requirement.

## Tests And Evidence Required

- Image-plan fixtures for real environment, conceptual environment, and branded-object cases.
- Provenance records for generated and edited assets.
- Visual QA checklist covering invariants, crop, logo placement, and subject framing.
- Regression note documenting the wellness-smoke lesson.

## Dependencies

- Validated manifest categories and approvals.
- Composition Preview module image requirements.
- Image-generation skill workflow.

## Risks

- Base assets may not match the requested subject or camera angle closely enough.
- Overly strict grounding could block useful conceptual campaigns.
- Logo fidelity may still require deterministic compositing after generation.

## Out Of Scope

- Dropbox upload or asset-library promotion of generated imagery.
- Automated visual similarity scoring.
- Broker-only package generation.
