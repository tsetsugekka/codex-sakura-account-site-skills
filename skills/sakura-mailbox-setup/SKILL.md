---
name: sakura-mailbox-setup
description: Configure website email sending on Sakura Server. Use when Codex needs to create a real Sakura mailbox in Sakura Control Panel with authorized browser/computer control, verify an existing mailbox, verify domain DNS, choose a From/envelope sender, store sender/public URL settings in private server configuration rather than admin UI, update PHP or cron mail code, and send safe Japanese test emails without storing mailbox passwords in the repository.
---

# Sakura Mailbox Setup

## Goal

Use a real Sakura mailbox as the website notification sender so account verification, settings confirmation, and cron failure alerts are deliverable.

Do not mark this skill complete until a real sender mailbox has either been created or its existence has been confirmed.

If the user authorizes browser/computer use, Codex should handle the Sakura Control Panel mailbox creation flow. Reuse an existing authenticated Sakura Control Panel session or approved credential path when available; do not ask the user to log in again unless the session is missing, expired, or requires fresh confirmation. Do not default to telling the user to create the mailbox manually.

## Workflow

1. Confirm the domain and intended sender address, for example `notify@example.com`.
2. Determine whether the mailbox already exists:
   - if it exists, record only the address and confirmation method,
   - if it does not exist, use Sakura Server Control Panel to create it.
3. When SSH credentials are already available through an ignored local secret file or a secure user prompt, use SSH only for reconnaissance before control-panel creation:
   - check whether a mailbox directory such as `/home/<account>/MailBox` already contains the intended mailbox,
   - check mail tools such as `mail`, `sendmail`, PHP `mail()`, and any provider-specific mailbox commands,
   - do not assume SSH can create Sakura managed mailboxes unless a verified provider command exists.
4. If the user explicitly authorizes browser/computer control, open or use the Sakura Control Panel session and create the mailbox there. If Sakura is already authenticated in the available browser/session context, continue without interrupting the user. If private deploy credentials can log in to the control panel, use them without printing values. For login, 2FA, and mailbox password fields, follow the user's delegation: the user may type them, or the user may explicitly ask Codex to generate/fill a strong mailbox password. Do not store or print control-panel credentials or mailbox passwords.
5. In the control panel, use the mail address management flow: open the mail address list, choose new/add, fill the mailbox local part, a neutral description, a strong password, and a minimal reasonable quota such as the panel default. If the user has already granted broad live-change permission, proceed without repeated confirmation for normal recoverable steps. Ask a concise confirmation only when authorization is unclear, the action is hard to undo, may create cost, deletes data, expands public access, or changes/rotates secrets.
6. If control-panel access is unavailable after attempting the authorized path, stop and report that mailbox creation is blocked. Give the fallback checklist and do not claim Sakura mail setup is complete.
7. Confirm the mailbox exists on the server or in the control panel.
8. Check DNS:
   - A/AAAA or CNAME for the domain,
   - MX records,
   - SPF TXT,
   - DKIM availability if Sakura provides it,
   - DMARC if the user wants stricter policy.
9. Update website mail code:
   - `From: Site Name <notify@example.com>`
   - envelope sender `-fnotify@example.com` for `sendmail` or PHP `mail()`.
10. Store infrastructure mail settings in private server configuration, not in an admin-editable settings file:
   - site name,
   - public base URL,
   - From address,
   - From display name,
   - envelope sender.
11. Keep admin UI limited to runtime notification recipients, usually only cron failure recipient and a test-send action.
12. Keep mail body in Japanese by default. Add other languages only if the site requires it.
13. Send a harmless test email to the configured recipient.
14. Report only success/failure and masked addresses. Do not print passwords.

## Proven End-to-End Pattern

Use this order when implementing a new Sakura site:

1. Browser/computer use: open Sakura Control Panel and create or confirm the sender mailbox on the real domain. If an authenticated Sakura session is already available, use it; a fresh user login is not required.
2. User-only input: request Sakura login, 2FA, or delegated secret entry only when the session is absent, expired, or asks for fresh confirmation. Do not expose secrets in chat, files, logs, or commits.
3. SSH reconnaissance: before creating a new mailbox, SSH may confirm existing mailbox folders and available mail tools, using a temporary local helper that reads ignored local secrets without printing them.
4. Control-panel creation: if SSH shows no existing mailbox and no verified provider mailbox-creation command, create the mailbox through Sakura Control Panel instead of handing the task to the user.
5. SSH/SFTP verification: after the mailbox exists, check server mail tools such as `sendmail`, `mail`, and PHP `mail()`.
6. Private config: write site name, public URL, From address, From display name, and envelope sender into environment variables or `config.local.php`.
7. Application code: use the same sender for registration verification, cron failure alerts, and notification-setting confirmation.
8. Admin UI: expose only the cron failure recipient and optional test-send action.
9. Verification: send a harmless test email and report whether the server accepted it for delivery.

Do not try to treat SSH as the mailbox-creation step. SSH is for reconnaissance, website-side configuration, and verification. Sakura managed mailbox account creation belongs to the control-panel path unless a verified Sakura mailbox CLI is present.

## Completion Criteria

The task is complete only when all are true:

- the sender mailbox has been created in Sakura Control Panel or an existing mailbox was confirmed,
- website code/config uses that real mailbox as From and envelope sender,
- registration verification mail and cron alert mail use the same server-configured sender,
- a test send was accepted by the server, or a precise delivery blocker is reported.

If the mailbox was not created or confirmed, say that clearly and leave the task as blocked/pending. Do not summarize the website-side code as "Sakura mail configured" in that state.

## Confirmation Discipline

Minimize confirmation prompts. Once the user has delegated the Sakura setup task and authorized browser/computer use, continue through normal, recoverable setup steps without asking again. Creating a sender mailbox for the requested site is a normal step when it can be deleted or changed later. Ask again only for high-risk boundaries: destructive changes, extra cost, public exposure, secret rotation, unclear target account/domain, or irreversible actions.

## Helper Script

Use `scripts/check_mail_dns.sh example.com notify@example.com` to collect DNS and local mail binary checks.

## References

- Read `references/sakura-mail-runbook.md` for control panel and server checks.
- Read `references/japanese-mail-templates.md` for standard Japanese email wording.

## Safety Rules

- Do not commit mailbox passwords.
- Do not print mailbox passwords.
- Do not use a fake sender address that does not exist.
- Do not skip mailbox creation just because Sakura has no stable SSH mailbox-creation command; use the control panel when the user authorizes browser/computer control.
- Do not present manual mailbox creation as the normal path when authorized browser/computer control is available.
- Do not require a fresh Sakura login when an existing authenticated control-panel session or approved credential path is available.
- Do not print local secret file contents, control-panel credentials, generated mailbox passwords, or SSH passwords.
- Do not ask for repeated confirmations for normal recoverable steps after the user has broadly delegated the task.
- Do not claim completion when mailbox creation is still a manual TODO.
- Do not say "mail configured" after only changing code over SSH; the Sakura mailbox must be created or confirmed first.
- Do not expose site name, public URL, From address, From name, or envelope sender as admin UI fields.
- Do not store sender infrastructure values in an admin-editable `site_settings.json`.
- Do not send test mail to arbitrary third parties. Use the user's configured recipient or a user-approved test address.
- Do not promise inbox delivery only because `mail()` returned true; say the server accepted the message for delivery.
