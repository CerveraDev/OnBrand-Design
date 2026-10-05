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
| 13 | Jev semantic decision pilot | Version 1 holdout complete; revise decision | 8/9 labels but 5/9 actions, one false allow; production rejected | Not planned until a version 2 pilot is justified |
| 14 | Email render matrix | Browser-preview tool and Rider evidence complete | Four browser modes pass; human and real-client matrix pending | Planned after representative package |
| 15 | Creative fidelity remediation | Implemented; creative approval pending | CFG-05 and Rider Gym 2 proof generated; further layout refinement requested | Planned after project calibration |
| 16 | Scaffold expansion and layout calibration | Canonical promotion complete; compatibility follow-up open | Phase 16 canonical and proof reproducible; native-client matrix pending | Planned after project calibration |

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
- Dataset v1 is frozen from two blinded reviews and explicit adjudication; provider questions and thresholds may use calibration cases only until the first question set is locked.
- Question set v1 pins `jev-1.13.0`, carries no production effect, and generates 17 calibration requests without labels or holdout cases.
- Provider execution defaults disabled, requires environment opt-in plus explicit live authorization, validates typed answers/model/question IDs, and emits non-production receipts without secrets.
- The owner-approved 17-case live calibration reached 16/17 candidate-action accuracy versus 10/17 for the lexical baseline on the same split. That calibration signal justified, but did not predict, the separately controlled holdout.
- The separately approved holdout matched 8/9 semantic labels but only 5/9 actions versus 4/9 for the baseline, with one false allow and 44.4% review routing. Version 1 is marked `revise`; the spent holdout cannot validate a revised policy.

## Public Release Gate

- Apache-2.0 license and attribution files remain present in the repository and standalone project packages.
- Ownership, authorship, support, repository, and maintainer metadata are complete.
- No secrets, private paths, missing assets, or cross-project references remain.
- Adapter installation/manual policies and deterministic outputs are tested; live platform/model claims wait for LIM-017 evidence.
- At least one representative project campaign passes human and compatibility review.
- The representative campaign must pass Phase 15 creative-fidelity approval before real-client evidence is treated as a release candidate.
- P0 and public-release-blocking P1 limitations in [LIMITATIONS.md](LIMITATIONS.md) are either closed or explicitly accepted by the owner with documented mitigations.

## Scaffold Expansion And Layout Gate

- Treat each newly supplied scaffold as a versioned input; preserve the current source and canonical scaffold as provenance rather than overwriting history.
- Parse and classify every new marker type before using its enclosed rows in campaign assembly.
- Map every added block to stable metadata, layout purpose, compatibility rules, editable slots, locked content, image requirements, and copy-allocation ownership.
- Distinguish technical compatibility from editorial layout intent so structurally valid blocks are not combined in an awkward sequence.
- Regenerate the module catalog, labeled galleries, composition plans, cross-platform fingerprints, and representative proof after scaffold calibration.
- Require owner review of the updated block sequence before replacing a canonical creative baseline.

Checkpoint on 2026-10-05: versioned intake, nested parsing, refined metadata, deterministic slots, runtime sequencing, regenerated galleries, owner proof approval, and canonical promotion are complete. The former Phase 15 trio is archived as regression provenance. The ordinary canonical build reproduces the approved proof byte-for-byte with 69 passing QA checks and eight assets. Reproducible browser-matrix evidence and native email-client testing remain open.

## Deferred Distribution Profiles Gate

- Phase 12 remains deferred until Cervera approves and maintains physical separation between public core, private project packs, and sanitized broker packages.
- Prompt rules alone are not treated as security or access control.
- The current public repository and project packages are treated as full internal-capability source, not restricted broker deliverables.
