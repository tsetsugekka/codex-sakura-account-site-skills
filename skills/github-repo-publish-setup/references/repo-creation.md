# GitHub Repo Creation

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

