# Roadmap

The roadmap applies to the framework and is executed independently for each project where calibration or assets differ.

| Phase | Name | Framework status | The Rider | Cassia |
|---|---|---|---|---|
| 0 | Multi-project foundation and governance | Complete | Registered | Scaffolded |
| 1 | Asset catalog and selection | In progress | In progress | Not started |
| 2 | Beefree, brand, and template calibration | Ready | Scaffold calibrated | Waiting on assets |
| 3 | Campaign strategy and copy system | Drafted | Drafted | Provisional |
| 4 | Image-generation specialist | Drafted | Drafted | Provisional |
| 5 | HTML assembly and footer variants | Rider implementation complete | Implemented and tested | Waiting on Phase 2 |
| 6 | Distribution packaging and QA | Rider implementation complete | Implemented and smoke-tested | Planned |
| 7 | Build modes | Rider implementation complete | Implemented and tested | Planned |
| 8 | Composition Preview | Rider implementation complete | Implemented and tested | Planned |
| 9 | Grounded image generation | Rider implementation complete | Implemented and tested | Planned |
| 10 | Copy allocation QA | Rider implementation complete | Implemented and tested | Planned |
| 11 | Cross-platform compatibility | Deterministic adapters/parity complete; live agents unverified | 13/13 critical components at 100 | Reference adapters; runtime unavailable |
| 12 | Distribution profiles | Deferred | Deferred | Deferred |
| 13 | Jev semantic decision pilot | Evaluation and independent-review tooling complete; provider not implemented | 26 provisional cases awaiting two blinded reviews | Not planned until Rider evidence exists |

## Framework Gate

- Project generator produces unique IDs and isolated packs with shared-core dependencies documented.
- Registry and project metadata remain valid.
- No project template contains another project's name, brand rules, or credentials.
- Known limitations, scoring opportunities, and deferred safeguards are recorded in [LIMITATIONS.md](LIMITATIONS.md) before new phase implementation starts.

## Asset Gate

- Project master manifest is reachable.
- Selection honors classification, media type, orientation, and project boundaries.
- Selected assets can be downloaded and traced to their source record.

## Template Gate

- Canonical project HTML has been analyzed.
- Brand and design tokens are documented per project.
- Locked footer insertion boundaries are verified.
- Header/hero compatibility and static-block lock boundaries are verified.

## Campaign Gate

- Directed and concept-development requests produce approved copy and module plans.
- Generated image work follows its separate approval workflow.
- Required variants assemble from one approved body.

## Build Mode Gate

- Composition Preview, Smoke Test, and Release Build are distinct modes.
- Representative-only builds record the selected variant and expansion policy.
- Footer, roster, and scaffold-footer changes still expand validation to every affected variant.
- The Rider runtime requires `build.mode` and records effective variant scope in metadata and QA.

## Composition Preview Gate

- Stable module codes and compatibility metadata exist before user selection.
- Users approve exact modules, static blocks, image requirements, copy slots, and representative variant before expensive image work starts.
- User-facing language uses Composition Preview or Design Proof; automated validation may continue to use Smoke Test.
- The Rider runtime provides portable catalog and approved-plan CLI artifacts and requires approved plans for Composition Preview and Release Build.

## Image Grounding Gate

- Image generation plans start from approved project sources and recorded environment context.
- Real Rider exterior, arrival, and architectural scenes default to approved base imagery rather than unconstrained generation.
- Generated images carry provenance, approval status, and placement constraints into QA.
- The Rider runtime validates `image_workflow` records, approved source assets, output checksums/dimensions, intended slots, and release eligibility before packaging generated or edited imagery.

## Copy Allocation Gate

- Every copy unit has an approved slot owner before rendering.
- Restricted phrases and names, including single-owner occurrences, are deduplicated across live text, baked imagery, alt text, and metadata.
- QA reports unsupported claims, repeated authority language, and ambiguous ownership rather than silently rewriting locked content.
- All Rider build modes require approved `copy_allocation` before rendering; successful metadata and QA retain ownership, claim references, explicit exemptions, deterministic counts, and transparent similarity scores.

## Cross-Platform Gate

- Codex and Claude Code adapters are thin wrappers around the same canonical references, JSON contracts, Python runtime, and QA.
- Manual-only adapters pass deterministic parity against CLI; all 13 critical components require 100. Live model invocation stays unverified under LIM-017.
- Platform-specific skill metadata remains outside shared canonical instructions.

## Semantic Decision Pilot Gate

- Jev remains optional and disabled by default; deterministic QA remains authoritative.
- The first evaluation targets semantic copy similarity and claim-support triage using a labeled Rider dataset and a held-out set.
- Questions, criteria, model version, thresholds, probabilities, confidence, and human overrides are versioned and auditable.
- Provider unavailability has a tested deterministic fallback and cannot replace the last passing package.
- Visual similarity stays with specialized image/OCR/render measurements; Jev may only route their structured evidence.
- Production blocking is prohibited until the Phase 13 acceptance report demonstrates measurable improvement and owner-approved data handling.
- Provisional seed labels must receive independent review and adjudication before provider questions or thresholds are accepted.

## Public Release Gate

- Apache-2.0 license and attribution files remain present in the repository and standalone project packages.
- Ownership, authorship, support, repository, and maintainer metadata are complete.
- No secrets, private paths, missing assets, or cross-project references remain.
- Adapter installation/manual policies and deterministic outputs are tested; live platform/model claims wait for LIM-017 evidence.
- At least one representative project campaign passes human and compatibility review.
- P0 and public-release-blocking P1 limitations in [LIMITATIONS.md](LIMITATIONS.md) are either closed or explicitly accepted by the owner with documented mitigations.

## Deferred Distribution Profiles Gate

- Phase 12 remains deferred until Cervera approves and maintains physical separation between public core, private project packs, and sanitized broker packages.
- Prompt rules alone are not treated as security or access control.
- The current public repository and project packages are treated as full internal-capability source, not restricted broker deliverables.
