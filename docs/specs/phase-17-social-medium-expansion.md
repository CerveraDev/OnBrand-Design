# Phase 17: Social Medium Expansion

**Status:** Drafted; first runtime increment implemented (AUD-101); not owner-approved

**Target:** A second medium runtime that produces static social posts and carousels from the same project packs, approval gates, and copy-allocation discipline already proven on email

**Depends on:** Phases 1, 8, 9, and 10. Broker distribution depends on Phase 12.

## Why This Phase Exists

OnBrand Design is currently an email-production framework with one calibrated project. The owner's objective is a 360 approach to marketing collateral across email and social, segmented by audience: in-house teams receive the full capability set, outside brokers receive a limited, pre-approved subset.

Social is a new medium, not a new product. The valuable and hard-won parts of the framework are medium-independent: deterministic asset selection, approved copy allocation with cross-surface repetition control, grounded image provenance, explicit approval gates, build modes, and blocking QA. Those must be reused rather than reimplemented.

This phase adds social as a sibling medium runtime inside the existing repository. It does not modify the email runtime.

## Architecture Decision

A separate repository or fork is rejected. `tools/platform_adapters/contract.py` already registers runtimes in a `RUNTIMES` table keyed by runtime name, and `projects/<slug>/adapter.json` already declares `runtime` as data. The dispatcher already tolerates projects with no implemented runtime. The extension point exists.

Consequences:

- `tools/rider_campaign_runtime/` is not modified by this phase.
- Social logic lives in a new sibling package.
- `contract.py` receives one additive `RUNTIMES` entry, covered by existing adapter tests.
- `project.json` gains a `social` entry under `skills`, producing `onbrand-<slug>-social`.
- Shared-core extraction is explicitly deferred. `tools/asset_selection/` is already a standalone importable package. Social may carry its own thin copy-allocation adapter until both mediums are stable and the genuinely shared shape is observable.

The email runtime's continued correctness is demonstrated by the existing test suite and by byte-for-byte reproduction of the approved canonical proof, not by source separation.

## Scope

In scope:

- Static single-image social posts
- Multi-slide carousels

Deferred to a later phase:

- Reels and any video output. Video introduces timeline, duration, audio rights, caption burn-in, motion, and codec concerns, and the current asset library contains no video records. Reels must not be specified in the same phase as carousels.
- Direct publishing or scheduling to any social platform. This phase produces reviewable collateral packages only.

## Audience And Capability Boundary

Audience is a capability boundary, not a prompt rule. `LIM-011` already records that prompt instructions are not a security control, so this phase must be designed so that Phase 12 packaging is a build step rather than a retrofit.

| Capability | In-house | Outside broker |
|---|---|---|
| Composition selection | Full labeled gallery and sequence selection | Fixed set of pre-approved layout templates |
| Copy authoring | Full allocation authoring and ownership | Approved slot fill only |
| Asset access | Full project catalog subset approved for social | Social-approved, broker-safe subset |
| Agent attribution | In-house agent records | Broker-supplied contact fields only |
| Email medium | Available | Absent from the bundle |

Design requirements that follow:

1. Social composition templates are data files, separable from the composition gallery generator.
2. No social runtime path may read `data/agents/` unless the variant explicitly requests in-house attribution.
3. Asset resolution for broker builds must be satisfiable from a filtered manifest that omits `agent-footer` and `image-generation-reference` records, and omits Dropbox IDs and paths.
4. Restricted-likeness records must be excluded by classification, never by filename convention.

Giving brokers less means giving them fewer approved choices, not a degraded tool. The pre-approved template set is simultaneously the IP control, the brand-compliance guarantee, and the mechanism that keeps a live training session free of unresolved approval gates.

## Asset Readiness Findings

Measured against the current local Rider manifest cache, 206 records:

| Measure | Count |
|---|---|
| Image records | 145 |
| PDF records | 61, all landscape |
| Landscape images | 100 |
| Square images | 29 |
| Portrait images | 16 |
| Records carrying any social `approved_for` value | 0 |

Square images include 7 in-house agent headshots approved only for `agent-footer`. Portrait images include 3 likeness-reference records restricted to the explicit image-generation workflow. The remaining square inventory is concentrated in a single interior/residence/unit/kitchen cluster of 14 records plus 7 exterior records.

Two blocking conclusions:

1. **No asset in the catalog is currently approved for social use.** The `approved_for` vocabulary is entirely email-role based: `hero`, `body`, `composition`, `agent-footer`, `image-generation-reference`. Social approval roles must be added by authorized curation before any real social build. Recorded as `LIM-021`.
2. **The library is landscape-dominant, but social is square and vertical.** Social therefore requires an approved, provenance-bearing crop and reframe operation. Selection alone cannot satisfy carousel or future vertical formats. Recorded as `LIM-022`.

All 206 records carry a `public_url`, so existing-asset hosting is not a gap for social. Hosting remains an open item only for generated imagery.

## Platform Format Contract

Platform requirements drift, so target dimensions, slide limits, and safe areas must live in a versioned sidecar rather than in code, following the precedent of versioned scaffolds and pinned question sets.

The sidecar must record, per format: aspect ratio, pixel dimensions, minimum and maximum slide count, safe-area insets, maximum text length per surface, file-size ceiling, and the date the values were verified. Builds must fail when a requested format is absent from the pinned sidecar version rather than falling back to a default.

