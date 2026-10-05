# OnBrand Limitations Register

Last updated: 2026-10-05

This is the living register for known limitations, evidence gaps, deferred safeguards, and scoring opportunities in the OnBrand framework and project-specific packs. It is intentionally root-level so release planning, implementation, audit, and handoff work all have one durable source of truth before new phase work begins.

This register does not replace phase specs, `STATUS.md`, `ROADMAP.md`, `CHANGELOG.md`, or `AUDIT_LOG.md`. It summarizes the current limitation, links back to the evidence, and records what must be true before the limitation can be closed.

## How to Use This Register

- Add or update an entry whenever a limitation is discovered, deferred, mitigated, or closed.
- Keep entries evidence-backed. Link to the governing spec, audit entry, reference file, test artifact, or runtime behavior.
- Do not close an entry only because a plan exists. Close it when acceptance evidence is committed.
- When an entry changes release scope, update `STATUS.md`, `ROADMAP.md`, `CHANGELOG.md`, and `AUDIT_LOG.md` in the same change.
- Scoring systems may triage, block, or flag work, but human approval remains required for brand, legal, likeness, and client-facing judgments unless a future spec explicitly says otherwise.

## Status Vocabulary

- `Open`: known limitation without committed mitigation.
- `Mitigated`: current workflow has a documented control, but the underlying limitation remains.
- `Deferred`: intentionally moved to a later phase or release gate.
- `Closed`: acceptance criteria are satisfied and evidence is committed.

## Priority Vocabulary

- `P0`: blocks release or creates a material security, legal, or client trust risk.
- `P1`: blocks the next planned phase, pilot expansion, or public release gate.
- `P2`: meaningful quality, portability, or operations limitation.
- `P3`: refinement that improves confidence, ergonomics, or maintainability.

## Index

| ID | Limitation | Priority | Status | Owner phase |
| --- | --- | --- | --- | --- |
| LIM-001 | Generated-image visual faithfulness and environment preservation are not automatically scored | P1 | Open | Phase 9 refinement |
| LIM-002 | Image provider execution and candidate-generation UX remain external to the runtime | P2 | Open | Phase 4 / Phase 9 refinement |
| LIM-003 | Copy allocation, phrase ownership, and cross-surface repetition QA | P1 | Closed | Phase 10 |
| LIM-004 | Claim truth verification, extraction, and copy-quality confidence remain review-based | P2 | Mitigated | Phase 10 / backlog |
| LIM-005 | Email-client and responsive visual compatibility are not covered by a committed render matrix | P1 | Open | Public release gate |
| LIM-006 | The Rider uses local-cache manifest fallback because the canonical public manifest URL is not configured | P1 | Open | Asset library / project setup |
| LIM-007 | Asset selection uses deterministic metadata scoring; sparse metadata still weakens ranking confidence | P2 | Mitigated | Asset library refinement |
| LIM-008 | Composition preview produces isolated HTML snippets, not bitmap thumbnails or scored visual options | P3 | Mitigated | Phase 8 refinement |
| LIM-009 | Review packages are not production-hosted send artifacts without explicit hosted asset URLs | P2 | Mitigated | Deployment handoff |
| LIM-010 | Cross-platform adapters need layered deterministic and live evidence | P1 | Mitigated | Phase 11 |
| LIM-011 | Public/private/sanitized distribution profiles are deferred; prompt rules are not a security boundary | P1 | Deferred | Phase 12 |
| LIM-012 | Cassia and non-Rider projects remain uncalibrated relative to The Rider pilot | P2 | Open | Project onboarding |
| LIM-013 | Public release support metadata, ownership contacts, and CODEOWNERS are unresolved | P2 | Open | Release governance |
| LIM-014 | Phase 9 lacks committed conceptual environment fixtures and human visual QA artifacts | P2 | Open | Phase 9 refinement |
| LIM-015 | Accessibility, contrast, readability, and alt-text quality checks are incomplete | P3 | Open | QA backlog |
| LIM-016 | Legal, fair-housing, financial, and regulated-copy checks are human-review flags, not compliance proof | P1 | Mitigated | Compliance governance |
| LIM-017 | Live agent invocation and model-behavior parity remain unverified | P1 | Open | Phase 11 live validation |
| LIM-018 | Jev semantic decision value, calibration, privacy approval, and fallback behavior are unverified | P2 | Open | Phase 13 pilot |
| LIM-019 | Copy QA counts logical slot owners, not every rendered replacement rule | P2 | Open | Phase 10 refinement |
| LIM-020 | Block metadata does not yet encode enough editorial layout intent | P1 | Mitigated | Phase 16 |

## Detailed Entries

### LIM-001: Generated-image visual faithfulness and environment preservation are not automatically scored

