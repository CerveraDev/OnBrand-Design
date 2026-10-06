# Credential Policy

OnBrand Design keeps credentials outside repository files, project packages, campaign deliverables, logs, and model-visible instructions. Track only examples containing empty values.

## Credential Map

| Purpose | Store | Never store |
|---|---|---|
| Local GitHub access | SSH private key in `~/.ssh` or GitHub CLI credential storage | Repository `.env`, source files, prompts, or remote URLs |
| GitHub Actions | Repository or organization Actions secrets; use the automatic `GITHUB_TOKEN` when sufficient | Workflow YAML values or committed shell scripts |
| Dropbox manifest refresh | `tools/dropbox-manifest/.env` on an authorized maintainer's machine | Git, project downloads, campaign packages, or `manifest.json` |
| Distributed skill asset access | Public manifest and approved public asset URLs | Dropbox app secret, refresh token, or maintainer access token |
| Optional TypeSafe Jev calibration | `tools/semantic_eval/.env` on an owner-approved evaluation machine | Git, project packages, campaign output, provider receipts, or skill instructions |
| Native Microsoft 365 email testing | `tools/graph_mail/.env` with a delegated refresh token | Git, campaign packages, MIME files, receipts, prompts, or app client secrets |

## GitHub Authentication

SSH is the recommended local method for routine commits because it avoids storing a GitHub token in the project and does not require repeated browser login.

1. Use a personal GitHub account with write access to the `CerveraDev` repository or organization.
2. Register only the public key with GitHub. Keep the private key in `~/.ssh`.
3. Load a passphrase-protected key into macOS Keychain:

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

4. Copy the public key and add it under GitHub **Settings > SSH and GPG keys**:

```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

5. Test access and switch this repository to its SSH remote:

```bash
ssh -T git@github.com
git remote set-url origin git@github.com:CerveraDev/OnBrand-Design.git
git remote -v
```

If an organization requires SAML SSO, authorize the SSH key for that organization in GitHub. Do not paste a private key, personal access token, or GitHub CLI token into chat, an issue, or a repository file.

GitHub CLI over HTTPS remains an acceptable alternative. It should store credentials through the operating system credential manager. Do not place `GH_TOKEN` or a personal access token in the project `.env` for ordinary local Git use.

## Dropbox Authentication

The manifest-maintenance script loads this ignored local file by default:

```text
tools/dropbox-manifest/.env
```

For repeated use, configure the Dropbox app key, app secret, and refresh token. Leave the short-lived access-token field empty when refresh-token authentication is active:

```dotenv
DROPBOX_APP_NAME=rider_ai_context
DROPBOX_APP_KEY=
DROPBOX_APP_SECRET=
DROPBOX_REFRESH_TOKEN=
DROPBOX_ACCESS_TOKEN=
DROPBOX_ROOT=
DROPBOX_MANIFEST_PATH=manifest.json
```

Create or rotate the refresh token with the repository helper:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/dropbox-manifest/requirements.txt
.venv/bin/python tools/dropbox-manifest/authorize_dropbox.py
```

The helper requests offline access, opens the Dropbox approval page, accepts the one-time authorization code with hidden input, verifies account access, and writes the refresh token directly to the selected `.env`. It does not print the refresh token. After successful verification, it clears `DROPBOX_ACCESS_TOKEN` so the manifest script uses refresh authentication.

Before authorization, confirm the Dropbox app has only the scopes required by the manifest workflow: `files.metadata.read`, `files.content.read`, `sharing.read`, and `sharing.write`. Permission changes require a new authorization grant.

Only authorized maintainers need these values. Normal campaign generation should consume a validated public manifest and approved public asset URLs without Dropbox credentials. A project package must continue from a validated local cache or request maintainer action if its public manifest is unavailable; it must not request or expose the maintainer's refresh token.

## Team And Automation

- Store shared operational secrets in an approved organization password manager, not a shared `.env` attachment.
- Give each person or automation identity the minimum permissions required.
- Prefer organization-level GitHub secrets only when several repositories genuinely need the same credential.
- Use environment-specific or repository-specific secrets for narrower access.
- Never echo secrets in commands, logs, error reports, manifests, or generated email packages.

## Rotation And Exposure

Rotate a credential when a maintainer leaves, permissions change, a token expires, or exposure is suspected. If a secret enters Git history, revoke it immediately before attempting history cleanup. Deleting the visible file or commit does not make the credential safe again.

Review ignored files before each public release and verify that only `.env.example` files with empty values are tracked.

## TypeSafe Jev Calibration

Jev remains an optional evaluation provider and is disabled by default. Copy the tracked empty example only after owner approval for a live calibration:

```text
tools/semantic_eval/.env
```

```dotenv
ONBRAND_JEV_ENABLED=false
TYPESAFE_API_KEY=
```

A live request requires all three conditions:

1. Set `ONBRAND_JEV_ENABLED=true` locally.
2. Supply `TYPESAFE_API_KEY` locally.
3. Pass the explicit `--execute-live` CLI flag.

The adapter sends only the state fields present in the committed calibration batch. It must not send expected labels, reviewer records, adjudication evidence, agent contact data, credentials, or complete campaign packages. Receipts store hashes, typed answers, model ID, usage, and failures without storing the API key.

Do not enable Jev for production campaign builds. Phase 13 calibration has no production effect, does not replace deterministic QA, and requires a separate owner-approved data-handling decision before any live call.

## Microsoft Graph MIME Testing

Native email tests use a dedicated Microsoft Entra application registration configured as a public client. Do not create or store a client secret. The application requests delegated `Mail.Send` plus `offline_access`; it cannot send until a human signs in and grants or receives administrator approval for that scope.

Copy `tools/graph_mail/.env.example` to the ignored `tools/graph_mail/.env`, then set:

```dotenv
ONBRAND_GRAPH_TENANT_ID=
ONBRAND_GRAPH_CLIENT_ID=
ONBRAND_GRAPH_REFRESH_TOKEN=
ONBRAND_GRAPH_SENDER=fmendoza@cervera.com
```

In Microsoft Entra:

1. Register a single-tenant application for OnBrand native email testing.
2. Under Authentication, enable **Allow public client flows**.
3. Add the delegated Microsoft Graph permission `Mail.Send`; grant administrator consent only if Cervera policy requires and authorizes it.
4. Put the Directory (tenant) ID and Application (client) ID in the local `.env`.
5. Run `python3 -m tools.graph_mail.authorize` and complete the displayed device-code sign-in as the authorized sender.

The authorization helper stores the refresh token atomically with mode `0600` and never prints it. The sender refreshes access tokens locally, rotates the stored refresh token when Microsoft returns one, and submits base64 MIME to Microsoft Graph v1.0 `/me/sendMail`. It refuses mismatched `From` addresses and CID-backed backgrounds. Live delivery requires both `--execute-live` and `--confirm-send`; omission of either performs no send.

Validate a candidate without network delivery:

```bash
python3 -m tools.graph_mail.send_mime --message path/to/native-test.eml
```

After reviewing the validation receipt, an authorized maintainer may explicitly send it:

```bash
python3 -m tools.graph_mail.send_mime \
  --message path/to/native-test.eml \
  --execute-live \
  --confirm-send
```

Microsoft Graph returns `202 Accepted` when it accepts the message for processing and saves it in Sent Items. That status is not proof of final delivery or client rendering; record the receiving-client evidence separately.
