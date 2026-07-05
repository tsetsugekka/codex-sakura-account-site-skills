# Local Secret Contract

Use a project-local secret file named `LOCAL_DEPLOY_SECRETS.md`. It must be ignored by Git.

Codex should create this file through a secure prompt or equivalent secret-entry UI when possible. The normal user role is to enter Sakura host/user/password into that prompt, not to hand-edit the file.

Supported fields:

```text
host: example.sakura.ne.jp
user: example-user
password: paste-locally-only
```

Rules:

- Keep one key-value pair per line.
- Allow `:`, `=`, or Japanese full-width colon after the key.
- Ignore blank lines and comment lines beginning with `#`.
- Do not store mailbox passwords, GitHub tokens, or unrelated API keys in this file.
- If SSH key authentication is preferred, store key paths outside the repository and document only the path placeholder.
- Set the real local secret file to mode `0600` when the filesystem supports it.

Validation:

- Confirm the file exists locally.
- Confirm `.gitignore` contains `LOCAL_DEPLOY_SECRETS.md`.
- Confirm `git status --short` does not list the real secret file.
- Confirm Codex can run harmless SSH/SFTP checks after the user provides the Sakura credentials.
- Confirm helper names match the project convention:
  - `scripts/sftp-with-local-secret.expect`
  - `scripts/ssh-run-with-local-secret.expect`
  - or, for projects that isolate deploy tooling, `deploy/scripts/sftp-with-local-secret.expect`
  - and `deploy/scripts/ssh-run-with-local-secret.expect`
- Helper scripts should locate `LOCAL_DEPLOY_SECRETS.md` by walking upward from their own directory so nested helper folders still work.
