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

Shell sendmail pattern:

```sh
sendmail -t -f "$MAIL_FROM" < "$message_file"
```

If Sakura control panel cannot create a mailbox for the domain, stop and ask the user to confirm the domain is attached to the server account.

