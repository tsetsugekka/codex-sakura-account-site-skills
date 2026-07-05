---
name: sakura-ssh-deploy-setup
description: Prepare safe SSH and SFTP deployment for Sakura Server projects. Use when Codex needs to guide a user through creating a local-only Sakura login secret file, generating reusable SSH/SFTP helper scripts, whitelist upload manifests, .gitignore rules, and scoped approvals so future Codex deploys can upload without repeated confirmation.
---

# Sakura SSH Deploy Setup

## Goal

Set up a Sakura Server project so Codex can deploy through SSH/SFTP using a local secret file that is never committed.

## Workflow

1. Inspect the repository and confirm the intended deploy target, public web root, and private job/data paths.
2. Create or update a local-only `LOCAL_DEPLOY_SECRETS.md` template. Never fill real secrets into tracked files.
3. Add `LOCAL_DEPLOY_SECRETS.md` to `.gitignore`.
4. Generate helper scripts that read the local secret file:
   - `scripts/sftp-with-local-secret.expect`
   - `scripts/ssh-run-with-local-secret.expect`
5. Create a whitelist SFTP manifest template. The manifest must list exact local-to-remote uploads; do not use recursive whole-repository uploads.
6. Ask the user to fill the local secret file manually or through a secure local workflow.
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
- Put private account data, cron state, logs, and settings outside the public web root.
- Run cleanup only after live verification, and only delete old generated hash `.js`, `.css`, or `.map` assets one file at a time.

## Helper Script

Use `scripts/create_deploy_helpers.py` to scaffold the local secret template, `.gitignore` entry, and helper scripts into the target repository.

Run from the target repository root:

```bash
python3 /path/to/skills/sakura-ssh-deploy-setup/scripts/create_deploy_helpers.py --project-root .
```

## References

- Read `references/local-secret-contract.md` when deciding where secrets live and how helpers parse them.
- Read `references/deploy-runbook.md` when creating a safe upload flow.

## Safety Rules

- Never print passwords, control panel credentials, mailbox passwords, API tokens, or full secret file contents.
- Never write real secrets into `SKILL.md`, README, scripts, examples, deploy manifests, docs, Git commits, or command logs.
- Require deploy manifests that list exact local and remote paths.
- Do not upload or overwrite production data unless the user explicitly asks for that exact data action.