- Priority: P1
- Status: Open
- Owner phase: Phase 9 refinement
- Dependencies: Approved source/output pairs and Phase 9 provenance; representative visual review fixtures (LIM-014) and reviewer-calibrated acceptance thresholds.
- Evidence: [docs/specs/phase-09-grounded-image-generation.md](docs/specs/phase-09-grounded-image-generation.md), [projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-composition-preview.runtime.json](projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-composition-preview.runtime.json)
- Current behavior: Phase 9 records image provenance, source mappings, generated output records, package QA checks, and audit artifacts. It does not include automated visual similarity scoring or committed human visual QA evidence for the generated output.
- Risk and impact: A generated image can pass structural provenance checks while still drifting from the source environment, camera angle, furnishing continuity, brand mark fidelity, or requested subject. This is especially important for real estate, hospitality, brokers, named people, and recognizable environments.
- Current control: Generated images require explicit provenance, asset references, QA packaging, and review-oriented artifacts. Human review remains the final quality gate.
- Scoring could help: Yes. Candidate scores should triage and block obvious drift, not approve images alone.
- Candidate metrics: CLIP or DINO source-output similarity, SSIM or LPIPS for preserved regions, perceptual hash for near-duplicate drift, segmentation-mask deltas, feature matching for room geometry and perspective, object-detection continuity, saliency/focal-point distance, safe-area compliance, OCR integrity for embedded text, logo detector or template-match scores, and reviewer disagreement rate for threshold calibration.
- Closure criteria: Commit a documented visual QA protocol, at least one representative human visual QA artifact, automated similarity checks for source-grounded generated imagery, and acceptance thresholds that identify blocking, warning, and informational findings.

### LIM-002: Image provider execution and candidate-generation UX remain external to the runtime

- Priority: P2
- Status: Open
- Owner phase: Phase 4 / Phase 9 refinement
- Dependencies: A selected provider adapter or candidate workflow, explicit image-skill invocation, approved composition placement (Phase 8), and Phase 9 provenance records.
- Evidence: [docs/specs/phase-04-image-generation.md](docs/specs/phase-04-image-generation.md), [docs/specs/phase-09-grounded-image-generation.md](docs/specs/phase-09-grounded-image-generation.md), [projects/the-rider/skills/onbrand-the-rider-image/SKILL.md](projects/the-rider/skills/onbrand-the-rider-image/SKILL.md)
- Current behavior: The runtime validates and packages generated image records, but image generation itself remains provider-neutral and externally executed. Candidate approval, selection, and regeneration are governed by skill instructions rather than a first-class runtime flow.
- Risk and impact: Teams may interpret provenance validation as end-to-end generation support. Provider differences, prompt drift, and missing candidate histories can reduce reproducibility.
- Current control: Provider-neutral local file handoff and explicit generated-image records prevent the runtime from inventing provenance or asset origins.
- Scoring could help: Yes, especially for candidate triage.
- Candidate metrics: Prompt-to-asset grounding score, candidate diversity, source-reference coverage, policy or brand-risk flags, likeness-consent verification where applicable, and human approval outcome tracking.
- Closure criteria: Implement a documented provider adapter or candidate workflow, record all candidate decisions, and verify that package QA distinguishes generated, approved, rejected, and superseded outputs.

### LIM-003: Copy allocation, phrase ownership, and cross-surface repetition QA

- Priority: P1
- Status: Closed, 2026-10-03
- Owner phase: Phase 10
- Dependencies: Phase 5 typed slots and scaffold locks, Phase 8 composition ownership, Phase 9 declared baked-image provenance when used, and approved copy/allocation records. These dependencies are satisfied for the Rider runtime.
- Evidence: [ROADMAP.md](ROADMAP.md), [STATUS.md](STATUS.md), [docs/specs/phase-10-copy-allocation-qa.md](docs/specs/phase-10-copy-allocation-qa.md)
- Current behavior: All Rider build modes require approved `copy_allocation` before rendering. Stable owners, exact approved text, normalized occurrences, restricted phrases/names, declared baked-image text, scoped exemptions, claim-reference policy, and transparent similarity checks are enforced. Passing metadata/QA retain approved units and findings; failed validation preserves the previous package.
- Risk and impact: Repeated phrases can make campaigns sound templated, overstate authority, or duplicate claims across surfaces. The Phase 10 reference failure is the wellness smoke package repeating phrases such as "From the creators..." and "Same routine..." across multiple rendered surfaces.
- Current control: Committed runtime gates and 18 dedicated allocation tests, including responsive fallback allocation/QA coverage, plus runtime integration/regression coverage and compliant plans in all four Rider fixtures. Undeclared bitmap text, implicit locked scaffold/contact strings, paraphrases, and factual truth still require human review; these are outside the explicit campaign inventory contract.
- Scoring could help: Yes. Deterministic counts should lead where possible.
- Candidate metrics: Normalized phrase overlap, repeated visible-text counts, restricted phrase occurrence count, person or broker name repetition, surface ownership confidence, subject-preview overlap, alt-visible duplicate rate, and unsupported-claim confidence.
- Closure evidence: [Phase 10 evaluation](docs/evals/phase-10-copy-allocation-qa.md), [allocation tests](tests/test_rider_copy_allocation.py), and AUD-055. The live Composition Preview pilot passes 86 QA checks, including 26 allocation checks for 23 units, with 9 assets and a byte-audited ZIP. Ownership, failure fixtures, report integration, and reviewable remediation guidance are implemented.

### LIM-004: Claim truth verification, extraction, and copy-quality confidence remain review-based

