---
name: sakura-auth-site-setup
description: Add a Japanese account system to a Sakura-hosted website. Use when Codex needs to implement user groups, registration with email verification, cron failure notification settings, role-based page permissions, an admin/supervisor screen that matches the existing site style, and safe storage outside the public web root.
---

# Sakura Auth Site Setup

## Goal

Add a production-ready account system to a Sakura-hosted website while preserving the existing site's visual style.

## Core Requirements

- Japanese UI and Japanese email by default.
- User records stored outside the public web root.
- Passwords stored with a modern password hash, never plaintext.
- Registration disabled by default unless explicitly enabled.
- Registration requires email verification before login.
- Verified new users default to the `user` group.
- Role groups control page access.
- Admin/supervisor page edits users, roles, page permissions, and cron failure email settings.
- Cron jobs send email only on failures, never on success.
- Mail sender uses a real mailbox configured through Sakura.

## Workflow

1. Inspect the existing site stack, routing, style system, and deploy process.
2. Define private storage paths outside `www`.
3. Add authentication API endpoints.
4. Add session and page access checks.
5. Add role model:
   - `user`: default verified users.
   - `staff`: limited private pages.
   - `admin`: fixed full access.
6. Add registration:
   - disabled by default,
   - requires email,
   - creates disabled pending user,
   - stores only token hash and expiry,
   - sends Japanese verification email,
   - enables user as `user` after verification.
7. Add admin/supervisor UI:
   - match existing sidebar/header/card/input style,
   - no marketing landing page,
   - compact operational layout,
   - page permission checkboxes only for actually protected pages.
8. Add cron failure notification setting:
   - save recipient in private settings file,
   - send Japanese confirmation mail when non-empty,
   - wrappers send failure email on non-zero status only.
9. Deploy and verify:
   - PHP syntax,
   - shell/Python cron syntax,
   - registration remains closed by default,
   - invalid verification token returns safe error,
   - public pages remain public,
   - protected pages deny anonymous access,
   - test mail is accepted by the server.

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

