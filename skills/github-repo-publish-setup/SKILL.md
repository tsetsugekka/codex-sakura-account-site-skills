---
name: github-repo-publish-setup
description: Prepare a new GitHub repository and ongoing Codex publishing workflow. Use when Codex needs to guide a user through creating a GitHub repo, configuring remotes, committing to the intended branch, pushing without repeated confirmations after scoped approval, and documenting safe publish discipline without leaking secrets.
---

# GitHub Repo Publish Setup

## Goal

Create or connect a GitHub repository and define a disciplined publish workflow for future Codex sessions.

## Workflow

1. Confirm the repository name, visibility, license, and intended default branch.
2. Check whether `gh` is installed and authenticated. If not, guide the user through `gh auth login`.
3. Initialize Git only if the target directory is not already a repository.
4. Add a `.gitignore` before the first commit.
5. Create the GitHub repository with `gh repo create` or ask the user to create it in the browser.
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
- Do not commit `.env`, local secret files, browser cookies, deployment credentials, or generated private data.
- Before staging, run `git status --short`.
- Before committing, run `git branch --show-current`.
- If the worktree contains unrelated changes, ask before staging them.