- Priority: P2
- Status: Mitigated
- Owner phase: Phase 10 / backlog
- Dependencies: Phase 10 claim-reference records; approved retrievable evidence, human factual/legal review (LIM-016), and an editorial calibration dataset before automated confidence scoring.
- Evidence: [projects/the-rider/skills/onbrand-the-rider-email/references/copy-quality.md](projects/the-rider/skills/onbrand-the-rider-email/references/copy-quality.md), [docs/evals/copy-quality.md](docs/evals/copy-quality.md), [docs/specs/phase-10-copy-allocation-qa.md](docs/specs/phase-10-copy-allocation-qa.md)
- Current behavior: Phase 10 blocks units declared `requires-evidence` without references and retains those references for review. It also reports deterministic repetition and a transparent overlap score (warning 0.65, blocking 0.82). It does not extract claims, retrieve or verify sources, certify factual/legal support, run OCR, or compute a general copy-quality confidence score. Similarity thresholds have fixture evidence but no broader editorial calibration dataset.
- Risk and impact: Unsupported claims can slip through if a reviewer misses them, and reviewers may apply inconsistent thresholds across campaigns.
- Current control: Required-reference gating and supported/unsupported claim fixtures mitigate missing declared evidence. Project references still require human review for undeclared claims, source truth, image-text declarations, and similarity findings; AI-detector-style judgments remain prohibited.
- Scoring could help: Yes, with caveats.
- Candidate metrics: Claim extraction count, supported-claim coverage, citation/source availability, unsupported-claim confidence, restricted-domain keyword hits, phrase naturalness heuristics, and reviewer override rate. Scores should identify review needs, not assert legal or factual compliance.
- Closure criteria: Commit a claim-support QA workflow, fixtures for supported and unsupported claims, report fields for human review, and documented non-goals around AI authorship detection.

### LIM-005: Email-client and responsive visual compatibility are not covered by a committed render matrix

- Priority: P1
- Status: Open
- Owner phase: Public release gate
- Dependencies: Phase 5-7 representative packages, a defined client/viewport/dark-mode support matrix, available render tooling or services, and committed human review evidence.
- Evidence: [Phase 14 report](docs/evals/phase-14-rider-render-matrix.md), [machine report](docs/evals/render-matrix/rider-wellness-v1/render-report.json), [canonical Phase 16 client matrix](docs/evals/phase-16-rider-canonical-client-matrix.md), [Phase 14 spec](docs/specs/phase-14-email-render-matrix.md)
- Current behavior: Structural QA, package QA, and static compatibility checks exist. The owner-approved canonical Phase 16 proof now has a committed four-entry Playwright matrix and completed agent-assisted review at desktop/mobile and light/dark browser preferences. All entries pass mechanically and visually. Native Gmail, Outlook, and Apple Mail evidence is still pending.
- Risk and impact: A package can be structurally valid while rendering poorly in Outlook, Gmail, Apple Mail, mobile clients, or dark mode.
- Current control: Outlook-oriented structure guidance, compatibility references, QA reports, a versioned browser-preview contract, and the public-release gate requiring representative human and real-client compatibility review.
- Scoring could help: Yes.
- Candidate metrics: Playwright screenshots for web preview, email-service render snapshots, pixel diffs, layout shift measurements, media-query behavior checks, table/fallback validation, dark-mode deltas, and per-client pass rates.
- Closure criteria: Define the supported email-client matrix, commit representative render evidence, add regression fixtures, and record pass/fail status in package QA.

### LIM-006: The Rider uses local-cache manifest fallback because the canonical public manifest URL is not configured

- Priority: P1
- Status: Open
- Owner phase: Asset library / project setup
- Dependencies: Maintainer publication of a canonical public manifest URL, approved asset access, and fresh-clone availability/checksum validation without private cache assumptions.
- Evidence: [STATUS.md](STATUS.md), [docs/specs/phase-01-asset-library.md](docs/specs/phase-01-asset-library.md), [projects/the-rider/manifest-source.json](projects/the-rider/manifest-source.json)
- Current behavior: The Rider asset library can resolve through a local cache, but the canonical public Dropbox manifest URL is still blank. Validation reports the public URL as unconfigured.
- Risk and impact: Fresh consumers cannot reliably bootstrap The Rider assets from a public canonical source. Local cache behavior proves package development, not public project distribution.
- Current control: The local cache and manifest source file make the fallback explicit.
- Scoring could help: Limited. This is mostly a configuration and availability requirement.
- Candidate metrics: Manifest availability, checksum match, redirect stability, download success rate, asset count parity, and stale-cache age.
- Closure criteria: Configure the canonical public manifest URL, validate a fresh clone without private local cache assumptions, and record the passing command output.

### LIM-007: Asset selection uses deterministic metadata scoring; sparse metadata still weakens ranking confidence

- Priority: P2
- Status: Mitigated
- Owner phase: Asset library refinement
- Dependencies: Phase 1 validated catalog records, improved project-specific metadata and approval coverage, and representative reviewer selection/correction evidence.
- Evidence: [tools/asset_selection/selector.py](tools/asset_selection/selector.py), [projects/the-rider/skills/onbrand-the-rider-email/references/asset-selection.md](projects/the-rider/skills/onbrand-the-rider-email/references/asset-selection.md), [docs/specs/phase-01-asset-library.md](docs/specs/phase-01-asset-library.md)
- Current behavior: Asset selection scoring weights media type, approval status, category overlap, orientation, and close-candidate review requirements. This helps make selection deterministic, but sparse or inconsistent metadata can still produce weak ranking confidence.
- Risk and impact: A technically valid asset can be selected even when a more semantically appropriate asset exists but is poorly tagged.
- Current control: Materially close candidates trigger review requirements, and project guidance asks reviewers to avoid overusing near-duplicates.
- Scoring could help: Yes.
- Candidate metrics: Metadata completeness, semantic image-text similarity, category confidence, near-duplicate clustering, approval freshness, campaign reuse frequency, and reviewer correction rate.
- Closure criteria: Improve metadata coverage, add ranking confidence reporting, and verify that low-confidence or materially different candidates produce actionable review prompts.

