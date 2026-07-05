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

