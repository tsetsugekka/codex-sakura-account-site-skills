# Sakura Mail Runbook

Server checks:

```bash
which sendmail || true
which mail || true
/usr/local/bin/php -i | grep -i sendmail
```

DNS checks:

```bash
dig MX example.com
dig TXT example.com
dig TXT _dmarc.example.com
```

Mailbox creation contract:

- Creating or confirming the real sender mailbox is part of this skill, not an optional afterthought.
- Prefer a sender such as `notify@example.com`, using the site's real domain.
- If an ignored local deploy secret file already exists, Codex may use it to authenticate SSH/SFTP. On Sakura Rental Server, the server account/domain password is also the Sakura Control Panel login credential. Use the same value for the control panel when it was collected as Sakura server credentials. Never print the values.
- If Sakura Control Panel access is authorized through browser/computer use, Codex should open the mail/mailbox section in the Codex in-app browser when available, or another isolated browser context, and create the mailbox there.
- Do not operate the user's active Chrome tabs, windows, or page content unless the user explicitly authorizes that exact session for the current task.
- If an authenticated Sakura Control Panel session or approved control-panel credential path is already available in the isolated context, Codex should reuse it and should not require the user to log in again.
- For control-panel login, 2FA, and mailbox password fields, follow the user's delegation. The user may type secrets directly, or may explicitly ask Codex to generate/fill a strong mailbox password. Do not ask the user to perform the whole mailbox creation flow if Codex can operate the panel.
- If the control panel cannot be accessed after trying the authorized path, stop and report the mailbox as not created. Provide fallback instructions instead of claiming the mail setup is complete.
- Never save the mailbox password in Git, `LOCAL_DEPLOY_SECRETS.md`, project docs, shell history, or admin-editable JSON.

Observed successful flow, generalized:

```text
1. Read only the necessary SSH/SFTP fields from an ignored local deploy secret or secure prompt; never echo values.
2. Use a temporary local SSH helper when needed to avoid leaking SSH/SFTP passwords into shell history or command output.
3. Over SSH, inspect the Sakura account for existing mailbox folders and available commands such as mail, sendmail, PHP mail, or provider-specific mailbox tools.
4. If the intended mailbox does not exist and no verified SSH mailbox-creation command is available, open Sakura Control Panel with browser/computer use in the Codex in-app browser when available, or in a separate browser profile, automation browser, or dedicated window/tab that the user is not actively using.
5. Reuse an existing authenticated Sakura session only when it is available in that isolated context, or when the user explicitly allows Codex to operate the current browser session; otherwise use the approved Sakura server/account credentials, or ask the user only for missing login, 2FA, or delegated secret input.
6. In the mail address list, use the new/add flow, fill the mailbox local part, description, strong password, and the default or smallest reasonable quota.
7. If broad live-change permission was already granted and the action is a normal recoverable setup step, submit without asking again. If authorization is unclear or the action is destructive, costly, public-facing, secret-rotating, or hard to undo, stop and ask one concise confirmation.
8. After creation, use SSH/SFTP for sendmail/PHP mail checks, private config, application code, and delivery testing.
9. Store sender identity in private server config, not admin UI.
10. Wire registration verification, cron failure alerts, and setting-confirmation mail to that sender.
11. Send a test message and report server acceptance without revealing secrets.
```

Do not replace control-panel creation with SSH unless a verified Sakura mailbox CLI exists. In the proven path, SSH is reconnaissance and post-creation verification; Sakura mailbox account creation belongs to the control-panel path.

SSH reconnaissance examples:

```bash
command -v mail || true
command -v sendmail || true
command -v postconf || true
command -v doveadm || true
command -v vadduser || true
command -v virtualmin || true
find /home/ACCOUNT -maxdepth 3 \( -iname "*mail*" -o -iname ".forward" -o -iname ".qmail*" \) | sed -n "1,120p"
```

Control-panel route:

```text
1. Open Sakura Server Control Panel in the Codex in-app browser when available, or another isolated browser context. Do not steal focus from the user's active browsing when a separate browser/profile/tool session is available.
2. If a login form appears, use approved Sakura server account/domain credentials. These are the same values used for SSH/SFTP when collected for the Sakura server account. Do not substitute unrelated generic deploy credentials.
3. Open the mail address management page.
4. Confirm whether only default mailboxes such as postmaster exist.
5. Click the new/add mail address action.
6. Fill the mailbox local part, description, password, and quota.
7. Submit creation when authorized by the user's broad instruction or an explicit confirmation. Do not add extra confirmations for normal recoverable setup steps.
```

Fallback checklist when control-panel access is unavailable:

```text
1. Tell the user that Codex could not access Sakura Control Panel without disturbing the user's active browser, so mailbox creation is not complete.
2. Ask the user to open Sakura Server Control Panel only as a fallback.
3. Ask the user to open the mail / domain mail settings area for the target domain.
4. Ask the user to create the sender mailbox, for example notify@example.com.
5. Remind the user not to put the mailbox password in the project repository.
6. Resume only after the sender email address has been created or confirmed.
```

PHP mail pattern:

```php
$from = 'notify@example.com';
$headers = [
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'From: Site Name <' . $from . '>',
];
mail($to, $encodedSubject, $body, implode("\r\n", $headers), '-f' . $from);
```

Configuration boundary:

- Keep `site_name`, `public_base_url`, `mail_from`, `mail_from_name`, and `mail_envelope_sender` in private server configuration such as environment variables or `config.local.php`.
- Do not put those values in an admin-editable settings JSON.
- Do not add admin form fields for `サイト名`, `公開URL`, `送信元メール`, or `送信元名`.
- Admin UI may edit notification recipients, for example `cronFailureEmail`, but not the sender identity.

Private config example:

```php
return [
    'site' => [
        'name' => 'Example Site',
        'public_base_url' => 'https://example.com',
    ],
    'mail' => [
        'from' => 'notify@example.com',
        'from_name' => 'Example Site',
        'envelope_sender' => 'notify@example.com',
    ],
];
```

Shell sendmail pattern:

```sh
sendmail -t -f "$MAIL_FROM" < "$message_file"
```

If Sakura control panel cannot create a mailbox for the domain, stop and ask the user to confirm the domain is attached to the server account.
