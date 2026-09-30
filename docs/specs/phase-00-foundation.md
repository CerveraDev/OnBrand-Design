# Phase 0: Foundation And Governance

**Status:** Complete  
**Target:** 0.1.0

## Goal

Establish the multi-project product boundary, skill architecture, invocation policy, delivery contract, and governance required for controlled implementation.

## Scope

- Reusable OnBrand Design framework with isolated project implementations.
- One main email and one isolated image-generation skill per project.
- Collision-safe project-specific skill IDs.
- Project registry, starter template, and generator.
- Explicit-only invocation in Codex and Claude Code.
- Directed-build and concept-development modes.
- Hero/footer module invariants and output variants.
- PRD, roadmap, status, audit, versioning, and GitHub-ready layout.

## Acceptance Criteria

- Both skills contain explicit-only metadata and instructions.
- Generated project IDs include their project slug and remain unique.
- Project folders are independently downloadable.
- Main skill identifies required modules and campaign variants.
- Project documents agree on phases, terminology, and current status.
- Repository ignores credentials, virtual environments, and generated outputs.
- Version `0.1.0` is recorded consistently.

## Exit Evidence

- Skill drafts and governance files exist in the canonical project package.
- The Rider is registered and Cassia is scaffolded from the shared starter.
- Manual validation previously confirmed both skill structures and policies.