### LIM-008: Composition preview produces isolated HTML snippets, not bitmap thumbnails or scored visual options

- Priority: P3
- Status: Mitigated
- Owner phase: Phase 8 refinement
- Dependencies: Phase 8 catalog/compatibility records and an available HTML render tool; implement a thumbnail board only when creative-review workflows require it.
- Evidence: [docs/specs/phase-08-composition-preview.md](docs/specs/phase-08-composition-preview.md)
- Current behavior: Composition preview supports machine-readable option records and isolated HTML snippets. It does not produce bitmap thumbnail sheets, side-by-side rendered previews, or scored option usefulness.
- Risk and impact: Reviewers can compare options, but the workflow is file-based and may be slower than a visual thumbnail board.
- Current control: Option records, compatibility checks, and isolated HTML snippets provide deterministic review artifacts.
- Scoring could help: Somewhat.
- Candidate metrics: Module compatibility pass rate, required-content coverage, copy density, asset uniqueness, preview render dimensions, and reviewer selection rate.
- Closure criteria: Add rendered thumbnails or an equivalent visual board if future workflows need faster creative comparison, with evidence that option compatibility still uses deterministic checks.

### LIM-009: Review packages are not production-hosted send artifacts without explicit hosted asset URLs

- Priority: P2
- Status: Mitigated
- Owner phase: Deployment handoff
- Dependencies: Phase 6 portable packages, an explicit approved public asset base URL, a selected ESP/deployment platform, and verification through that platform's import/send workflow.
- Evidence: [tools/rider_campaign_runtime/README.md](tools/rider_campaign_runtime/README.md), [projects/the-rider/skills/onbrand-the-rider-email/references/distribution-package.md](projects/the-rider/skills/onbrand-the-rider-email/references/distribution-package.md), [docs/PRD.md](docs/PRD.md)
- Current behavior: Runtime packages can include relative image paths suitable for package review. Hosted deployment HTML requires an explicit hosted asset base URL. The runtime does not invent production hosting URLs.
- Risk and impact: A valid ZIP package may not be immediately send-ready in an ESP or production campaign system.
- Current control: Distribution guidance requires identifying external assets and hosted URL assumptions explicitly.
- Scoring could help: Limited.
- Candidate metrics: Asset self-containment, external-reference count, hosted URL coverage, broken-link count, ZIP integrity, HTML size, and ESP import warnings.
- Closure criteria: Choose the final deployment platform and image-hosting handoff, document send-ready requirements, and verify a hosted package through the target workflow.

### LIM-010: Cross-platform adapters need layered deterministic and live evidence

- Priority: P1
- Status: Mitigated
- Owner phase: Phase 11
- Dependencies: Canonical Phase 7-10 JSON/CLI contracts, available target-platform execution environments, thin explicit-invocation adapters, and committed artifact/QA parity fixtures.
- Evidence: [Compatibility](docs/COMPATIBILITY.md), [Phase 11 evaluation](docs/evals/phase-11-cross-platform-compatibility.md), [parity report](docs/evals/phase-11-parity-report.json), [adapter tests](tests/test_platform_adapters.py)
- Current behavior: Thin Codex/Claude/CLI adapters, manual policies, versioned contracts, and independent realistic runtime builds pass all 13 critical parity components at 100. Live model invocation is not established.
- Risk and impact: Deterministic adapter parity could be mistaken for observed live host behavior or independent model interpretation.
- Current control: All critical components require 100; shared recursive JSON-semantic comparison and hashing prevent boolean/number coercion at parity, approval/selection, and asset-size boundaries. The initial 175a284 audit defects are corrected with type-sensitive regressions and a rebuilt realistic pilot. Finite numeric equivalence and parser-precision boundaries are explicit in the compatibility guide. Live claims remain gated by LIM-017.
- Scoring could help: Yes, as parity evidence.
- Candidate metrics: Fixture output parity, command-invocation compatibility, generated artifact diffs, QA result parity, and adapter-specific failure counts.
- Closure criteria: Deterministic implementation/report/docs criteria are met; obtain live manual host evidence under LIM-017 before closing the full cross-platform support gap.

### LIM-011: Public/private/sanitized distribution profiles are deferred; prompt rules are not a security boundary

- Priority: P1
- Status: Deferred
- Owner phase: Phase 12
- Dependencies: Owner-approved physical public/private/broker source separation, maintained package allowlists, security/history review, and clean-build inventory/secret tests before restricted distribution.
- Evidence: [ROADMAP.md](ROADMAP.md), [STATUS.md](STATUS.md), [docs/specs/phase-12-distribution-profiles.md](docs/specs/phase-12-distribution-profiles.md), [docs/DISTRIBUTION_SECURITY.md](docs/DISTRIBUTION_SECURITY.md)
- Current behavior: Distribution-profile work is deferred. The repository currently contains internal-capability source and should not be treated as a broker-restricted public package. Prompt rules and instructions are not source isolation.
- Risk and impact: Publishing the wrong package could expose internal guidance, client-specific material, or capabilities intended only for controlled use.
- Current control: Release blockers explicitly forbid broker-restricted distribution until physical source/package separation exists.
- Scoring could help: Yes, but only as a supplement to physical separation.
- Candidate metrics: File inventory allowlist pass rate, private-reference count, forbidden-path inclusion, package diff against public profile, secret scan results, and generated archive manifest checksums.
- Closure criteria: Implement physical public/private/sanitized package profiles, commit inventory tests, document public-history caveats, and verify broker-safe output from a clean build.

