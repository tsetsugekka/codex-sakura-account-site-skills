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