Initial formats to pin: 1:1 square post, 4:5 portrait post, and 1:1 and 4:5 carousels. Current commonly cited values are 1080x1080 and 1080x1350, with carousels of up to 10 slides, but every value must be verified and dated before it is treated as authoritative. Owner decision, 2026-10-09 (AUD-104): 4:5 formats export at 1200x1500, the social scaffold canvas at 2x.

## Crop And Reframe Provenance

Source assets remain unmodified, per FR-010. A crop is a derived output requiring a provenance record, following the Phase 9 grounded-image model:

- Source asset reference resolved through the validated manifest
- Requested output format and target dimensions
- Crop geometry and resulting focal point
- Output checksum and dimensions, verified against the local file
- Approval status

Builds must reject a derived crop whose source asset is missing, unapproved for social, or whose output checksum or dimensions do not match. Automated subject preservation and focal-point quality scoring remain out of scope; `LIM-001` already records that generated-image visual faithfulness is not automatically scored, and the same limitation applies to automated cropping.

## Composition Model

Social composition is slide-sequenced rather than row-ranged. Required contract elements:

- Stable template codes and human-readable labels, consistent with the `CFG-*` and `SEQ-*` convention
- Per-slide role, such as opener, feature, detail, proof, or call to action
- Required and optional slots per slide, typed
- Image count, aspect ratio, and crop requirement per slide
- Minimum and maximum slide counts per template
- Locked content and editable slots, matching the email scaffold's lock discipline
- Template availability per audience

The email distinction between technical, content, editorial, and visual compatibility carries over. The first three may be increasingly deterministic; final visual quality remains human-approved.

## Copy Allocation

Social reuses the Phase 10 allocation contract and its calibrated thresholds, with an extended channel vocabulary. The current email channel set is `live-html`, `baked-image-text`, `alt-text`, `metadata`, `static`, `legal`, and `footer`. Social requires at minimum `caption`, `on-image-text`, `slide-text`, `hashtags`, and `alt-text`.

The highest-value requirement in this phase: **cross-medium repetition must be detectable within one campaign.** The same headline appearing in a Rider email and a Rider carousel in the same campaign week is a real quality failure, and it is only detectable while one system can see both surfaces. This capability is the principal reason a fork was rejected, and it must have a test fixture.

Thresholds stay at the calibrated 0.65 warning and 0.82 blocking values until a social-specific calibration dataset justifies a change. Do not retune thresholds against social fixtures without recording the evidence.

## Build Modes

The existing three modes map directly:

- **Composition Preview:** renders one representative post or carousel for approval before crop work or full packaging.
- **Smoke Test:** technical validation only, never delivered.
- **Release Build:** the full authorized variant matrix for the audience in scope.

Variant semantics differ from email. Social has no footer partials or per-agent footer matrix. The initial variant axis is `branded` and `broker-customizable`, where broker-customizable substitutes contact and attribution fields without removing Rider project identity.

## Quality Assurance Gates

Blocking:

- Every slot filled or explicitly declared optional
- Every image resolved to an approved, social-approved manifest record or an approved derived crop
- Output dimensions and file sizes within the pinned format sidecar
- Text within per-surface limits, measured after normalization
- Copy allocation passing, including cross-medium repetition checks
- No restricted-likeness or `agent-footer` asset present in a broker build
- No Dropbox ID, Dropbox path, or private URL present in any delivered manifest

Human-reviewed, not automated:

- Crop subject preservation and focal quality
- Editorial and visual coherence across the slide sequence
- Legal, fair-housing, and regulated-copy review, per `LIM-016`

## Deliverables

- `tools/social_runtime/` sibling package with schema, composition, crop provenance, packaging, and QA
- Versioned platform-format sidecar
- Social composition templates, with audience availability recorded
- Social role vocabulary added to the asset approval taxonomy, applied by authorized curation
- `onbrand-<slug>-social` canonical skill and generated platform wrappers
- One additive `RUNTIMES` entry
- Cross-medium repetition test fixture
- Broker-exclusion test asserting no agent, likeness, email-runtime, or private-path artifact reaches a broker bundle
- Representative Rider carousel Composition Preview for owner approval

## Acceptance Criteria

1. The email test suite and the canonical email proof remain unchanged, with byte-for-byte reproduction preserved.
2. A Rider carousel Composition Preview builds from approved inputs and passes blocking QA.
3. A build requesting an unapproved-for-social asset fails with a specific reason.
4. A broker-profile build fails if any restricted record, agent record, or private path is reachable.
5. Cross-medium repetition between an email surface and a social surface in one campaign is detected and reported.
6. A format absent from the pinned sidecar fails rather than defaulting.
7. No social instruction claims a capability boundary that packaging does not physically enforce.

## Non-Goals

- Reels, video, audio, or motion output
- Publishing, scheduling, or platform API integration
- Automated crop quality or subject-preservation scoring
- Automated legal or compliance approval
- Treating pre-approved broker templates as a security control absent Phase 12 packaging
- Modifying the email runtime, canonical scaffold, or approved email proof

## Sequencing Note

The carousel runtime can be built before Phase 12. Broker *training* cannot. The capability boundary above must be designed in now so that Phase 12 becomes a packaging step rather than a retrofit of an already-entangled runtime.

Asset curation under `LIM-021` is the true critical-path prerequisite, because it requires owner authorization rather than engineering time.
