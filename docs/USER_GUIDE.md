# OnBrand Design User Guide

This guide explains how to use an OnBrand Design project skill to plan, review, build, and package an email campaign. The Rider is the first working project implementation. Cassia and future projects require their own calibrated scaffold, assets, footers, and runtime before they can build campaigns.

## What The Skill Produces

An approved build produces a campaign folder and matching ZIP containing:

- One or more HTML email files, according to the selected build mode
- Only the images and PDFs used by those emails
- `asset-manifest.json` with asset identity, checksum, source, and usage
- `campaign-metadata.json` with build, composition, image, and copy decisions
- `qa-report.json` with blocking and passing checks

The package is intended for review and team handoff. In `relative-review` mode, HTML uses packaged relative image paths. A deployment platform that requires public image URLs needs an explicitly configured hosted asset base URL; the runtime does not invent one.

## Requirements

### Ordinary Campaign Use

Required:

- A checkout or download of the complete OnBrand Design repository
- Python 3.10 or newer
- The selected project pack and its shared runtime in the same checkout
- A configured, validated project asset manifest
- Filesystem access to write the generated campaign package
- Network access when approved assets must be downloaded from public URLs
- Codex, Claude Code, or a shell capable of running the Python commands

The current Rider project uses the ignored local fallback at `tools/dropbox-manifest/manifest.json`. A fresh clone does not contain that file, and no stable public Rider manifest URL is configured yet. Until that is completed, a maintainer must supply the validated manifest locally before a new machine can build Rider campaigns.

Not required for ordinary campaign use:

- Dropbox app key, app secret, access token, or refresh token
- GitHub credentials, unless the user will contribute changes
- PyYAML
- TypeSafe Jev or a Jev API key
- Node.js or Playwright
- The Dropbox Python dependencies

### Optional Maintenance Tasks

| Task | Additional requirement |
|---|---|
| Refresh the Dropbox manifest | Authorized Dropbox app, local ignored `.env`, and `tools/dropbox-manifest/requirements.txt` |
| Commit repository changes | Git and authorized GitHub access |
| Run the browser render matrix | Node.js plus the pinned Playwright toolchain |
| Run optional semantic evaluation | Explicit owner approval and local TypeSafe credentials |
| Generate or edit campaign imagery | Explicit invocation of the separate project image skill and an available image-generation provider |

Credentials belong only in their documented local stores. Never place credentials in a skill folder, campaign JSON, generated package, prompt, or committed file. See [Credential Policy](CREDENTIALS.md).

## Install The Explicit-Only Skills

From the repository root, install the project wrappers into the current workspace:

```bash
python3 -m tools.platform_adapters.cli install --project the-rider --platform codex --workspace .
python3 -m tools.platform_adapters.cli install --project the-rider --platform claude --workspace .
```

These commands do not log in, add credentials, or change global settings. They create thin workspace wrappers that point to the canonical project skills and runtime.

The skills never activate from an ordinary topic match:

- Codex: explicitly invoke `$onbrand-the-rider-email`
- Claude Code: explicitly invoke `/onbrand-the-rider-email`
- Generated or edited imagery: separately invoke `$onbrand-the-rider-image` or `/onbrand-the-rider-image`

The CLI requires both `--explicit` and a request record declaring a HUMAN explicit invocation. These controls prevent accidental model invocation; they are not authentication or access control.

## Start A Campaign

You can begin with a complete brief or a broad idea.

Directed example:

```text
$onbrand-the-rider-email

Create a Rider long-form wellness email for prospective buyers. Use the approved
wellness direction, CTA "Schedule a presentation," and build a branded Composition
Preview first. Use existing approved assets unless we approve generated imagery.
```

Concept-development example:

```text
$onbrand-the-rider-email

I want to promote The Rider as the center of a Miami wellness routine. Give me
campaign angles, headline and CTA options, a recommended block sequence, and image
directions before building anything.
```

Useful brief details include:

