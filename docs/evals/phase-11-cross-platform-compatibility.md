# Phase 11 Compatibility Evidence

**Date:** 2026-10-03
**Scope:** deterministic adapter/runtime parity, not independent model interpretation
**Input baseline:** main at `2cc607df3c6467bee97dd9d16264e7373611d5ff`

## Method

The [shared request](../../projects/the-rider/skills/onbrand-the-rider-email/examples/cross-platform.request.json) references the unchanged Phase 10 wellness Composition Preview fixture, approved selection, and approved composition plan. All three adapter calls consume those same files and embedded image/copy approvals. Only the isolated output root differs.

Each independently executes the canonical builder, copy/claim/reuse/similarity validation, image provenance, localization, rendering, metadata, QA, and ZIP creation. Evaluation-only transport supplies nine actual approved image payloads from the prior Phase 10 package after checksum/size verification, retaining original source URL/name. Uncached remote sources fail. No rendered output or QA result is copied between runs.

Ignored local artifacts: `campaign-output/phase-11-parity-final/{cli,codex,claude}/`. The prior Phase 10 package remains unchanged.

## Result

- All 13 critical components scored 100; aggregate 100.0; blocking gate passed.
- Each platform rendered the branded variant with 23 approved copy units.
- Each passed 86 runtime QA checks, including 26 allocation checks.
- Each package has 9 real image assets and 13 files (16 ZIP members including 3 directories).
- HTML SHA-256: `fcd0bed5e6ea6c5c2ca46ef76a130ecf0e3fee8c29f80cd8ecd9fcd4b867ad32`.
- ZIP integrity verifies all uncompressed file bytes and directory inventory; duplicate/extra members fail.
- Adapter provenance remains outside the campaign folder and ZIP.

The [complete report](phase-11-parity-report.json) records per-component hashes and run counts. [Compatibility](../COMPATIBILITY.md) defines the only permitted normalizations and reproduction command.

## Static And Regression Coverage

Tests cover contract/version/project rejection, exact HUMAN/manual booleans, unchanged emission, checksum/approval/selection drift, unrecognized-output preservation, single shared runtime binding, portable manual-only wrappers, installer collisions, generator scaffolds, all component mismatches, copy owners/claims/exemptions/scores, high-aggregate blocking, missing evidence, failed/duplicate QA, tampered assets, stale ZIPs, extra ZIP directories, provenance drift, and cache failure.

Full discovery after the audit correction: 124 tests passing, including 45 Phase 11 tests. The initial implementation passed 109 tests; the correction adds 15 focused regressions. The Phase 7-10 runtime is unchanged. Final verification also parses JSON/YAML, validates local Markdown links/manual policies, reviews secret patterns, audits package/ZIP bytes, and checks whitespace.

Correction checks parsed 35 JSON files (including 4 schema documents and 5 resolved internal schema references), 24 YAML/frontmatter documents with manual policy checks, and 222 local Markdown links. No high-confidence secret patterns or whitespace errors were found. Package snapshots reproduce the committed component hashes. The prior Phase 10 ZIP retains SHA-256 `3f6ec61261a361e26ed90a964a6200a42611aaa4fbfa099d931e73ea2481620b`.

## Completion Audit Correction

A read-only audit of `175a28468ca9d9808172910fcb64923459c296c5` found two P2 gaps: Python object equality allowed a campaign `true -> 1` change to report aggregate 100/pass despite differing hashes, and a checksum-consistent composition attachment with `includes_header: 1` matched approved boolean `true`.

The shared [JSON-semantic helper](../../tools/platform_adapters/json_semantics.py) now preserves type distinctions recursively, compares finite numbers by parsed value, rejects non-JSON/non-finite values, and gives equivalent numbers identical hashes. Parity comparisons, JSON inventory hashes, composition/image/copy attachments, selection plans, and asset/cache size matching use that representation. Remaining direct comparisons were reviewed: version/identity/digest strings, string inventories, and exact boolean guards do not have the coercion defect. Canonical campaign rules and input byte/checksum binding are unchanged.

New regressions cover the original campaign and composition reproductions, recursive object/array/scalar changes across all 13 components, adjacent boolean/number/null/string values, array/member significance, reordered objects, numeric equivalence/precision/no-tolerance cases, non-finite rejection, copy occurrence caps, selection matching, and one-byte boolean cache sizes.

The campaign reproduction now reports failed campaign/variant components at 66.67 each, aggregate 94.87, and a blocked gate. The manipulated composition attachment is rejected for every platform even with its checksum updated. Equivalent `1/1.0` and `0/-0.0` cases pass with matching semantic hashes instead of contradictory hashes.

The corrected realistic pilot independently rebuilt all three outputs at `campaign-output/phase-11-parity-strict-json/{cli,codex,claude}/` using the same approved request and verified real asset cache. All 13 components pass at 100, with the same 86 QA checks, 23 units, 9 assets, branded HTML hash, and 13 files/16 ZIP members. The committed report now records this corrected run and explicit numeric normalization. Original pilot artifacts remain untouched.

Formal Draft 2020-12 validator tooling was unavailable in the installed/bundled Python and Node environments; no dependency was installed. JSON/schema documents are parsed, internal references are checked, and canonical/custom schema validators and contract rejection tests run. That is not a claim of independent standards-level schema validation. Accepted LIM-017 live invocation gaps remain unchanged; no authentication or app-server workaround was retried.

## Live CLI Evidence

| Check | Observation | Meaning |
|---|---|---|
| Codex version | 0.160.0 | Executable available |
| Codex login status | Existing ChatGPT login | No credentials emitted or changed |
| Codex explicit skill request | Bounded 90-second read-only `codex exec --ephemeral --ignore-user-config --sandbox read-only --json`; exit 1 immediately | Local database/app-server permission failure before model execution; live invocation unverified |
| Claude version | 2.1.273 | Executable available |
| Claude auth status | Not logged in | No login/installation attempted; no live model invocation |

The Codex prompt explicitly named `$onbrand-the-rider-email`, allowed only wrapper/canonical/request reading, and forbade build/download/edit/login/install/other-skill invocation. It failed before those actions. Authentication directories were not copied or made writable to bypass the sandbox.

The report's `claude` label means shared Claude adapter dispatch, not a Claude model run. No independent model-behavior equivalence or observed live automatic-invocation prevention is claimed. LIM-010 is mitigated; LIM-017 records the live evidence gap.

## Acceptance Reconciliation

COMPAT-001 through COMPAT-016 and COMPAT-018 have implementation/tests/report evidence. COMPAT-017 is met by precise CLI/authentication/failure observations and the unverified-live limitation, not a substituted success claim. Live manual invocation and independent new-brief interpretation remain follow-up gates under LIM-017.
