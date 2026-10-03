# Product Requirements Document

## Product

OnBrand Design

## Ownership

- Owner: Cervera Real Estate, Inc.
- Author: Felix Mendoza
- License: Apache-2.0
- Intended distribution: publicly reusable framework source under the repository license, subject to separate rights for project assets and deferred private/sanitized package profiles

## Vision

Provide a scalable framework for creating self-contained, project-specific real estate email-production skills. Each project implementation must preserve its own brand, assets, templates, campaign rules, and invocation identity while sharing a proven production workflow.

## Architecture Principle

The repository is reusable; installed skills are project-specific. OnBrand Design must never blend brand rules or assets across projects merely because they share the framework.

Runtime logic should live in a canonical core shared by thin platform adapters. Codex is the current implemented path. Claude Code support remains planned until its adapter writes the same canonical campaign specifications, calls the same runtime, and passes parity validation.

Each project folder contains a complete downloadable skill bundle with unique technical IDs:

```text
projects/<project-slug>/
|-- project.json
|-- README.md
`-- skills/
    |-- onbrand-<project-slug>-email/
    `-- onbrand-<project-slug>-image/
```

## Users

- Cervera marketing owners who control project brand, campaign direction, and approvals.
- Project sales teams requiring attributed variants.
- Outside brokers requiring broker-neutral marketing materials.
- Authorized collaborators using Codex or Claude Code.
- Framework maintainers onboarding new Cervera developments.

## Product Principles

- Explicit invocation only.
- Project-specific brand and asset isolation.
- Human approval for creative ambiguity and generated imagery.
- Source-of-truth assets remain unchanged.
- Beefree-derived HTML is the compatibility benchmark when a project supplies it.
- Deliverables are traceable, portable, and reviewable.
- Credentials and private configuration never travel with project packages.
- New projects are generated from a maintained starter, then calibrated from approved project materials.
- Composition selection happens before expensive generation or release packaging.
- Real project imagery is grounded in approved source assets and environment context.
- Prompt rules are guidance, not security; restricted distribution requires physically separate source/package profiles.

## Primary User Journeys

### Project Onboarding

A maintainer generates a project folder, assigns unique skill IDs, supplies project metadata, connects the approved asset manifest, adds canonical HTML and locked footers, calibrates project references, validates behavior, and publishes the project bundle.

### Directed Campaign Build

The user invokes one project's email skill and supplies campaign type, audience, goal, CTA, and constraints. The skill uses only that project's references and assets, drafts content, obtains approvals, builds variants, validates them, and packages the campaign.

### Concept Development

The user invokes a project skill with a broad idea. It proposes angles, headlines, subject lines, preview text, CTA options, visual direction, and modules before assembly.

### Composition Preview And Release Build

The user approves a representative Design Proof with exact modules, static-block decisions, image requirements, and copy-slot ownership before the runtime performs expensive image work or complete release packaging. Release Build remains the mode that generates every authorized internal distribution variant.

### Asset Library Maintenance

An authorized maintainer runs the shared Dropbox manifest synchronizer against a configured project library. It updates generated metadata while preserving hand-curated classifications.

## Functional Requirements