### LIM-012: Cassia and non-Rider projects remain uncalibrated relative to The Rider pilot

- Priority: P2
- Status: Open
- Owner phase: Project onboarding
- Dependencies: Project-specific approved brand standards, canonical HTML, legal/footer data, logos, and asset catalog; complete Phase 1-6 calibration and representative package QA per project.
- Evidence: [STATUS.md](STATUS.md), [ROADMAP.md](ROADMAP.md), [AUDIT_LOG.md](AUDIT_LOG.md)
- Current behavior: The Rider is the active runtime pilot. Cassia and other projects remain scaffolded or planned pending brand standards, canonical HTML, footers, logos, asset catalog material, and project-specific calibration.
- Risk and impact: The Rider evidence should not be generalized to all OnBrand projects without onboarding and validation.
- Current control: Project portfolio status records Cassia as waiting or planned, and earlier audit notes describe Cassia as provisional.
- Scoring could help: Somewhat.
- Candidate metrics: Project readiness checklist completion, brand-reference coverage, asset-catalog completeness, footer/legal availability, module compatibility fixtures, and project-specific QA pass rate.
- Closure criteria: Complete onboarding inputs for each project, add project fixtures, run representative package QA, and update portfolio status.

### LIM-013: Public release support metadata, ownership contacts, and CODEOWNERS are unresolved

- Priority: P2
- Status: Open
- Owner phase: Release governance
- Dependencies: Owner decisions on support contacts, CODEOWNERS identities, repository visibility, and intended distribution profiles (LIM-011).
- Evidence: [STATUS.md](STATUS.md), [docs/PRD.md](docs/PRD.md)
- Current behavior: The project still needs decisions on public repository visibility, support email, CODEOWNERS identities, and related release metadata.
- Risk and impact: Public users may lack clear support, escalation, ownership, or contribution routing.
- Current control: Release blockers and open decisions keep these items visible.
- Scoring could help: Limited.
- Candidate metrics: Release-readiness checklist status, required metadata presence, support route test, and ownership coverage for governed paths.
- Closure criteria: Commit support contacts, CODEOWNERS, repository visibility decisions, and any public release metadata required by the chosen distribution profile.

### LIM-014: Phase 9 lacks committed conceptual environment fixtures and human visual QA artifacts

- Priority: P2
- Status: Open
- Owner phase: Phase 9 refinement
- Dependencies: Phase 9 source/generated provenance, approved representative conceptual and source-grounded outputs, and human reviewers who can commit visual acceptance evidence.
- Evidence: [docs/specs/phase-09-grounded-image-generation.md](docs/specs/phase-09-grounded-image-generation.md), [projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-composition-preview.runtime.json](projects/the-rider/skills/onbrand-the-rider-email/examples/rider-wellness-composition-preview.runtime.json)
- Current behavior: The committed Phase 9 pilot evidence demonstrates structural runtime packaging for one generated-image variant, including QA checks and referenced assets. It does not yet include a broader conceptual environment fixture set or a committed human visual QA artifact.
- Risk and impact: Schema support for generated imagery can look more comprehensive than the current fixture coverage proves.
- Current control: The Phase 9 spec requires visual QA evidence, and the runtime preserves source/generated provenance for reviewers.
- Scoring could help: Yes, after fixtures exist.
- Candidate metrics: Fixture category coverage, conceptual-vs-source-grounded classification, environment preservation score, reviewer approval status, and failure-mode coverage.
- Closure criteria: Add representative conceptual and source-grounded generated-image fixtures, attach human visual QA evidence, and run runtime package QA across them.

### LIM-015: Accessibility, contrast, readability, and alt-text quality checks are incomplete

- Priority: P3
- Status: Open
- Owner phase: QA backlog
- Dependencies: Defined email accessibility scope, Phase 5-7 rendered packages, reliable contrast/structure checks, and client/dark-mode rendering evidence (LIM-005) for visual findings.
- Evidence: [projects/the-rider/skills/onbrand-the-rider-email/references/copy-quality.md](projects/the-rider/skills/onbrand-the-rider-email/references/copy-quality.md), [docs/specs/phase-05-html-variants.md](docs/specs/phase-05-html-variants.md), [tools/rider_campaign_runtime/README.md](tools/rider_campaign_runtime/README.md)
- Current behavior: The workflow contains copy and package QA expectations, but it does not yet provide comprehensive automated accessibility, contrast, readability, or alt-text quality scoring across generated packages.
- Risk and impact: A package can pass structural checks while still being hard to read, weak in dark mode, or missing useful alt text.
- Current control: Human review and package QA can flag missing obvious alt text or structural issues.
- Scoring could help: Yes.
- Candidate metrics: WCAG contrast ratios, font-size and line-height checks, text density, reading level, heading structure, image alt coverage, decorative-image classification, link-label quality, and dark-mode contrast deltas.
- Closure criteria: Define accessibility scope for email artifacts, add automated checks where reliable, and record human-review expectations for cases automation cannot judge.

