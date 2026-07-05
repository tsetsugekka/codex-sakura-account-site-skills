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
- If Sakura Control Panel access is authorized through browser/computer use, Codex should open the mail/mailbox section and create the mailbox there.
- For control-panel login, 2FA, and mailbox password fields, follow the user's delegation. The user may type secrets directly, or may explicitly ask Codex to generate/fill a strong mailbox password. Do not ask the user to perform the whole mailbox creation flow if Codex can operate the panel.
- If the control panel cannot be accessed after trying the authorized path, stop and report the mailbox as not created. Provide fallback instructions instead of claiming the mail setup is complete.
- Never save the mailbox password in Git, `LOCAL_DEPLOY_SECRETS.md`, project docs, shell history, or admin-editable JSON.

Fallback checklist when control-panel access is unavailable:

```text
1. Tell the user that Codex could not access Sakura Control Panel, so mailbox creation is not complete.
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
