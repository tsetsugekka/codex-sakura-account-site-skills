# Local Secret Contract

Use a project-local secret file named `LOCAL_DEPLOY_SECRETS.md`. It must be ignored by Git.

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

Validation:

- Confirm the file exists locally.
- Confirm `.gitignore` contains `LOCAL_DEPLOY_SECRETS.md`.
- Confirm `git status --short` does not list the real secret file.

