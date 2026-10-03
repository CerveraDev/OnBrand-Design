# Phase 12: Distribution Profiles

**Status:** Deferred
**Target:** Post-compatibility decision
**Depends on:** Phase 11 and a private-distribution decision

## Goal

Define future internal and broker-only distribution profiles after the repository privacy and packaging strategy is approved.

## Non-Goals

- Do not implement this phase now.
- Do not represent the current public repository as access-restricted.
- Do not rely on prompt rules in a public local skill as a security boundary.
- Do not attempt to scrub public Git history by moving files later.

## Requirements

- DIST-001: Treat the current public repository as the full internal-capability source until this phase is implemented.
- DIST-002: Do not distribute the current public project package to outside brokers as if internal features are restricted.
- DIST-003: Future architecture separates public reusable core, private Cervera project packs, and sanitized broker package.
- DIST-004: Broker package generates only one personalized broker email.
- DIST-005: Broker package physically excludes agent roster, batch variants, branded-footer generator, and internal configs.
- DIST-006: Private project packs hold internal project assets, agent data, internal release profiles, and Cervera-specific configuration.
- DIST-007: Documentation must warn that public Git history remains public even after later file moves.

## Anticipated Data And Contracts

- `distribution_profile`: `internal`, `broker-sanitized`, or `public-core`.
- Sanitized broker manifest excluding internal identities and batch generation metadata.
- Private project-pack manifest for internal-only assets and agent data.
- Migration checklist for public-to-private file movement.

## Workflow

1. Decide whether Cervera will maintain private project packs.
2. Freeze public-core boundaries.
3. Move internal project data into private packs only after repository/privacy approval.
4. Create broker package from sanitized inputs, not prompt restrictions.
5. Prove excluded capabilities are physically absent.
6. Document public-history limitations before any external distribution.

## Acceptance Criteria

- A broker package cannot generate all agent variants because the roster and generator are absent.
- Internal project packs can still produce full Cervera-authorized output.
- Public core remains reusable without private assets.
- Distribution documentation clearly distinguishes public-source visibility from runtime authorization.

## Tests And Evidence Required

- File inventory tests proving broker packages exclude internal files.
- Runtime tests proving broker packages cannot request batch agent variants.
- Secret and private-path scans.
- Migration audit log entries.

## Dependencies

- Cross-platform adapter architecture.
- Repository visibility decision.
- Private hosting or private repository budget approval.

## Risks

- Public history may already contain information unsuitable for broker distribution.
- Sanitization by instruction alone would create a false security claim.
- Maintaining public, private, and broker packages increases release complexity.

## Out Of Scope

- Any implementation before explicit approval.
- Git history rewriting.
- Legal determination of what brokers may receive.
