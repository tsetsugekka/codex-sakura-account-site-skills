---
name: sakura-auth-site-setup
description: Build or upgrade a production account and authorization system for a Sakura-hosted website. Use when Codex needs registration with email verification, resend-verification and forgot-password flows, one-time password reset, login/session/CSRF security, email or password changes, user groups and role assignment, role-level page permissions, protected page and API contracts, an admin/supervisor UI, private storage outside the web root, and integration with sakura-mailbox-setup for the real Sakura sender and delivery infrastructure.
---

# Sakura Auth Site Setup

## Goal

Build a production account system that owns identity, account lifecycle, user groups, page permissions, session security, and server-side API authorization while preserving the existing site's visual style.

Use `sakura-mailbox-setup` for Sakura mailbox creation/confirmation, DNS, sender configuration, PHP/sendmail integration, and delivery testing. This skill owns why and when verification/reset messages are sent, token lifecycle, account state transitions, and authorization. Mailbox readiness alone does not mean registration authentication is complete.

Use `sakura-api-secrets-deploy` when protected pages call paid or credentialed external APIs. Use `github-repo-publish-setup` for GitHub creation and publishing.

## Responsibility Boundary

`sakura-auth-site-setup` owns:

- registration, login, logout, and session bootstrap,
- email verification and safe resend behavior,
- forgot-password request and single-use password reset,
- authenticated email/password changes and optional account deletion,
- user groups, role assignment, and role-level page permissions,
- protected page entrypoints and business API enforcement,
- CSRF, session invalidation, rate limits, and account-enumeration controls,
- admin account/role/permission screens.

`sakura-mailbox-setup` owns:

- creating or confirming the real Sakura sender mailbox,
- MX/SPF/DKIM/DMARC and sender-domain checks,
- private From/display name/envelope-sender configuration,
- complete message headers and server acceptance tests,
- diagnosing bounces and accepted-versus-delivered status.

Do not duplicate Sakura Control Panel mailbox steps here. Invoke the mailbox skill and consume its confirmed private sender configuration.

## Core Requirements

- Keep user records, settings, preferences, tokens, session indexes, locks, and logs outside the public web root.
- Use modern password hashing, preferably Argon2id when available, through `password_hash`/`password_verify`.
- Keep registration disabled by default unless the operator explicitly enables it.
- Do not auto-login a newly submitted registration.
- Require email verification before granting the normal verified group or privileged page access.
- Store verification and reset tokens only as cryptographic hashes with expiry, purpose, and single-use semantics.
- Use generic responses for reset/resend paths when a response could reveal whether an account exists.
- Keep page permissions on roles/user groups, never directly on individual users.
- Let each page define its own ordered permission keys; do not invent one global permission enum.
- Make protected page UI read the server-evaluated page permission. Do not infer capabilities from role names.
- Enforce the same permission inside every page-specific API before reading private data or performing work.
- Require CSRF on all cookie-authenticated mutations, including login/logout, registration, resend, reset completion, profile changes, role changes, and admin actions.
- Treat intentionally anonymous account lifecycle APIs as explicit exceptions, not as a reason to leave business APIs public.
- Fix the bootstrap administrator at full access and prevent UI/API deletion or downgrade.
- Keep infrastructure values such as site name, public base URL, From address/name, envelope sender, OAuth credentials, and API credentials out of admin-editable JSON and forms.

## Workflow

1. Inspect the current stack, routes, session model, existing users, public/protected page catalog, styles, deploy manifests, mailbox state, and all account/business APIs.
2. Write down the boundary between public lifecycle APIs, protected account APIs, protected business APIs, CLI workers, and include-only libraries.
3. Define private storage and configuration. Read `references/auth-architecture.md`.
4. Define the account lifecycle. Read `references/account-lifecycle.md`.
5. Invoke `sakura-mailbox-setup` to create or confirm the sender and private mail configuration before claiming verification/reset mail is production-ready.
6. Implement or upgrade session security:
   - secure cookie attributes,
   - session ID regeneration after authentication/privilege change,
   - CSRF bootstrap and constant-time validation,
   - session invalidation on password reset, password change, account disable, and admin revocation.
