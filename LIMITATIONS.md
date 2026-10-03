# OnBrand Limitations Register

Last updated: 2026-10-03

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
| LIM-003 | Copy allocation, phrase ownership, and cross-surface repetition QA are not implemented | P1 | Open | Phase 10 |
| LIM-004 | Unsupported-claim and copy-quality confidence are review-based, not scored or citation-backed | P2 | Open | Phase 10 / backlog |
| LIM-005 | Email-client and responsive visual compatibility are not covered by a committed render matrix | P1 | Open | Public release gate |
| LIM-006 | The Rider uses local-cache manifest fallback because the canonical public manifest URL is not configured | P1 | Open | Asset library / project setup |
| LIM-007 | Asset selection uses deterministic metadata scoring; sparse metadata still weakens ranking confidence | P2 | Mitigated | Asset library refinement |
| LIM-008 | Composition preview produces isolated HTML snippets, not bitmap thumbnails or scored visual options | P3 | Mitigated | Phase 8 refinement |
| LIM-009 | Review packages are not production-hosted send artifacts without explicit hosted asset URLs | P2 | Mitigated | Deployment handoff |
| LIM-010 | Claude Code and other non-Codex adapters are planned but not implemented or parity-tested | P1 | Deferred | Phase 11 |
| LIM-011 | Public/private/sanitized distribution profiles are deferred; prompt rules are not a security boundary | P1 | Deferred | Phase 12 |
| LIM-012 | Cassia and non-Rider projects remain uncalibrated relative to The Rider pilot | P2 | Open | Project onboarding |
| LIM-013 | Public release support metadata, ownership contacts, and CODEOWNERS are unresolved | P2 | Open | Release governance |
| LIM-014 | Phase 9 lacks committed conceptual environment fixtures and human visual QA artifacts | P2 | Open | Phase 9 refinement |
| LIM-015 | Accessibility, contrast, readability, and alt-text quality checks are incomplete | P3 | Open | QA backlog |
| LIM-016 | Legal, fair-housing, financial, and regulated-copy checks are human-review flags, not compliance proof | P1 | Mitigated | Compliance governance |

## Detailed Entries

### LIM-001: Generated-image visual faithfulness and environment preservation are not automatically scored

- Priority: P1
- Status: Open
- Owner phase: Phase 9 refinement
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
- Evidence: [docs/specs/phase-04-image-generation.md](docs/specs/phase-04-image-generation.md), [docs/specs/phase-09-grounded-image-generation.md](docs/specs/phase-09-grounded-image-generation.md), [projects/the-rider/skills/onbrand-the-rider-image/SKILL.md](projects/the-rider/skills/onbrand-the-rider-image/SKILL.md)
- Current behavior: The runtime validates and packages generated image records, but image generation itself remains provider-neutral and externally executed. Candidate approval, selection, and regeneration are governed by skill instructions rather than a first-class runtime flow.
- Risk and impact: Teams may interpret provenance validation as end-to-end generation support. Provider differences, prompt drift, and missing candidate histories can reduce reproducibility.
- Current control: Provider-neutral local file handoff and explicit generated-image records prevent the runtime from inventing provenance or asset origins.
- Scoring could help: Yes, especially for candidate triage.
- Candidate metrics: Prompt-to-asset grounding score, candidate diversity, source-reference coverage, policy or brand-risk flags, likeness-consent verification where applicable, and human approval outcome tracking.
- Closure criteria: Implement a documented provider adapter or candidate workflow, record all candidate decisions, and verify that package QA distinguishes generated, approved, rejected, and superseded outputs.

### LIM-003: Copy allocation, phrase ownership, and cross-surface repetition QA are not implemented

- Priority: P1
- Status: Open
- Owner phase: Phase 10
- Evidence: [ROADMAP.md](ROADMAP.md), [STATUS.md](STATUS.md), [docs/specs/phase-10-copy-allocation-qa.md](docs/specs/phase-10-copy-allocation-qa.md)
- Current behavior: Phase 10 is approved but not implemented. The framework does not yet enforce owner slots, restricted phrases, name-deduplication, or repeated authority-language checks across visible text, baked imagery, alt text, metadata, subject lines, and preview text.
- Risk and impact: Repeated phrases can make campaigns sound templated, overstate authority, or duplicate claims across surfaces. The Phase 10 reference failure is the wellness smoke package repeating phrases such as "From the creators..." and "Same routine..." across multiple rendered surfaces.
- Current control: Human review, copy references, and audit notes can flag repetition manually.
- Scoring could help: Yes. Deterministic counts should lead where possible.
- Candidate metrics: Normalized phrase overlap, repeated visible-text counts, restricted phrase occurrence count, person or broker name repetition, surface ownership confidence, subject-preview overlap, alt-visible duplicate rate, and unsupported-claim confidence.
- Closure criteria: Implement Phase 10 QA with fixtures, failure cases, runtime/report integration, and documented remediation guidance.

### LIM-004: Unsupported-claim and copy-quality confidence are review-based, not scored or citation-backed