### LIM-016: Legal, fair-housing, financial, and regulated-copy checks are human-review flags, not compliance proof

- Priority: P1
- Status: Mitigated
- Owner phase: Compliance governance
- Dependencies: Qualified human/legal reviewers, approved project facts and disclaimers, an owner-approved escalation policy, and declared Phase 10 claim references when support is required.
- Evidence: [projects/the-rider/skills/onbrand-the-rider-email/references/copy-quality.md](projects/the-rider/skills/onbrand-the-rider-email/references/copy-quality.md), [docs/evals/copy-quality.md](docs/evals/copy-quality.md), [docs/PRD.md](docs/PRD.md)
- Current behavior: Guidance can flag potential legal, fair-housing, financial, or regulated-copy concerns for human review. It does not certify compliance or replace qualified legal review.
- Risk and impact: Users may over-trust automated or agent review if docs do not keep this boundary explicit.
- Current control: Project guidance says sensitive claims require human review and avoids asserting compliance.
- Scoring could help: Yes, only as risk triage.
- Candidate metrics: Regulated-term hits, claim-risk category, protected-class language flags, pricing/availability claim extraction, required-disclaimer presence, and human legal-review status.
- Closure criteria: Commit a compliance-review policy, required escalation paths, and explicit non-goals for automated legal determinations.

### LIM-017: Live agent invocation and model-behavior parity remain unverified

- Priority: P1
- Status: Open
- Owner phase: Phase 11 live validation
- Dependencies: Installed authenticated CLIs, permitted local app-server/state access, explicit HUMAN invocation, and representative approved inputs; no forced login or permission bypass.
- Evidence: [Phase 11 evaluation](docs/evals/phase-11-cross-platform-compatibility.md), [compatibility scope](docs/COMPATIBILITY.md)
- Current behavior: Codex 0.160.0 is authenticated but its bounded read-only manual request fails before model execution due to local sandbox app-server/database restrictions. Claude Code 2.1.273 is installed but not authenticated; no login/model call was attempted. Deterministic runtime parity passes, not live agent/model behavior.
- Risk and impact: Host skill discovery/manual-only behavior, tool permissions, and new-brief model interpretation can differ even when shared runtime outputs match.
- Current control: No live success claim; no authentication changes, credentials copying, or sandbox bypass. Source/manual policy checks and deterministic artifact evidence are clearly labeled.
- Scoring could help: Yes, only with separately observed live evidence.
- Candidate metrics: Observed explicit skill discovery, absence of implicit invocation, request/spec hashes, tool execution outcomes, model-produced approval fidelity, and artifact parity by authenticated host.
- Closure criteria: Commit permitted authenticated manual invocation evidence for both platforms, representative live artifact comparisons, and any remaining model-interpretation deviations. Keep legal/visual approval external.

### LIM-018: Jev semantic action routing remains unfit for production

- Priority: P2
- Status: Open
- Owner phase: Phase 13 pilot
- Dependencies: Phase 10 lexical baseline, a versioned and de-identified Rider evaluation set, owner-approved hosted-data handling, and recorded-response tests before live API evaluation.
- Evidence: [Phase 13 spec](docs/specs/phase-13-jev-semantic-decision-pilot.md), [holdout report](docs/evals/phase-13-jev-holdout-report.md), [machine-readable holdout report](docs/evals/phase-13-jev-holdout-report.v1.json), [frozen dataset](docs/evals/data/phase-13-rider-copy-pairs.v1.frozen.json), [Phase 10 baseline](docs/specs/phase-10-copy-allocation-qa.md)
- Current behavior: OnBrand preserves the frozen Rider dataset, reviews, adjudication, lexical baseline, live calibration, locked policy, and live holdout evidence. Holdout label agreement reached 8/9, but the candidate policy matched only 5/9 actions versus 4/9 for the lexical baseline, produced one false allow, and routed 44.4% to review. Version 1 is `revise`, has no production effect, and its spent holdout cannot validate a revised policy.
- Risk and impact: Adding an uncalibrated hosted decision model could increase false positives, hide model-version drift, transmit unnecessary project data, create an availability dependency, or be mistaken for visual, factual, legal, or compliance proof.
- Current control: Jev is approved only as an optional evaluation candidate. Existing deterministic QA remains authoritative, direct visual similarity remains outside Jev, and no runtime or skill behavior has changed.
- Scoring could help: Yes, if measured against the existing baseline.
- Candidate metrics: Semantic duplicate precision/recall, false-positive and false-negative rates, claim-support triage accuracy, confidence/review coverage, reviewer agreement, override rate, latency, provider failure rate, token cost, and cross-adapter receipt parity.
- Closure criteria: Either keep Jev disabled and formally accept or remove the optional evaluation code, or complete a version 2 pilot with a fresh independently reviewed dataset, newly locked policy, untouched holdout, no false allows, bounded review rate, measurable baseline improvement, fallback verification, and cross-adapter receipt parity. This does not close visual-similarity limitations.

### LIM-019: Copy QA counts logical slot owners, not every rendered replacement rule