7. Implement role/group authorization:
   - `unverified` or `pending`,
   - normal verified `user`,
   - optional operator/staff groups,
   - fixed full-access `admin`,
   - optional documented automatic assignment rules such as approved email domains or campaign codes.
8. Define page permissions with the consuming page. Read `references/page-permissions.md`.
9. Protect the page entrypoint and inject a minimal project-scoped runtime contract containing the current page permission and CSRF token. Never inject hashes, uid internals, secrets, or private paths.
10. Protect every page API server-side. Mutations must validate method, session, page permission, and CSRF before reading the request body, credential, job, upload, or private record.
11. Build the admin/supervisor UI:
   - account list and state,
   - role/group assignment,
   - role-level page permissions,
   - protected bootstrap admin,
   - optional cron failure recipient and safe test-send action,
   - no infrastructure sender/public URL/API key fields.
12. Match the existing site style. Read `references/ui-guidelines.md`.
13. Wrap scheduled jobs only when requested. Read `references/cron-alerts.md`.
14. Deploy through exact-file manifests and verify both anonymous and authorized behavior.

## Required Endpoint Set

Adapt names to the existing routing, but cover these responsibilities:

```text
session / csrf bootstrap
login
logout
register
verify email
resend verification
request password reset
complete password reset
change email
change password
account preferences or self-service account action
page access check
admin users
admin roles and role permissions
admin runtime settings
```

Optional OAuth endpoints remain separate and must use state/nonce, explicit callback origins, and private client credentials.

## Verification Matrix

- Registration is closed by default and opens only through private configuration.
- Registration never logs the new user in automatically.
- Verification and reset records contain hashes, not raw tokens.
- Expired, malformed, reused, wrong-purpose, and revoked tokens fail safely.
- Reset/resend public responses do not disclose account existence.
- Password reset invalidates existing sessions.
- Anonymous requests cannot reach protected pages or business APIs.
- A lower page permission cannot invoke a higher-permission API even if the UI button is manually re-enabled.
- Cookie-authenticated mutations without valid CSRF fail before state changes.
- Public pages remain public and do not appear in role-permission controls.
- Role changes affect users through group membership; no hidden per-user page grant remains.
- Bootstrap admin cannot be disabled, deleted, or downgraded through UI or API.
- Admin mail settings do not expose site name, public URL, From address/name, envelope sender, mailbox password, OAuth secret, or API key.
- Mail tests are reported as server accepted for delivery unless authoritative delivery is confirmed.
- PHP syntax, account lifecycle tests, role/permission tests, CSRF tests, and deployment manifests pass.

If the sender mailbox is not created or confirmed, report the mail-dependent lifecycle as blocked. If the account APIs are not deployed and verified, do not call the account system complete.

## References

- Read `references/auth-architecture.md` before implementation.
- Read `references/account-lifecycle.md` before registration, verification, resend, reset, email change, or password change work.
- Read `references/page-permissions.md` before changing roles, page access, runtime contracts, or business APIs.
- Read `references/cron-alerts.md` when wrapping scheduled jobs.
- Read `references/ui-guidelines.md` before editing admin screens.

## Assets

- `assets/admin-form.css` contains a compact admin form style snippet that can be adapted to the existing site.

## Safety Rules

- Never commit real users, password hashes, emails, tokens, sessions, mailbox passwords, OAuth secrets, API keys, production settings, or logs.
- Never place private account data or configuration under the public web root.
- Never use a request Host header as the sole source for verification/reset callback URLs; use an explicit private public-base-URL setting.
- Never put raw tokens in storage or logs.
- Never authorize a business API only because its page entrypoint is protected.
- Never rely on front-end button visibility as authorization.
- Never silently change whether a page is public or protected.
- Never make sender infrastructure or credentials editable in the admin UI.
- Never claim email delivery from a successful `mail()` return alone.
