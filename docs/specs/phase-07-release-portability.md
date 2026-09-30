# Phase 7: Portability, Release, And Team Distribution

**Status:** Planned  
**Target:** 0.9.0 through 1.0.0  
**Depends on:** Phases 0-6

## Goal

Release documented, versioned project packages that authorized collaborators can install and explicitly invoke in Codex or Claude Code.

## Requirements

- RELEASE-001: Preserve Codex `allow_implicit_invocation: false`.
- RELEASE-002: Preserve Claude Code `disable-model-invocation: true`.
- RELEASE-003: Isolate platform-specific metadata from portable skill content.
- RELEASE-004: Package skills, references, scripts, safe examples, and dependency declarations without secrets.
- RELEASE-005: Document local installation and update procedures for both environments.
- RELEASE-006: Decide whether to ship as skill folders, a portable plugin, or both.
- RELEASE-007: Establish repository ownership, visibility, license, review rules, and release tags.
- RELEASE-008: Test from a clean second computer or clean environment.
- RELEASE-009: Publish owner, author, citation, support, repository, and explicit license metadata.
- RELEASE-010: Allow users to download one project without receiving unrelated project assets or instructions.

## Acceptance Criteria

- A new authorized user can install and invoke the skill from documented steps.
- Ordinary email requests do not activate either skill implicitly.
- The public manifest can be read and selected assets can be acquired without private Dropbox access.
- A clean environment can produce and validate a representative campaign package.
- Multiple project bundles can be installed together without invocation collisions.
- Version 1.0 release notes identify supported environments and remaining limitations.
