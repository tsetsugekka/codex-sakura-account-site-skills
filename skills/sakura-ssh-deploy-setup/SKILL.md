---
name: sakura-ssh-deploy-setup
description: Prepare safe SSH and SFTP deployment for Sakura Server projects. Use when Codex needs to guide a user through creating a local-only Sakura login secret file, generating reusable SSH/SFTP helper scripts, updating .gitignore, and setting up approved command prefixes so future Codex deploys can upload without repeated confirmation.
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
   - `scripts/ssh-with-local-secret.expect`
5. Ask the user to fill the local secret file manually or through a secure local workflow.
6. Run a harmless `ssh` check such as `pwd` or `ls -la`.
7. Run a harmless `sftp` check such as `ls`.
8. If the environment supports persistent command approvals, ask the user once for narrowly scoped prefixes:
   - `expect scripts/sftp-with-local-secret.expect`
   - `expect scripts/ssh-with-local-secret.expect`
   - optionally plain `ssh` and `sftp`

Do not claim that confirmations can be bypassed. Phrase it as: after the user explicitly approves narrow command prefixes, Codex can repeat matching deploy commands without asking again in that environment.

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
- Prefer deploy manifests that list exact local and remote paths.
- Do not upload or overwrite production data unless the user explicitly asks for that exact data action.

