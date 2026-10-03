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
| 10 | Copy allocation QA | Approved spec, not implemented | Planned | Planned |
| 11 | Cross-platform compatibility | Approved spec, not implemented | Codex current; Claude Code planned | Planned |
| 12 | Distribution profiles | Deferred | Deferred | Deferred |

## Framework Gate

- Project generator produces unique IDs and complete self-contained folders.
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

## Cross-Platform Gate

- Codex and Claude Code adapters are thin wrappers around the same canonical references, JSON contracts, Python runtime, and QA.
- Claude Code support is not claimed until a manual-invocation adapter has produced parity evidence against Codex.
- Platform-specific skill metadata remains outside shared canonical instructions.

## Public Release Gate

- Apache-2.0 license and attribution files remain present in the repository and standalone project packages.
- Ownership, authorship, support, repository, and maintainer metadata are complete.
- No secrets, private paths, missing assets, or cross-project references remain.
- Codex installation and explicit invocation are tested; Claude Code release claims wait for Phase 11 parity validation.
- At least one representative project campaign passes human and compatibility review.
- P0 and public-release-blocking P1 limitations in [LIMITATIONS.md](LIMITATIONS.md) are either closed or explicitly accepted by the owner with documented mitigations.

## Deferred Distribution Profiles Gate

- Phase 12 remains deferred until Cervera approves and maintains physical separation between public core, private project packs, and sanitized broker packages.
- Prompt rules alone are not treated as security or access control.
- The current public repository and project packages are treated as full internal-capability source, not restricted broker deliverables.
