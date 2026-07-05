# Auth Architecture

Recommended private files:

```text
/home/ACCOUNT/private_auth/users.json
/home/ACCOUNT/private_auth/site_settings.json
/home/ACCOUNT/private_auth/preferences/
```

Recommended API endpoints:

```text
/api/session.php
/api/login.php
/api/logout.php
/api/register.php
/api/verify-email.php
/api/access.php
/api/account.php
/api/supervisor.php
```

User record fields:

```json
{
  "id": "numeric-stable-id",
  "username": "user",
  "email": "user@example.com",
  "emailVerifiedAt": "",
  "emailVerificationTokenHash": "",
  "emailVerificationExpiresAt": "",
  "passwordHash": "password_hash output",
  "role": "user",
  "disabled": true,
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601"
}
```

Rules:

- Keep page permissions in role/group records. Do not store per-user page grants unless the project explicitly requires an exception.
- Store password hashes with PHP `password_hash`.
- Generate verification tokens with cryptographic randomness.
- Store only `hash('sha256', token)`.
- Expire verification links, commonly after 24 hours.
- Regenerate session ID on login and verification success.
- Use `HttpOnly`, `SameSite=Lax`, and `Secure` on HTTPS.
- Use file locks and temporary-file-plus-rename writes when the lightweight store is JSON.
- Make the bootstrap admin fixed full access and prevent deleting or downgrading it through the UI.
- Keep registration closed by default; when opened, create a disabled/pending user or assign a pending group until email verification succeeds.
- After verification, move the user to the normal default group such as `user` unless the project explicitly requires an admin approval step.
- Role names are project configuration, not universal UI copy. A common pattern is `unverified` or `pending` for pre-verification registrations, `user` for normal verified users, and `admin` for fixed full access.

Role catalog pattern:

```json
[
  {"id": "unverified", "name": "未認証", "pages": [], "system": true},
  {"id": "user", "name": "User", "pages": [], "system": true},
  {"id": "staff", "name": "Staff", "pages": [], "system": true},
  {"id": "admin", "name": "管理者", "pages": ["*"], "system": true}
]
```

For pages with levels, store page permission values by page path inside the role record. The `admin` role should resolve to full access or the highest declared page permission.

Do not bake project-specific names, domains, product labels, or UI branding into the reusable account code. Keep them in configuration, copy files, or the consuming project's styles.
