# Account Lifecycle

## Registration

Recommended sequence:

1. Require the expected method and the site's anonymous-CSRF protection.
2. Validate username, email, password length, and payload limits.
3. Keep registration closed unless private configuration explicitly enables it.
4. Create the user in `unverified`/`pending` state with no privileged page permissions.
5. Generate a cryptographically random verification token.
6. Store only its SHA-256 hash, expiry, issued time, and purpose.
7. Send the one-time URL through the confirmed private sender configuration.
8. Do not auto-login the new account.

If the email already exists, prefer a generic response. When product requirements intentionally provide different guidance for verified and unverified accounts, document the account-enumeration tradeoff and keep rate limits/cooldowns.

## Email Verification

- Use at least 32 random bytes before URL-safe encoding.
- Default expiry may be 24 hours.
- Compare the stored hash with `hash_equals`.
- Clear the hash and expiry before or atomically with the account transition.
- Promote to the configured verified default role, usually `user`, unless an explicit approval/assignment policy says otherwise.
- Record `emailVerifiedAt`.
- Regenerate the session identifier if verification also authenticates the user.
- Reject malformed, expired, reused, revoked, and wrong-purpose tokens with a safe message.

## Resend Verification

- Accept an email or authenticated unverified account according to the UI design.
- Return a generic accepted response whether or not a matching account exists.
- Do nothing for an already verified or disabled account unless the product explicitly says otherwise.
- Enforce a resend cooldown, for example 60 seconds.
- Replace the previous token hash so only the newest link remains valid.
- Do not disclose mail delivery errors that reveal account state.

## Forgot Password

- Return the same public response for existing and nonexistent emails.
- Enforce per-account and per-source cooldown/rate limits.
- Generate a new purpose-bound token and store only its hash.
- Default expiry may be one hour.
- Do not alter the password during the request step.
- Do not place username, email, or token in logs.

## Complete Password Reset

1. Require the expected method and CSRF/origin protection appropriate to the reset page.
2. Validate token format and purpose.
3. Validate expiry and constant-time hash equality.
4. Validate the new password and confirmation.
5. Write the new password hash atomically.
6. Clear the reset token before returning success.
7. Invalidate all existing sessions for the account.
8. Do not auto-login unless that policy is explicitly chosen and reviewed.

## Authenticated Account Changes

For password change:

- require login, CSRF, and current-password reauthentication,
- validate the new password,
- invalidate other sessions and rotate the current session.

For email change:

- require login, CSRF, and current-password reauthentication,
- send a verification link to the new address,
- keep the current verified address active until confirmation,
- prevent duplicate-email assignment,
- invalidate the pending token after use or replacement.

For self-service deletion:

- require login, CSRF, current password, and an explicit irreversible confirmation,
- protect bootstrap/full-access administrators,
- delete or anonymize account-owned private data according to the site's policy,
- invalidate every session.

## Session and CSRF

- Set `HttpOnly`, `SameSite=Lax`, and `Secure` on HTTPS cookies.
- Enable strict session handling when supported.
- Regenerate the session ID after login and permission-sensitive state changes.
- Use a cryptographically random CSRF token stored server-side.
- Send it to the browser only through the session/bootstrap contract.
- Require a custom header or exact form field and compare with `hash_equals`.
- Rotate or clear it with the session lifecycle.

Login, registration, resend, reset request, and reset completion are anonymous-facing mutations. Bootstrap an anonymous session/CSRF token or enforce a documented strict-origin alternative; do not simply exempt every anonymous POST from CSRF controls.

## Mail Composition Boundary

This lifecycle decides the recipient, purpose, expiry, and one-time URL. The companion mailbox skill provides the real sender, complete headers, Japanese templates, server acceptance test, and delivery troubleshooting. Never place authentication tokens in mail logs or status UI.
