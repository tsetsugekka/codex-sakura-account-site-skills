---
name: sakura-ssh-deploy-setup
description: Prepare safe SSH and SFTP deployment for Sakura Server projects. Use when Codex needs to create a local-only Sakura login secret file through secure user input, generate reusable SSH/SFTP helper scripts, whitelist upload manifests, .gitignore rules, and scoped approvals so future Codex deploys can upload without repeated confirmation.
---

# Sakura SSH Deploy Setup

## Goal

Set up a Sakura Server project so Codex can deploy through SSH/SFTP using a local secret file that is never committed.

Codex should do the setup work. The user should only need to provide Sakura host/user/password through a secure prompt or equivalent secret-entry UI.

GitHub repository creation and commit/push discipline are intentionally outside this skill. If the user also wants Codex to create a GitHub repository, connect `origin`, make the initial commit, or set future publish rules, use/install the companion skill `github-repo-publish-setup` before committing or pushing.

## Workflow

1. Inspect the repository and confirm the intended deploy target, public web root, and private job/data paths.
2. Create or update a local-only `LOCAL_DEPLOY_SECRETS.md` from secure user input when credentials are needed. Never put real secrets in tracked files or chat output.
3. Add `LOCAL_DEPLOY_SECRETS.md` to `.gitignore`.
4. Generate helper scripts that read the local secret file. Common layouts are:
   - `scripts/sftp-with-local-secret.expect`
   - `scripts/ssh-run-with-local-secret.expect`
   - or a scoped deploy folder such as `deploy/scripts/sftp-with-local-secret.expect`
   - and `deploy/scripts/ssh-run-with-local-secret.expect`
5. Create a whitelist SFTP manifest template. The manifest must list exact local-to-remote uploads; do not use recursive whole-repository uploads.
6. Use a secure prompt/popup or the helper script's `--write-local-secret` mode so the user only enters Sakura host/user/password; Codex writes the ignored local secret file.
7. Run a harmless `ssh` check such as `pwd` or `ls -la`.
8. Run a harmless `sftp` check such as `ls`.
9. If the environment supports persistent command approvals, ask the user once for narrowly scoped prefixes:
   - `expect scripts/sftp-with-local-secret.expect`
   - `expect scripts/ssh-run-with-local-secret.expect`
   - optionally plain `ssh` and `sftp`

Do not claim that confirmations can be bypassed. Phrase it as: after the user explicitly approves narrow command prefixes, Codex can repeat matching deploy commands without asking again in that environment.

## Deploy Discipline

- Use whitelist manifests for SFTP deploys.
- Do not upload the full repository, full `dist`, `.env`, databases, user data, cache directories, upload directories, or `node_modules`.
- For static frontend builds, upload new hashed assets before the live `index.html`.
- For PHP/account-site deploys without hashed frontend assets, old asset cleanup may be not applicable; do not force cleanup against non-hash shared assets such as `app.css`.
- Put private account data, cron state, logs, and settings outside the public web root.
- Run cleanup only after live verification, and only delete old generated hash `.js`, `.css`, or `.map` assets one file at a time. Final dry-run must report `delete=0`.

## Helper Script

Use `scripts/create_deploy_helpers.py` to scaffold the local secret template, `.gitignore` entry, helper scripts, and optionally the ignored local secret file into the target repository.

Run from the target repository root:

```bash
python3 /path/to/skills/sakura-ssh-deploy-setup/scripts/create_deploy_helpers.py --project-root .
```

To create the ignored local secret file through secure prompts:

```bash
python3 /path/to/skills/sakura-ssh-deploy-setup/scripts/create_deploy_helpers.py \
  --project-root . \
  --write-local-secret
```

For projects that keep deploy helpers under a scoped deploy folder, use:

```bash
python3 /path/to/skills/sakura-ssh-deploy-setup/scripts/create_deploy_helpers.py \
  --project-root . \
  --helper-dir deploy/scripts \
  --deploy-dir deploy/_deploy
```

## References

- Read `references/local-secret-contract.md` when deciding where secrets live and how helpers parse them.
- Read `references/deploy-runbook.md` when creating a safe upload flow.

## Safety Rules

- Never print passwords, control panel credentials, mailbox passwords, API tokens, or full secret file contents.
- Never write real secrets into `SKILL.md`, README, scripts, examples, deploy manifests, docs, Git commits, or command logs.
- Do not ask the user to manually edit `LOCAL_DEPLOY_SECRETS.md` when a secure prompt or equivalent secret-entry UI is available.
- Require deploy manifests that list exact local and remote paths.
- Do not upload or overwrite production data unless the user explicitly asks for that exact data action.
- Do not treat GitHub setup as complete from this skill alone; use the separate `github-repo-publish-setup` companion for repo creation and publish discipline.
