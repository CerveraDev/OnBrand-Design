# Cross-Platform Compatibility

**Status:** Phase 11 deterministic adapters implemented; live agent invocation unverified
**Updated:** 2026-10-03

## Supported Scope

The Rider has thin Codex, Claude Code, and ordinary CLI/file entrypoints into one canonical Python runtime. All three deterministic entrypoints pass the representative campaign parity gate. This does not prove that two models interpret a new brief identically or that live manual discovery has been observed on both hosts.

Cassia and generated projects install their own reference wrappers but cannot build until calibrated project runtimes are registered. Phase 12 public/private/broker source separation remains deferred.

## Layout And Authority

| Surface | Location | Authority |
|---|---|---|
| Shared core | `tools/rider_campaign_runtime/`, project Markdown/JSON/templates | All rendering, approval, ownership, claim, image, variant, footer, QA, packaging rules |
| Project declaration | `projects/<slug>/adapter.json` | Core/adapter/contract/runtime versions and project binding |
| Codex | `.agents/skills/onbrand-<slug>-{email,image}/` | Thin routing and `agents/openai.yaml` manual policy |
| Claude Code | `.claude/skills/onbrand-<slug>-{email,image}/SKILL.md` | Thin routing and Claude-only manual frontmatter |
| CLI/file workflow | `python3 -m tools.platform_adapters.cli` | Same request and runtime as both wrappers |
| Installer | `tools/platform_adapters/install.py` | Project metadata drives wrappers; refuses conflicting files |
| Evaluation | `tools/platform_adapters/parity.py` | Independent builds, component comparisons, ZIP/asset integrity |

Canonical project SKILL.md frontmatter stays portable. Do not install it directly into Claude Code; use the wrapper carrying the host-specific invocation flag. No adapter copies brand rules, business logic, credentials, hooks, dynamic shell injection, or permission bypasses.

## Installation

Requires Python 3.10+ and its standard library. Keep the core checkout and relevant project pack together; a project folder alone does not include the shared Python runtime. From the core root:

```bash
python3 -m tools.platform_adapters.cli install --project the-rider --platform codex --workspace .
python3 -m tools.platform_adapters.cli install --project the-rider --platform claude --workspace .
```

The repository already contains Rider and Cassia wrappers. Installation is idempotent for identical files and refuses to overwrite different files. For another workspace, pass its path to `--workspace`; links/core-root references are relative. Reinstall after changing the core/workspace relationship. No home-directory settings, API keys, login state, or platform configuration are changed.

New projects receive `adapter.json` with a null runtime. Names include the slug and cannot exceed 64 characters. New runtimes must register their own canonical validator/builder in the shared dispatch table, not borrow Rider calibration.

## Manual Invocation

- Codex: HUMAN invokes `$onbrand-the-rider-email` or the separate image skill. The wrapper's `policy.allow_implicit_invocation: false` disables topic-driven selection.
- Claude Code: HUMAN invokes `/onbrand-the-rider-email` or the separate image skill. The wrapper uses `disable-model-invocation: true`; `user-invocable: false` is deliberately not used.
- CLI: HUMAN supplies `--explicit` and the request record `invocation: {"actor": "HUMAN", "explicit": true}`. Both are mandatory. They attest intent, not authenticated identity or access control.

Ordinary topic matches must not invoke OnBrand skills. Image generation still uses the separately invoked canonical workflow; adapters add no provider or automatic skill handoff. Without shell tools, return the same command for the human. Never hand-assemble around failed QA. Host filesystem/network permissions still apply.

## Request Contract 1.0

See the [schema](../tools/platform_adapters/request.schema.json) and [approved Rider example](../projects/the-rider/skills/onbrand-the-rider-email/examples/cross-platform.request.json).

- Required version fields `contract_version`, `adapter_version`, `core_version` are `1.0`.
- `project`, `runtime`, `runtime_version` must equal the project declaration. Unknown versions/projects/runtimes fail; null-runtime scaffolds cannot build or emit.
- `campaign_spec` identifies the authoritative approved JSON, relative to the request file (absolute paths also work).
- `inputs` optionally names brief, selection, composition, image, and copy JSON files with path/SHA-256. Embedded approved plans remain authoritative when no separate file exists.
- `invocation` is the exact HUMAN/manual record above. Unknown fields fail.

Attached composition/image/copy files must equal the embedded canonical sections. Selection must produce the same composition plan using the existing canonical generator. Brief JSON is checksum-bound context, not a second rule source or automated truth check. All platforms consume the same files; no platform discriminator enters campaign JSON.

```bash
python3 -m tools.platform_adapters.cli emit --platform codex --request projects/the-rider/skills/onbrand-the-rider-email/examples/cross-platform.request.json --output campaign-output/adapter-emission --explicit
python3 -m tools.platform_adapters.cli build --platform cli --request projects/the-rider/skills/onbrand-the-rider-email/examples/cross-platform.request.json --output campaign-output/adapter-build --explicit
```

