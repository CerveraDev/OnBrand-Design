# Phase 4: Image-Generation Specialist

**Status:** Drafted  
**Target:** 0.5.0  
**Depends on:** Phases 1 and 2

## Goal

Provide a separately invoked, approval-driven workflow for generated or edited project campaign imagery without weakening architectural or brand accuracy.

## Requirements

- IMAGE-001: Require separate explicit invocation.
- IMAGE-002: Start from an approved project asset when editing a real building.
- IMAGE-003: Preserve architecture unless the user explicitly authorizes a conceptual treatment.
- IMAGE-004: Define what remains unchanged, what is added, placement, crop, realism, and forbidden changes.
- IMAGE-005: Return approval candidates before final email assembly.
- IMAGE-006: Record base asset, prompt, edits, approval state, and final file provenance.
- IMAGE-007: Decide whether text remains live HTML or is baked into the hero.
- IMAGE-008: Return only approved final images to the campaign package.

## Acceptance Criteria

- A realistic edit brief produces credible candidates without changing protected architecture.
- Project logos and branded objects are used only with supplied approved assets.
- Rejected candidates never enter the final campaign package.
- The final image has suitable dimensions and crop for the calibrated hero module.
