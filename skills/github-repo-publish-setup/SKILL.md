---
name: github-repo-publish-setup
description: Prepare a new GitHub repository and ongoing Codex publishing workflow. Use when Codex needs to create a GitHub repo for the user with gh or browser automation, have the user handle only GitHub verification codes or authorization prompts, configure remotes, commit to the intended branch, push without repeated confirmations after scoped approval, and document safe publish discipline without leaking secrets.
---

# GitHub Repo Publish Setup

## Goal

Create or connect a GitHub repository and define a disciplined publish workflow for future Codex sessions.

Codex should create the repository when the user asks. The user should only need to complete GitHub authentication steps that cannot be delegated, such as entering a browser/device verification code or approving an authorization prompt.

## Workflow

1. Confirm the repository name, visibility, license, and intended default branch.
2. Check whether `gh` is installed and authenticated. If not, start `gh auth login` or the browser auth flow; have the user enter only the verification code or approve the GitHub prompt.
3. Initialize Git only if the target directory is not already a repository.
4. Add a `.gitignore` before the first commit.
5. Create the GitHub repository with `gh repo create`, or use browser automation when `gh` is unavailable. Do not ask the user to create the repo manually unless both automation paths are unavailable or denied.
6. Set `origin` and default branch.
7. Commit only intended files.
8. Push to the intended target branch.
9. Add an `AGENTS.md` or project maintenance section that requires:
   - checking current branch before commit,
   - avoiding accidental temp branches,
   - never committing secrets,
   - using direct `main` publish only when requested.

## No-Repeated-Confirmation Setup

Codex cannot bypass approvals by itself. After the user approves narrow command prefixes such as `git add`, `git commit`, `git push`, `git remote`, and optionally `gh repo`, future matching commands can proceed without repeated prompts in that environment.

Keep the allowed prefixes narrow. Do not ask for broad arbitrary script prefixes.

## Helper Script

Use `scripts/write_publish_policy.py` to add a safe publish policy block to a target repository's `AGENTS.md`.

```bash
python3 /path/to/skills/github-repo-publish-setup/scripts/write_publish_policy.py --project-root .
```

## References

- Read `references/repo-creation.md` for GitHub creation choices.
- Read `references/publish-discipline.md` before committing or pushing.

## Safety Rules

- Do not print GitHub tokens.
- Do not make the user create the GitHub repository manually when `gh` or browser automation is available.
- Do not commit `.env`, local secret files, browser cookies, deployment credentials, or generated private data.
- Before staging, run `git status --short`.
- Before committing, run `git branch --show-current`.
- If the worktree contains unrelated changes, ask before staging them.