- Campaign type and goal
- Audience
- Required CTA or desired action
- Required facts, offer details, dates, and legal constraints
- Desired tone
- Existing image or PDF preferences
- Whether generated or edited imagery may be considered
- Desired proof or final output mode

The skill should ask only for information that is actually missing. It must not invent project facts, agent details, approvals, claims, or asset provenance.

## Approval Workflow

1. **Brief and copy:** Review strategy, subject line, preview text, headline, body copy, CTA, and factual claims.
2. **Composition Preview:** Review labeled header, hero, body, static, and pre-footer choices. Approve the exact configuration and block sequence.
3. **Static blocks:** Explicitly include or exclude every optional locked static block.
4. **Images:** Approve selected existing assets. If generation or editing is needed, invoke the separate image skill and approve the final candidate before assembly.
5. **Copy allocation:** Confirm where each approved message appears so repeated or near-duplicate copy can be blocked or deliberately exempted.
6. **Build:** Choose Composition Preview, Smoke Test, or Release Build.
7. **QA and handoff:** Review `qa-report.json`; distribute the folder or ZIP only when blocking QA passes.

Do not bypass a failed build by manually assembling HTML or creating a ZIP outside the runtime.

## Build Modes

| Mode | Purpose | Default output |
|---|---|---|
| Composition Preview | Human creative review and block approval | One representative variant |
| Smoke Test | Technical validation after a focused change | One representative variant unless explicitly expanded |
| Release Build | Final authorized internal package | Branded, outside-broker customizable, and all active in-house agent variants |

The representative variant defaults to branded. A Composition Preview or Smoke Test may instead target the outside-broker customizable version or one named agent without generating the full matrix.

The outside-broker customizable version preserves Rider identity and required project/legal content while exposing broker contact placeholders. It is not the same as removing Rider branding.

## Command-Line Workflow

Most users can let the invoked skill operate these commands. Technical operators can run them directly from the repository root.

Generate review galleries:

```bash
python3 -m tools.rider_campaign_runtime.cli catalog --output path/to/review-folder
```

Create a composition plan from an approved selection:

```bash
python3 -m tools.rider_campaign_runtime.cli plan \
  --selection path/to/composition-selection.json \
  --output path/to/composition-plan.json
```

Build an approved campaign:

```bash
python3 -m tools.rider_campaign_runtime.cli build path/to/campaign.runtime.json
```

The current Phase 16 Rider scaffold is still staged rather than canonical. Reproducing its latest proof requires the complete staged sidecar trio:

```bash
python3 -m tools.rider_campaign_runtime.cli build path/to/campaign.runtime.json \
  --scaffold projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.phase16-intake.html \
  --slot-map projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.phase16-slot-map.json \
  --metadata projects/the-rider/skills/onbrand-the-rider-email/templates/scaffold/rider-scaffolding.phase16-block-metadata.json
```

After owner approval and canonical promotion, those three flags will no longer be needed for ordinary Rider builds.

For the versioned cross-platform request workflow, see [Cross-Platform Compatibility](COMPATIBILITY.md).

## Current Boundaries

- Only The Rider has an implemented campaign runtime. Other project folders are scaffolds until calibrated.
- The latest Phase 16 Rider design is a staged review candidate, not yet the canonical default.
- The public Rider manifest URL is not configured, so fresh-clone asset bootstrap is incomplete.
- Browser QA does not certify Gmail, Outlook, Apple Mail, an ESP, accessibility, or legal compliance.
- Human approval remains required for visual fidelity, factual claims, likeness use, brand judgment, legal text, and final distribution.
- Generated-image provenance and checksums do not automatically prove source-environment similarity.
- Broker-only capability restriction is not implemented. The current public source contains internal variant logic and must not be presented as a sanitized broker-restricted distribution.
- A relative review package is not automatically a production-hosted send package.

Track open work in [Project Status](../STATUS.md), [Roadmap](../ROADMAP.md), and the [Limitations Register](../LIMITATIONS.md).

