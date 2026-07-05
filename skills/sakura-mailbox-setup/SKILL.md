---
name: sakura-mailbox-setup
description: Configure website email sending on Sakura Server. Use when Codex needs to create or guide creation of a real Sakura mailbox, verify domain DNS, choose a From/envelope sender, update PHP or cron mail code, and send safe Japanese test emails without storing mailbox passwords in the repository.
---

# Sakura Mailbox Setup

## Goal

Use a real Sakura mailbox as the website notification sender so account verification, settings confirmation, and cron failure alerts are deliverable.

## Workflow

1. Confirm the domain and intended sender address, for example `notify@example.com`.
2. In Sakura Server Control Panel, create the mailbox. Do not store the mailbox password in Git.
3. Confirm the mailbox exists on the server or in the control panel.
4. Check DNS:
   - A/AAAA or CNAME for the domain,
   - MX records,
   - SPF TXT,
   - DKIM availability if Sakura provides it,
   - DMARC if the user wants stricter policy.
5. Update website mail code:
   - `From: Site Name <notify@example.com>`
   - envelope sender `-fnotify@example.com` for `sendmail` or PHP `mail()`.
6. Keep mail body in Japanese by default. Add other languages only if the site requires it.
7. Send a harmless test email to the configured recipient.
8. Report only success/failure and masked addresses. Do not print passwords.

## Helper Script

Use `scripts/check_mail_dns.sh example.com notify@example.com` to collect DNS and local mail binary checks.

## References

- Read `references/sakura-mail-runbook.md` for control panel and server checks.
- Read `references/japanese-mail-templates.md` for standard Japanese email wording.

## Safety Rules

- Do not commit mailbox passwords.
- Do not print mailbox passwords.
- Do not use a fake sender address that does not exist.
- Do not send test mail to arbitrary third parties. Use the user's configured recipient or a user-approved test address.
- Do not promise inbox delivery only because `mail()` returned true; say the server accepted the message for delivery.