- Priority: P2
- Status: Open
- Owner phase: Phase 10 / backlog
- Evidence: [projects/the-rider/skills/onbrand-the-rider-email/references/copy-quality.md](projects/the-rider/skills/onbrand-the-rider-email/references/copy-quality.md), [docs/evals/copy-quality.md](docs/evals/copy-quality.md), [docs/specs/phase-10-copy-allocation-qa.md](docs/specs/phase-10-copy-allocation-qa.md)
- Current behavior: Copy-quality guidance is contextual. It flags unsupported facts, policy-sensitive assertions, and artificial-sounding phrases, but it does not compute a confidence score, citation coverage score, or automated claim-support report.
- Risk and impact: Unsupported claims can slip through if a reviewer misses them, and reviewers may apply inconsistent thresholds across campaigns.
- Current control: Project references require human review for unsupported facts and prohibit claiming certainty from AI-detector-style judgments.
- Scoring could help: Yes, with caveats.
- Candidate metrics: Claim extraction count, supported-claim coverage, citation/source availability, unsupported-claim confidence, restricted-domain keyword hits, phrase naturalness heuristics, and reviewer override rate. Scores should identify review needs, not assert legal or factual compliance.
- Closure criteria: Commit a claim-support QA workflow, fixtures for supported and unsupported claims, report fields for human review, and documented non-goals around AI authorship detection.

### LIM-005: Email-client and responsive visual compatibility are not covered by a committed render matrix

- Priority: P1
- Status: Open
- Owner phase: Public release gate
- Evidence: [ROADMAP.md](ROADMAP.md), [STATUS.md](STATUS.md), [AUDIT_LOG.md](AUDIT_LOG.md), [docs/specs/phase-05-html-variants.md](docs/specs/phase-05-html-variants.md)
- Current behavior: Structural QA, package QA, and static compatibility checks exist, but representative desktop/mobile render evidence and broader email-client compatibility review remain pending. Earlier audit notes recorded that local browser rendering was unavailable during one review and that human/client visual review remained required.
- Risk and impact: A package can be structurally valid while rendering poorly in Outlook, Gmail, Apple Mail, mobile clients, or dark mode.
- Current control: Outlook-oriented structure guidance, compatibility references, QA reports, and the public-release gate requiring representative human and compatibility review.
- Scoring could help: Yes.
- Candidate metrics: Playwright screenshots for web preview, email-service render snapshots, pixel diffs, layout shift measurements, media-query behavior checks, table/fallback validation, dark-mode deltas, and per-client pass rates.
- Closure criteria: Define the supported email-client matrix, commit representative render evidence, add regression fixtures, and record pass/fail status in package QA.

### LIM-006: The Rider uses local-cache manifest fallback because the canonical public manifest URL is not configured

- Priority: P1
- Status: Open
- Owner phase: Asset library / project setup
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
- Evidence: [tools/rider_campaign_runtime/README.md](tools/rider_campaign_runtime/README.md), [projects/the-rider/skills/onbrand-the-rider-email/references/distribution-package.md](projects/the-rider/skills/onbrand-the-rider-email/references/distribution-package.md), [docs/PRD.md](docs/PRD.md)
- Current behavior: Runtime packages can include relative image paths suitable for package review. Hosted deployment HTML requires an explicit hosted asset base URL. The runtime does not invent production hosting URLs.
- Risk and impact: A valid ZIP package may not be immediately send-ready in an ESP or production campaign system.
- Current control: Distribution guidance requires identifying external assets and hosted URL assumptions explicitly.
- Scoring could help: Limited.
- Candidate metrics: Asset self-containment, external-reference count, hosted URL coverage, broken-link count, ZIP integrity, HTML size, and ESP import warnings.
- Closure criteria: Choose the final deployment platform and image-hosting handoff, document send-ready requirements, and verify a hosted package through the target workflow.

### LIM-010: Claude Code and other non-Codex adapters are planned but not implemented or parity-tested

- Priority: P1
- Status: Deferred
- Owner phase: Phase 11
- Evidence: [ROADMAP.md](ROADMAP.md), [STATUS.md](STATUS.md), [docs/PRD.md](docs/PRD.md), [docs/specs/phase-11-cross-platform-compatibility.md](docs/specs/phase-11-cross-platform-compatibility.md)
- Current behavior: Codex is the validated execution environment. Cross-platform support is planned, but Claude Code adapter parity, invocation checks, and output parity fixtures have not been implemented.
- Risk and impact: Public docs could overstate portability if they imply that non-Codex agents are already supported.
- Current control: Current docs identify Phase 11 as planned and say not to claim adapter support until parity validation passes.
- Scoring could help: Yes, as parity evidence.
- Candidate metrics: Fixture output parity, command-invocation compatibility, generated artifact diffs, QA result parity, and adapter-specific failure counts.
- Closure criteria: Implement thin adapters, run parity fixtures, commit a parity report, and update release docs with supported environments.

### LIM-011: Public/private/sanitized distribution profiles are deferred; prompt rules are not a security boundary

- Priority: P1
- Status: Deferred
- Owner phase: Phase 12
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
- Evidence: [projects/the-rider/skills/onbrand-the-rider-email/references/copy-quality.md](projects/the-rider/skills/onbrand-the-rider-email/references/copy-quality.md), [docs/evals/copy-quality.md](docs/evals/copy-quality.md), [docs/PRD.md](docs/PRD.md)
- Current behavior: Guidance can flag potential legal, fair-housing, financial, or regulated-copy concerns for human review. It does not certify compliance or replace qualified legal review.
- Risk and impact: Users may over-trust automated or agent review if docs do not keep this boundary explicit.
- Current control: Project guidance says sensitive claims require human review and avoids asserting compliance.
- Scoring could help: Yes, only as risk triage.
- Candidate metrics: Regulated-term hits, claim-risk category, protected-class language flags, pricing/availability claim extraction, required-disclaimer presence, and human legal-review status.
- Closure criteria: Commit a compliance-review policy, required escalation paths, and explicit non-goals for automated legal determinations.

## Entry Template

Use this template for new limitations:

```markdown
### LIM-000: Short title

- Priority: P1
- Status: Open
- Owner phase: Phase N / backlog
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
