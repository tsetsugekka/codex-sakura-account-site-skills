---
name: sakura-auth-site-setup
description: Add a Japanese account system to a Sakura-hosted website. Use when Codex needs to implement user groups, registration with email verification, cron failure notification settings, role-based page permissions, an admin/supervisor screen that matches the existing site style, safe storage outside the public web root, and a rule that mail delivery is not complete until the Sakura sender mailbox is created or confirmed.
---

# Sakura Auth Site Setup

## Goal

Add a production-ready account system to a Sakura-hosted website while preserving the existing site's visual style. Mail delivery is production-ready only after the real Sakura sender mailbox is created or confirmed.

## Core Requirements

- Japanese UI and Japanese email by default.
- User records stored outside the public web root.
- Passwords stored with a modern password hash, never plaintext.
- Registration disabled by default unless explicitly enabled.
- Registration requires email verification before login.
- New registrations stay disabled or in a pending group until email verification.
- Verified users default to the `user` group unless the user explicitly requested another default group.
- Do not default verified registrations to `demo`.
- Role groups control page access.
- Page permissions are saved on roles/user groups, not individual users.
- Protected page entrypoints inject a server-evaluated page permission value for the page using a project-scoped runtime global.
- Page UI and page APIs enforce page-defined permission keys; do not infer behavior from global role names.
- Admin/supervisor page edits users, roles, page permissions, and cron failure recipient only.
- Admin/supervisor page must not edit site name, public URL, From address, From display name, or envelope sender.
- Cron jobs send email only on failures, never on success.
- Mail sender uses a real mailbox created or confirmed through `sakura-mailbox-setup`.

## Workflow

1. Inspect the existing site stack, routing, style system, and deploy process.
2. Define private storage paths outside `www`.
3. Add authentication API endpoints.
4. Add session and page access checks.
5. Confirm the sender mailbox through `sakura-mailbox-setup` before claiming registration email or cron email is production-ready.
6. Add role model:
   - a pending group such as `unverified`: newly registered users before email verification.
   - a default group such as `user`: normal verified users.
   - optional groups such as `staff`: limited private pages.
   - `admin`: fixed full access.
7. Add registration:
   - disabled by default,
   - requires email,
   - creates disabled pending user or assigns the pending group,
   - stores only token hash and expiry,
   - sends Japanese verification email,
   - enables or promotes the user to `user` after verification unless the user explicitly requested another policy.
8. Add admin/supervisor UI:
   - match the existing navigation, header, card, form, and input style,
   - no marketing landing page,
   - compact operational layout,
   - permission controls only for actually protected pages,
   - public pages stay public even if they are shown in a staff-like navigation group,
   - cron notification UI contains the failure-recipient email and optional test-send action only,
   - no fields for site name, public URL, From address, From name, or envelope sender.
9. Add cron failure notification setting:
   - save recipient in private settings file,
   - send Japanese confirmation mail when non-empty,
   - wrappers send failure email on non-zero status only.
10. Add protected page handoff:
   - central account code decides whether a request may enter the page,
   - the entry PHP injects a project-scoped global such as `window.SITE_AUTH.pagePermission`,
   - the page reads that value for buttons/forms/features,
   - page-specific APIs repeat the same permission check server-side.
11. Deploy and verify:
   - PHP syntax,
   - shell/Python cron syntax,
   - registration remains closed by default,
   - invalid verification token returns safe error,
   - public pages remain public,
   - protected pages deny anonymous access,
   - verified registration creates or promotes the user to `user`, not `demo`,
   - admin mail UI does not contain `サイト名`, `公開URL`, `送信元メール`, or `送信元名`,
   - test mail is accepted by the server.

If the real sender mailbox is not created or confirmed, report that mail delivery remains blocked instead of saying the mail features are complete.

## References

- Read `references/auth-architecture.md` before implementation.
- Read `references/page-permissions.md` when deciding what belongs in the admin permission screen.
- Read `references/cron-alerts.md` when wrapping scheduled jobs.
- Read `references/ui-guidelines.md` before editing admin screens.

## Assets

- `assets/admin-form.css` contains a compact admin form style snippet that can be adapted to the existing site.

## Safety Rules

- Do not include real usernames, passwords, mailbox passwords, or production user JSON in commits.
- Do not put private settings, user DB, verification tokens, or logs under the public web root.
- Do not redirect old admin paths to new hidden paths if the user explicitly wants no redirect.
- Do not silently make public pages protected or protected pages public; document permission changes.
- Do not put a public page in the admin permission screen only because it appears in a staff-only sidebar group.
- Do not make infrastructure mail sender settings editable from the admin UI.
