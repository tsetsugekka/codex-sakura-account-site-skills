# GitHub Repo Creation

Codex should create the repository. The user should only handle GitHub authentication actions that cannot be delegated, such as entering a device/browser code or approving an OAuth prompt.

Recommended commands:

```bash
git init
git branch -M main
gh repo create OWNER/REPO --public --source . --remote origin --push
```

For private repositories, use `--private`.

For an existing repository:

```bash
git remote add origin git@github.com:OWNER/REPO.git
git push -u origin main
```

Before creation:

- Confirm visibility.
- Confirm repository name.
- Confirm license.
- Confirm whether generated deploy files should be committed.
- Confirm whether the repo may contain production artifacts.

If `gh` is not authenticated, run `gh auth login` and guide the user through the displayed verification code flow. If `gh` is unavailable but browser automation is authorized, create the repository in GitHub's web UI. Only fall back to asking the user to create the repository manually after those paths are unavailable or denied.
