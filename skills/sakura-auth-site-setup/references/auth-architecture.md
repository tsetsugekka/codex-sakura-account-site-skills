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

- Store password hashes with PHP `password_hash`.
- Generate verification tokens with cryptographic randomness.
- Store only `hash('sha256', token)`.
- Expire verification links, commonly after 24 hours.
- Regenerate session ID on login and verification success.
- Use `HttpOnly`, `SameSite=Lax`, and `Secure` on HTTPS.