| ID | Requirement |
|---|---|
| FR-001 | Every email and image skill runs only after explicit user invocation. |
| FR-002 | Every project uses unique technical skill IDs containing its slug. |
| FR-003 | A project folder is independently downloadable and contains all runtime skill instructions it requires. |
| FR-004 | The generator can add projects without imposing a fixed maximum count. |
| FR-005 | Project-specific assets, templates, footers, and brand rules never cross project boundaries implicitly. |
| FR-006 | Each email skill supports directed-build and concept-development modes. |
| FR-007 | Every email contains a hero and one approved footer variant unless the calibrated project contract says otherwise. |
| FR-007A | Calibrated projects classify standalone headers separately from heroes and reject incompatible duplicate-header compositions. |
| FR-007B | Every locked static block receives an explicit include/exclude decision and an approved position before HTML generation. |
| FR-008 | A campaign generates every variant configured for its project unless narrowed by the user. |
| FR-009 | The skill reads its project's master asset manifest and filters by campaign relevance, classification, media type, and orientation. |
| FR-010 | Selected assets are copied or downloaded without modifying originals. |
| FR-011 | Generated or edited imagery follows a separate explicit approval workflow. |
| FR-012 | HTML follows the project's calibrated Beefree structure and conservative email-client patterns. |
| FR-013 | Locked footer partials are inserted without unauthorized rewriting. |
| FR-014 | Every campaign delivers a folder and ZIP with HTML, used assets, and a campaign asset manifest. |
| FR-015 | QA detects missing assets, private paths, incorrect variants, and unsupported invented facts. |
| FR-016 | Dropbox catalog refresh preserves `category` and `approved_for` for matched records. |
| FR-017 | Credentials remain outside distributable project folders and repository history. |
| FR-018 | Project packages remain structured for portability, with Codex current and Claude Code support planned pending adapter parity validation. |
| FR-019 | The registry records every maintained project and its lifecycle status. |
| FR-020 | Repository metadata attributes ownership to Cervera Real Estate, Inc. and authorship to Felix Mendoza. |
| FR-021 | Every project email skill runs a contextual copy-quality pass that preserves approved voice, reports unsupported claims, and does not claim to detect authorship. |
| FR-022 | Campaign production distinguishes Composition Preview, Smoke Test, and Release Build modes, with representative-only output permitted only when recorded by policy. |
| FR-023 | Composition Preview records exact module choices, static-block decisions, image requirements, copy-slot ownership, and representative variant before image generation or release packaging. |
| FR-024 | Generated project imagery is grounded in approved source assets and environment context, with real Rider exterior and arrival scenes defaulting to approved base imagery. |
| FR-025 | Copy-allocation QA deduplicates restricted owner phrases and names across live text, baked imagery, alt text, and metadata before release. |
| FR-026 | Cross-platform support uses a canonical core plus thin Codex and Claude Code adapters; Claude Code is planned only until parity validation is recorded. |
| FR-027 | Broker-only or sanitized distribution packages remain deferred until public core, private project packs, and broker packages are physically separated and validated. |

## Non-Functional Requirements

- Scalability: dozens of project folders without technical ID collisions.
- Reliability: no partial manifest writes; backups precede replacement.
- Traceability: source identity, project ownership, and campaign use are recorded.
- Security: secrets are local-only and never emitted into artifacts.
- Compatibility: HTML prioritizes major email clients and Outlook-safe patterns.
- Maintainability: shared scaffolding changes deliberately; generated projects are reviewed independently.
- Portability: local paths and credentials remain configuration rather than source assumptions.
- Security: public source and prompt instructions are not access controls for broker or private distribution.

## Data Contracts

### Project Metadata

Each `project.json` records framework name, project name and slug, owner, author, lifecycle status, technical skill IDs, calibration status, and asset-manifest configuration state.

### Master Asset Manifest

Maintained per project and used for discovery. Current records include:

- `filename`
- `dropbox_id`
- `dropbox_path`
- `category` as an array
- `orientation`
- `approved_for` as an array
- `public_url`

### Campaign Asset Manifest

Created per deliverable and limited to assets used by that campaign. It records role, provenance, package path, variants, generation/edit status, and final hosted URL when known.

## Boundaries

- Public Dropbox URLs are acquisition sources, not guaranteed production hosting.
- PDFs are linked/packaged or converted to approved images; they are not assumed embeddable email content.
- No pricing, availability, dates, contact details, or claims may be invented.
- The framework does not publish or send campaigns unless separately specified and authorized.
- Public source reuse does not automatically grant reuse rights for project logos, photographs, renderings, templates, or campaign content.
- The current repository and project packages are not broker-restricted distributions; sanitized broker profiles are a deferred planning item.
- Claude Code support is not implemented until an adapter and parity validation are recorded.

## Success Measures

- A new project can be scaffolded without hand-renaming skill IDs.
- Multiple project bundles can be installed together without collisions or brand leakage.
- A user can create a complete campaign package without manually locating assets or assembling variants.
- Every selected asset can be traced to the correct project's master catalog.
- Curated metadata survives repeated synchronization.
- Representative campaigns pass package QA and human review.

## Open Decisions

- GitHub organization, repository URL, visibility, support email, and CODEOWNERS identities.
- Canonical public manifest URL and caching policy per project.
- Final deployment platform and image-hosting handoff.
- Supported email-client test matrix for version 1.0.
- Business decision and hosting model for private project packs and sanitized broker packages.