- Priority: P2
- Status: Open
- Owner phase: Phase 10 refinement
- Dependencies: Phase 10 allocation ownership, scaffold slot rules, and representative modules where one slot intentionally or accidentally replaces text more than once.
- Evidence: [corrected Phase 15 proof](docs/evals/phase-15-rider-wellness-corrected-proof.md), [slot renderer](tools/rider_campaign_runtime/slots.py), [copy allocation](tools/rider_campaign_runtime/copy_allocation.py)
- Current behavior: Copy allocation counts each declared slot as one logical owner. A slot may contain multiple replacement rules and therefore render the same approved value more than once. The CFG-05 review exposed this boundary in `B-04`: two previously locked authority rows were visible in the output but absent from the slot inventory. They are now separate slots with unique content, so the corrected proof has one canonical authority statement. The general multiplicity boundary remains for other multi-rule slots such as the repeated primary CTA.
- Risk and impact: A package can pass logical-owner repetition QA while rendering the same text multiple times from one slot. Some repetition is intentional, especially CTAs and responsive fallbacks, but accidental repeated editorial messages may be undercounted.
- Current control: Known editorial repeats receive distinct slots or are resolved by module/static selection; browser review remains required. Responsive fallback duplication is still treated as one logical owner by design.
- Scoring could help: Limited. Deterministic rendered-occurrence counting is preferable; scoring is useful only for deciding whether distinct rendered phrases are semantically repetitive.
- Candidate metrics: Replacement-rule multiplicity, rendered visible-text occurrence count, owner-to-render ratio, intentional-repeat classification, responsive-branch identity, and reviewer override rate.
- Closure criteria: Add a rendered-copy inventory that distinguishes intentional responsive duplication from multiple visible placements, require explicit reuse policy for multi-placement slots, and add positive CTA plus negative editorial-repeat fixtures.

### LIM-020: Block metadata does not yet encode enough editorial layout intent

- Priority: P1
- Status: Mitigated
- Owner phase: Phase 16
- Dependencies: The annotated expanded Rider scaffold is received and marker-validated; nested-annotation parsing, stable metadata identities, and the existing Phase 8/15 module catalog and proof workflow remain required.
- Evidence: [Phase 16 specification](docs/specs/phase-16-scaffold-expansion-and-layout-calibration.md), [Phase 16 intake](docs/evals/phase-16-rider-scaffold-intake.md), [Phase 16 layout gallery](docs/evals/phase-16-rider-layout-gallery.md), [Phase 16 branded proof](docs/evals/phase-16-rider-wellness-branded-proof.md), [Phase 15 corrected proof](docs/evals/phase-15-rider-wellness-corrected-proof.md)
- Current behavior: The Phase 16 parser, metadata, slot map, and composition planner classify and enforce 20 modules, 17 granular annotations, required/optional content, four container-owned conditional list/payoff rows, repeating lists, campaign compatibility, predecessor/successor rules, and exclusion groups. `S-02` carries wellness/sauna guidance, `S-04` carries building-arrival guidance, and the explicit `S-01` then `S-02` exception is permitted while other static-message pairs remain blocked. The owner selected and approved the `SEQ-LF-07` proof, and the Phase 16 scaffold and sidecars are now canonical. Presets are not automatically ranked, and the optional full light-body conversion is not yet a coordinated runtime transform.
- Risk and impact: An assembled email can pass structural and package QA while still using an awkward block sequence, mismatched density, redundant visual rhythm, or a content block that is technically valid but contextually wrong.
- Current control: Composition Preview and human review remain required. Stable `SEQ-*` choices expose complete block order before proof assembly, and every campaign requires a fresh header/hero approval. Candidate build flags can evaluate a future scaffold without changing canonical defaults.
- Scoring could help: Yes, after the annotation vocabulary is stable. Deterministic compatibility and content-fit rules should lead; scoring may rank multiple valid sequences.
- Candidate metrics: Required-content coverage, copy-density fit, image-count fit, adjacent color-transition compatibility, duplicate-purpose count, narrative-role coverage, sequence-rule violations, mobile-height balance, and reviewer selection or correction rate.
- Closure criteria: Add evidence-backed ranking metrics for multiple valid sequences, implement a coordinated light-body transform if approved for a real campaign, and validate representative layouts in the browser and native email-client matrices.

## Entry Template

Use this template for new limitations:

```markdown
### LIM-000: Short title

- Priority: P1
- Status: Open
- Owner phase: Phase N / backlog
- Dependencies: Required phases, inputs, tooling, or approval conditions; use None when no prerequisites apply.
- Evidence: `path/to/evidence.md`
- Current behavior: ...
- Risk and impact: ...
- Current control: ...
- Scoring could help: Yes/No/Limited.
- Candidate metrics: ...
- Closure criteria: ...
```

## Change History

