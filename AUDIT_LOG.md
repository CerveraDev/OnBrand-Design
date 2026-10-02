# Audit Log

This append-only record captures decisions, implementation events, validations, and material changes. Correct earlier entries with a new entry rather than rewriting history.

| ID | Date | Type | Record | Evidence or impact |
|---|---|---|---|---|
| AUD-001 | 2026-09-27 | Scope | Limited the system to Rider Residences rather than generic real estate. | A different property requires a separate property-specific skill. |
| AUD-002 | 2026-09-27 | Architecture | Selected one main email skill and one isolated image-generation skill. | Image generation has separate constraints and approval behavior. |
| AUD-003 | 2026-09-27 | Workflow | Added directed-build and concept-development modes. | Users may provide a complete brief or request strategic options. |
| AUD-004 | 2026-09-27 | Modules | Made hero and footer required modules. | Hero requires logo, headline, and image; subheading remains optional. |
| AUD-005 | 2026-09-27 | Variants | Defined branded, broker-neutral, and in-house-agent output variants. | Broker-neutral removes sales attribution, not Rider identity. |
| AUD-006 | 2026-09-27 | Compatibility | Chose Beefree-generated HTML as the canonical compatibility reference. | Exact rules remain provisional until the source HTML is supplied. |
| AUD-007 | 2026-09-27 | Invocation | Disabled implicit invocation for both skills. | Codex uses `$skill-name`; Claude Code uses `/skill-name`. |
| AUD-008 | 2026-09-27 | Delivery | Required a campaign folder and ZIP containing HTML variants and every used asset. | Each campaign also receives `asset-manifest.json`. |
| AUD-009 | 2026-09-29 | Asset data | Adopted a Dropbox master `manifest.json` with array-valued `category` and `approved_for`. | The master manifest is distinct from campaign delivery manifests. |
| AUD-010 | 2026-09-29 | Tooling | Updated `build_manifest.py` to synchronize additions/deletions while preserving manual metadata. | Matching uses Dropbox ID, path, stable shared-link identity, then unambiguous filename. |
| AUD-011 | 2026-09-29 | Security | Added local `.env` support and excluded credentials from distributable output. | App name is `rider_ai_context`; the current configuration uses a short-lived access token. |
| AUD-012 | 2026-09-29 | Validation | Completed a live Dropbox synchronization. | 195 assets; 191 curated records preserved; four genuine additions; no genuine removals. |
| AUD-013 | 2026-09-29 | Defect correction | Corrected first-run rename matching for three `ph-suite` to `rh-ph-suite` files. | Stable shared-link tokens now ignore mutable filename portions. |
| AUD-014 | 2026-09-30 | Governance | Created a GitHub-ready project structure with PRD, phased specs, status, roadmap, audit, changelog, and versioning. | Established version 0.1.0 and phase-based release gates. |
| AUD-015 | 2026-09-30 | Branding | Adopted OnBrand Design as the framework brand. | Public product identity is separate from technical skill IDs. |
| AUD-016 | 2026-09-30 | Attribution | Recorded Cervera Real Estate, Inc. as owner and Felix Mendoza as author. | Added authorship, notice, and citation metadata. |
| AUD-017 | 2026-09-30 | Scope evolution | Expanded the repository from a Rider-only package to a reusable multi-project framework. | Each runtime skill remains project-specific, preserving the original isolation requirement. |
| AUD-018 | 2026-09-30 | Naming | Adopted `onbrand-<project-slug>-email` and `onbrand-<project-slug>-image`. | Multiple project bundles can be installed without invocation collisions. |
| AUD-019 | 2026-09-30 | Portfolio | Registered The Rider and scaffolded Cassia. | Cassia contains provisional rules pending project-specific calibration. |
| AUD-020 | 2026-09-30 | Automation | Added a starter template and `create_project.py`. | Future project folders can be generated and registered without a fixed maximum count. |
| AUD-021 | 2026-09-30 | Licensing | Confirmed intent for public reuse but deferred license selection. | Public release remains blocked until an explicit software license is approved. |
| AUD-022 | 2026-09-30 | Isolation | Defined each `projects/<slug>/` directory as an independently distributable package. | Shared templates are brand-neutral; cross-project names, assets, footers, and campaign assumptions are release failures. |
| AUD-023 | 2026-09-30 | Validation | Generated a temporary third project and validated metadata, unique IDs, explicit invocation, placeholders, links, and cross-project isolation. | The official Python validator could not start because `PyYAML` is unavailable; equivalent YAML parsing passed with Ruby. |
| AUD-024 | 2026-09-30 | Licensing | Cervera Real Estate, Inc. selected Apache License 2.0 for OnBrand Design. | Added the canonical license and required it in every independently distributed project package; project assets remain subject to separate rights. |
| AUD-025 | 2026-09-30 | Editorial quality | Added one contextual copy-quality layer instead of importing two overlapping anti-slop skills. | The email skill runs a silent pass after drafting and supports audit-only review; approved brand language and factual accuracy outrank generic pattern warnings. |
| AUD-026 | 2026-09-30 | Credentials | Adopted SSH or operating-system credential storage for GitHub and a local ignored `.env` for Dropbox manifest refresh. | GitHub tokens do not belong in the project `.env`; distributed skills consume public manifests and never receive maintainer Dropbox credentials. |
| AUD-027 | 2026-09-30 | Dropbox authorization | Added an offline OAuth helper for the `rider_ai_context` app. | The helper verifies access before atomically saving a refresh token and clearing the short-lived access token; no token is printed or committed. |
| AUD-028 | 2026-09-30 | Validation | Verified a live Dropbox synchronization using refresh-token authentication. | The run preserved all 195 records, including 191 curated records, reported zero additions and removals, retained array-valued manual fields, and used no stored access token. |
| AUD-029 | 2026-10-01 | Asset selection | Added a shared local-manifest validator and deterministic asset shortlist selector. | Campaign generation can filter and rank approved candidates without Dropbox credentials; public URL/cache fallback and final asset download packaging remain pending. |
| AUD-030 | 2026-10-02 | Scaffold calibration | Preserved the supplied Rider Beefree export as an immutable source copy and created a corrected canonical runtime scaffold. | Canonical copy fixes `REQUEST MORE INFORMAITON` and `ARTTS`, formalizes 13 marker pairs, excludes marker rows from generated outputs, and preserves head/CSS/Outlook/table structure. |
| AUD-031 | 2026-10-02 | Footer terminology | Replaced the former unbranded/broker-neutral footer language with outside-broker customizable footer language. | Rider branding, developer/legal content, and footer structure remain intact; outside-broker personalization covers headshot, name, title, phone, and email. |
| AUD-032 | 2026-10-02 | Agent data | Adopted one JSON record per verified in-house Rider agent, plus shared schema and deterministic index. | Jake Lecce is the only active factual record from the scaffold; future agents require verified source material. |
| AUD-033 | 2026-10-02 | Asset synchronization | Refreshed the reorganized Rider Dropbox library after adding `20. People` headshots and likeness references. | 205 assets were found; 10 were added, zero removed, and all 195 prior records were preserved. |
| AUD-034 | 2026-10-02 | Agent roster | Registered six user-verified in-house Rider agents and changed headshots from direct URLs to canonical manifest `dropbox_id` references. | Footer resolution requires an image under `/20. People/In-house Agents/` approved for `agent-footer`; supplied shared-link tokens were normalized through unique manifest matches. |
| AUD-035 | 2026-10-02 | Likeness boundary | Restricted Diego Ojeda assets to `image-generation-reference`. | These assets cannot qualify for agent footers or ordinary campaign asset selection and require the separate explicit image-generation workflow. |
| AUD-036 | 2026-10-02 | Agent data correction | Corrected Julian Oliveros's verified phone number. | Julian Oliveros now uses `+1 239 384 0836`; Jake Lecce and all other agent records remain unchanged. |
