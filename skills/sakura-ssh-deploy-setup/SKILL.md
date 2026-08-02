---
name: sakura-ssh-deploy-setup
description: Prepare and troubleshoot safe SSH and SFTP deployment for Sakura Server projects. Use when Codex needs to create a local-only Sakura login secret file through secure user input, generate reusable SSH/SFTP helper scripts with a restricted-terminal AskPass fallback, distinguish key-exchange warnings from authentication failures, create whitelist upload manifests and .gitignore rules, or establish scoped approvals for repeatable deploys.
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
7. Run a harmless `ssh` check such as `pwd` or `ls -la`. Use the normal interactive prompt first. If the execution environment cannot expose that prompt and no password was submitted, retry once with the generated local AskPass fallback.
8. Run a harmless `sftp` check such as `ls`, using the same normal-first and fallback-only rule.
9. If the environment supports persistent command approvals, ask the user once for narrowly scoped prefixes:
   - `expect scripts/sftp-with-local-secret.expect`
   - `expect scripts/ssh-run-with-local-secret.expect`
   - optionally plain `ssh` and `sftp`

Do not claim that confirmations can be bypassed. Phrase it as: after the user explicitly approves narrow command prefixes, Codex can repeat matching deploy commands without asking again in that environment.

## Diagnose Before Changing Compatibility Settings

Identify the stage that actually failed before editing SSH options:

1. DNS/TCP connection
2. key exchange and server host-key verification
3. user authentication
4. remote command execution
5. SFTP file transfer

An OpenSSH warning that the connection is not using a post-quantum key-exchange algorithm is informational. If a password prompt or `Authentications that can continue` appears afterward, transport and key exchange already succeeded. Do not add legacy `HostKeyAlgorithms +ssh-rsa` or `PubkeyAcceptedAlgorithms +ssh-rsa` merely because of the post-quantum warning.

Use an explicit `user@host`; `ssh host` otherwise defaults to the local operating-system username. Treat these results separately:

- `Permission denied (publickey,password)` after a submitted password is an authentication failure.
- `no matching key exchange method`, `no matching host key type`, or a signature-algorithm error is a negotiation mismatch; use a host-scoped, temporary compatibility override only when the exact diagnostic requires it.
- A password that succeeds in the Sakura control panel is not, by itself, proof that the SSH username and SSH authentication path are correct.
- If manual SSH works but an Expect helper receives no password prompt, do not conclude that the stored password changed. Use the fallback rules below.

Read `references/ssh-auth-troubleshooting.md` before changing algorithms, host-key behavior, or password automation.

## AskPass Is a Fallback, Not the Default

Prefer SSH key authentication when the project and host are ready for it. For an authorized password-based workflow, keep the ordinary interactive SSH/SFTP prompt as the first attempt.

The generated helper may retry with `SSH_ASKPASS_REQUIRE=force` only when all of these are true:

- the first connection did not expose a usable password prompt;
- no password was submitted on that connection;
- authentication then failed;
- the local AskPass helper is executable and reads the already ignored local secret file.

If a password was submitted and rejected, stop after that attempt. Do not automatically submit it again. Limit each connection to `NumberOfPasswordPrompts=1` to reduce account-lockout risk.

The AskPass helper must not embed the password, place it in a command argument or environment-variable value, print it to logs, or enter Git. A dummy `DISPLAY` may be set only because OpenSSH requires it when forcing AskPass. Keep normal host-key verification enabled. Never solve this problem with `StrictHostKeyChecking=no`.

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
- Read `references/ssh-auth-troubleshooting.md` when SSH/SFTP fails, emits a post-quantum warning, or behaves differently between an interactive terminal and Codex/CI.

## Safety Rules

- Never print passwords, control panel credentials, mailbox passwords, API tokens, or full secret file contents.
- Never write real secrets into `SKILL.md`, README, scripts, examples, deploy manifests, docs, Git commits, or command logs.
- Do not ask the user to manually edit `LOCAL_DEPLOY_SECRETS.md` when a secure prompt or equivalent secret-entry UI is available.
- Require deploy manifests that list exact local and remote paths.
- Do not upload or overwrite production data unless the user explicitly asks for that exact data action.
- Do not treat GitHub setup as complete from this skill alone; use the separate `github-repo-publish-setup` companion for repo creation and publish discipline.
