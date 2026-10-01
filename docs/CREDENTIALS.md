# Credential Policy

OnBrand Design keeps credentials outside repository files, project packages, campaign deliverables, logs, and model-visible instructions. Track only examples containing empty values.

## Credential Map

| Purpose | Store | Never store |
|---|---|---|
| Local GitHub access | SSH private key in `~/.ssh` or GitHub CLI credential storage | Repository `.env`, source files, prompts, or remote URLs |
| GitHub Actions | Repository or organization Actions secrets; use the automatic `GITHUB_TOKEN` when sufficient | Workflow YAML values or committed shell scripts |
| Dropbox manifest refresh | `tools/dropbox-manifest/.env` on an authorized maintainer's machine | Git, project downloads, campaign packages, or `manifest.json` |
| Distributed skill asset access | Public manifest and approved public asset URLs | Dropbox app secret, refresh token, or maintainer access token |

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