Use `--platform claude` for Claude dispatch. `emit` checks the envelope, checksums, campaign schema, and attached approvals without downloading/rendering. Full copy/image/composition semantic and package QA gates run during `build`. Emitted JSON retains original source-relative references; build through the original request instead of relocating that JSON alone.

The only campaign override is isolated `campaign.output_dir`. Original approved files are unchanged; unrecognized output roots are preserved. `campaign.runtime.json` and `adapter-provenance.json` sit beside the campaign folder/ZIP. Provenance records versions, platform, manual attestation, input checksums, and approved campaign checksum; it contains no credentials/private paths and stays outside the portable package.

Failures/blocked QA exit nonzero and are not deliverables. Direct canonical use (`python3 -m tools.rider_campaign_runtime.cli <approved-campaign.json>`) remains available; the adapter is not a security boundary around the core.

## Parity Gate

Thirteen critical components compare campaign, build, variants, composition, image workflow, copy allocation, HTML hashes, complete asset manifest, complete metadata, QA, ZIP inventory, integrity, and provenance. Copy comparison retains owners/channels, claims/references, reuse exemptions, counts, similarity findings, and thresholds.

Each component scores `100 * matching platforms / 3` against CLI. Every critical component requires 100 and a pass; the arithmetic mean cannot override a failure. Missing evidence, extra fields, failed QA, duplicate QA IDs, altered assets, stale ZIPs, duplicate/extra archive members, and unrecognized run artifacts fail.

Approval/selection matching and all component comparisons use the shared type-sensitive JSON representation, also used for component hashes and JSON inventory hashes. Boolean, number, null, string, array, and object types are distinct recursively: `true` never equals `1`, nor `false` equals `0`. Object key order is irrelevant; array order, length, and object member presence remain significant.

Only these normalizations are allowed:

1. Verified per-run `campaign.output_dir` becomes `<OUTPUT>`.
2. JSON key order/whitespace use canonical serialization; arrays remain ordered.
3. Top-level QA checks sort by unique name; IDs, messages, outcomes, and nested content remain intact.
4. ZIP timestamps/compression/container bytes are excluded. Directory/member names and uncompressed file bytes must match the package. Cross-platform QA JSON hashes use the same check-order normalization.
5. Verified sidecar platform becomes `<PLATFORM>`; all other provenance fields must match and extra fields fail.
6. JSON has one number type. Finite numbers compare by their parsed numeric value, without rounding tolerance: `1` equals `1.0`, and `0` equals `-0.0`. Integral floats normalize to integers; fractional parsed floats keep their values. Equivalent numbers receive identical semantic hashes. This uses the shared JSON parser's numeric precision, not arbitrary-precision decimal arithmetic. NaN/infinity and non-JSON values are rejected. Source-file checksum/provenance binding still uses original bytes/approved input serialization.

There is no generic path/URL/text/timestamp/claim/score stripping. Use the same approved files and source root; differing local-source paths are not excused.

## Realistic Reproduction

With the approved Phase 10 package present:

```bash
python3 -m tools.platform_adapters.cli parity --request projects/the-rider/skills/onbrand-the-rider-email/examples/cross-platform.request.json --output campaign-output/new-parity-run --cache-package campaign-output/rider-wellness-composition-preview/rider-wellness-composition-preview --explicit
```

Output must be new. Evaluation-only transport verifies prior asset checksums/sizes and supplies actual bytes under the original source URL/name. Unknown remote sources fail instead of downloading. Rendering, validation, QA, source identities, and packaging are unchanged. Without `--cache-package`, the canonical asset reader runs normally.

See [evaluation evidence](evals/phase-11-cross-platform-compatibility.md) and the [machine-readable report](evals/phase-11-parity-report.json). Generated packages stay ignored.

## Official References

Verified/accessed 2026-10-03:

- [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills): required name/description, repository `.agents/skills`, explicit mention, and `agents/openai.yaml` invocation policy. The former developers.openai.com/codex/skills URL redirects here.
- [Anthropic Claude Code skills](https://code.claude.com/docs/en/skills): project `.claude/skills/<name>/SKILL.md`, YAML frontmatter, slash invocation, and `disable-model-invocation: true`.

Installed CLIs: Codex 0.160.0 and Claude Code 2.1.273. Codex already has ChatGPT authentication, but its bounded read-only manual request exited before model execution because the sandbox blocked its app server/state database. Claude reports not logged in; no login or model invocation was attempted. Neither proves live discovery/manual behavior/model parity. [LIM-017](../LIMITATIONS.md#lim-017-live-agent-invocation-and-model-behavior-parity-remain-unverified) tracks this separately.