- 2026-10-03: Created root limitations register covering Phase 1 through Phase 12 findings before Phase 10 implementation.
- 2026-10-03: Closed LIM-003 with committed Phase 10 runtime/test/pilot evidence; mitigated LIM-004 through declared claim-reference gating and transparent repetition scoring while keeping source verification, OCR, and calibration limitations explicit.
- 2026-10-03: Added explicit dependency conditions to all 16 limitation entries and the entry template after completion audit; retained stable IDs, status, closure evidence, and prior history.
- 2026-10-03: Mitigated LIM-010 with versioned thin adapters and 100% deterministic parity; added LIM-017 for precise unverified live agent/model behavior. Phase 12 remains deferred.
- 2026-10-03: Completion audit found two P2 boolean/number coercion gaps in parity and composition approval matching at 175a284. Corrected shared JSON-semantic comparison/hashing and adjacent approval/selection/size boundaries; 15 new regressions and the rebuilt pilot close those defects. LIM-010 remains mitigated because LIM-017 live evidence is still open.
- 2026-10-03: Added LIM-018 and the approved Phase 13 Jev pilot boundary. Jev remains optional, text-only, unimplemented, and subject to held-out evaluation, privacy approval, deterministic fallback, and a keep/remove decision.
- 2026-10-03: Added the Phase 13 evaluation foundation: 26 provisional de-identified cases, 9 held out, a strict validator and schema, blind review worksheet, and lexical baseline. Provider implementation still waits for independent label adjudication.
- 2026-10-03: Added dataset-bound reviewer templates, strict completed-response validation, independent-reviewer enforcement, and deterministic disagreement reporting. No review or adjudication result is claimed yet.
- 2026-10-03: Committed two completed blinded reviews and their deterministic comparison: 21/26 full agreement, 25/26 label agreement, and five explicit adjudication cases. No disputed case was silently resolved.
- 2026-10-03: Adjudicated all five review disputes through a hash-bound policy artifact and generated a separate frozen dataset without changing the provisional snapshot or holdout text. The action baseline remains 14/26.
- 2026-10-03: Locked Jev question set version 1 for calibration only and generated 17 provider-shaped requests without expected labels, review evidence, contact data, holdout cases, or production effect. No network call was made.
- 2026-10-03: Added the optional TypeSafe provider and receipt boundary with double opt-in, pinned-model/typed-answer validation, disabled fallback, secret-free receipts, and no production effect. The committed receipt proves disabled behavior only; no live call was made.
- 2026-10-03: Ran the explicitly owner-approved 17-case live calibration. Jev matched 13/17 semantic labels; the conservative candidate policy matched 16/17 actions versus the lexical baseline's 10/17, routing three cases to review. Production remains disabled and the nine-case holdout remains untouched.
- 2026-10-03: Locked the candidate policy before running the separately approved nine-case holdout. Jev matched 8/9 semantic labels but only 5/9 actions, with one false allow and four review routes. Version 1 failed the keep gate and is marked `revise`; production remains disabled.
- 2026-10-03: Added Phase 15 Workstream A selection evidence: 16 labeled compatible Rider header/hero configurations, a grouped gallery, and configuration-bound plan validation. LIM-005 remains open because human visual selection and real-client evidence are still pending.
- 2026-10-03: Implemented Phase 15 Workstream C by auto-inventorying included static copy, rejecting partial declarations, retaining owner context, and narrowing similarity exemptions to exact pairs. Semantic paraphrase detection remains limited and human-reviewed.
- 2026-10-03: Added LIM-019 after the corrected CFG-05 proof exposed that one logical slot can render through multiple replacement rules. The Rider authority rows now have distinct slots and copy, while general rendered-occurrence accounting remains open.
- 2026-10-03: Added LIM-020 after owner review confirmed that the corrected proof is a major improvement but still needs richer block-layout semantics. Phase 16 now waits for an annotated expanded Rider scaffold.
- 2026-10-04: Received and marker-validated the annotated expanded Rider scaffold. LIM-020 remains open while nested annotations, repeated static identities, sequence semantics, and a new owner-approved proof are implemented.
- 2026-10-04: Implemented nested annotation parsing and checksum-bound refined metadata for 20 modules and 14 annotations. LIM-020 remains open because the production slot map, sequence enforcement/ranking, previews, and owner-approved proof still use the prior runtime model.
- 2026-10-04: Implemented deterministic Phase 16 slots and composition enforcement with required/optional behavior, structured repeating lists, negative sequence fixtures, and stable codes. LIM-020 remains open for visual sequence ranking, regenerated gallery review, branded proof approval, and canonical promotion.
- 2026-10-04: Generated and inspected Phase 16 module, header/hero, and complete sequence galleries. Eight runtime-valid `SEQ-*` presets are committed with no missing targets or marker leaks. LIM-020 remains open for owner sequence selection, any requested light-body transformation, the new branded proof, and canonical promotion.
- 2026-10-04: Continuity review found that the initial eight presets omitted the approved CFG-05 `H-01 + AI-01` combination. Added `SEQ-LF-07` as a ninth proposed sequence with the refined body, one authority block, and pre-footer; owner approval remains pending.
- 2026-10-05: The owner selected `SEQ-LF-07`, then clarified that its wellness narrative requires `S-02` immediately after `S-01`. Creative guidance now identifies `S-02` as the sauna/wellness block and `S-04` as the building-arrival block. The revised proof passes 69 QA checks and clean browser diagnostics. LIM-020 remains open for owner visual approval, any resulting layout changes, reproducible browser-matrix evidence, native email-client review, and canonical promotion.
- 2026-10-05: Preserved the CSS-corrected 102-row scaffold and implemented four nested conditional list/payoff containers. The regenerated proof retains the two populated list rows and removes the two absent list families as balanced table units. Full discovery passes 179 tests. LIM-020 remains open for owner visual approval, any further annotated layout changes, reproducible browser-matrix evidence, native email-client review, and canonical promotion.
- 2026-10-05: The owner accepted the canonical-promotion recommendation. The Phase 16 trio and migrated fixtures now drive ordinary builds, the Phase 15 trio is archived as regression provenance, and the approved proof reproduces byte-for-byte without override flags. LIM-020 is mitigated; sequence ranking, optional full-light transformation, and native-client evidence remain open.
