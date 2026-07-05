# Cron Failure Alerts

Wrap scheduled jobs so success never sends mail.

Send mail only when:

- the scraper command returns non-zero,
- the Python process raises an unhandled exception,
- the wrapper detects a hard failure.

Do not send mail when:

- the job succeeds,
- there is no task in the current time window,
- a lock prevents concurrent execution,
- a normal batch intentionally stops before completion.

Store the recipient in a private settings file, for example:

```json
{"cronFailureEmail": "operator@example.com"}
```

That admin-editable settings file must only contain runtime notification choices such as `cronFailureEmail`. It must not contain site name, public URL, From address, From display name, envelope sender, mailbox password, SMTP password, or Sakura control-panel credentials.

Sender identity must come from private server configuration such as environment variables or `config.local.php`, created during Sakura mailbox setup.

Before declaring cron alerts production-ready, confirm the sender mailbox was created or confirmed by `sakura-mailbox-setup`. If not, the cron wrapper can be implemented but delivery remains blocked.

Validate that the address is syntactically valid, shorter than 255 characters, and contains no newline characters. When the admin saves a non-empty recipient, send a Japanese confirmation email so the operator knows the setting is active.

Recommended body fields:

```text
処理名:
ホスト:
状態:
時刻:
ログ:
直近ログ:
```

Use the same real sender mailbox as account verification:

```text
From: Site Name <notify@example.com>
Envelope sender: notify@example.com
```

Keep logs outside the public web root.

Use Sakura `sendmail` or `mail` when available. Do not store SMTP credentials in the repository just to make cron alerts work.

Admin UI rules:

- Label the section as cron failure notification settings.
- Allow editing only the failure-recipient address.
- Optional test-send is acceptable if it uses the server-configured sender.
- Do not add fields for `サイト名`, `公開URL`, `送信元メール`, or `送信元名`.
