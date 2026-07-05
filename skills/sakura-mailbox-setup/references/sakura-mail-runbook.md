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
- If Sakura Control Panel access is authorized, open the mail/mailbox section and create the mailbox there. The user should type control-panel credentials and mailbox password when needed.
- If the control panel cannot be accessed, stop and report the mailbox as not created. Provide manual instructions instead of claiming the mail setup is complete.
- Never save the mailbox password in Git, `LOCAL_DEPLOY_SECRETS.md`, project docs, shell history, or admin-editable JSON.

Manual checklist when control-panel access is unavailable:

```text
1. Open Sakura Server Control Panel.
2. Open the mail / domain mail settings area for the target domain.
3. Create the sender mailbox, for example notify@example.com.
4. Save the password only in Sakura/password manager, not in the project repository.
5. Return to Codex with the sender email address only.
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
