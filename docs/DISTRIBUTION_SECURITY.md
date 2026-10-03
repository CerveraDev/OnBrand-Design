# Distribution Security Plan

**Status:** Approved specification, Phase 12 deferred
**Updated:** 2026-10-03

## Warning

Do not distribute the current public repository or project package to outside brokers as if internal capabilities are access-restricted. The current public repository must be treated as the full internal-capability source until a later private/sanitized packaging phase is implemented.

## Threat Model

Sensitive or internal material may include:

- Agent rosters and contact data.
- Batch variant generation.
- Internal release profiles and packaging rules.
- Project-specific assets, templates, and campaign inputs.
- Private configuration and maintainer-only credentials.

Likely risks:

- A broker receives files capable of generating internal variants.
- Public Git history preserves files even after later moves.
- Prompt instructions are mistaken for access control.
- Ignored local credentials are copied manually into a package.

## Public-Source Limitations

Prompt rules in a local public skill are not security. A user with the source can read, edit, or remove those rules. Physical exclusion and repository access control are required for meaningful distribution boundaries.

Public Git history remains public. Moving a file later does not erase its earlier availability. If a file should never be seen by brokers, it should not be committed to a public repository in the first place.

## Internal And Broker Boundary

Current state:

- Public repository is the full internal-capability source.
- No broker-only sanitized package exists.
- No private Cervera project pack exists.
- No claim of access restriction should be made.

Deferred target state:

- Public reusable core: generic runtime, schemas, docs, and safe examples.
- Private Cervera project packs: internal project assets, rosters, full variant profiles, and private configs.
- Sanitized broker package: one personalized broker email generator, no roster, no batch variants, no branded-footer generator, and no internal configs.

## Deferred Privacy Decision

Phase 12 depends on an explicit business decision to pay for or maintain private hosting/repositories. Until then, keep planning language clear: broker-only distribution is deferred and unimplemented.

## Migration Considerations

- Inventory files that must move to private packs.
- Document which public files already exist in history.
- Create sanitized packages from a clean source tree rather than deleting files after packaging.
- Add tests proving excluded files are absent.
- Run secret and private-path scans before every release.
- Record migration decisions in `AUDIT_LOG.md`.

## Do Not Distribute As Restricted Yet

Before external broker distribution, require evidence that:

1. Broker package contents are physically limited.
2. Internal roster data is absent.
3. Batch generation and branded/internal footer generation are absent.
4. Private configs and ignored credentials are absent.
5. The package was created from the sanctioned broker source profile, not the internal public repository checkout.

Until those criteria are implemented and validated, use the repository only as an internal-capability source.
