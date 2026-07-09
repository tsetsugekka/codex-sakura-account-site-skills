# Cron Job Patterns

Use this reference when implementing or reviewing scheduled jobs that update website data.

## Wrapper Shape

A safe wrapper should:

- set `set -u` and carefully handle exit codes,
- set a predictable `PATH`,
- `cd` to the application directory,
- acquire a lock before starting,
- exit `0` for lock-skip when another instance is running,
- run the command with a timeout,
- append output to a private log,
- send mail only when the command fails,
- include a sanitized log tail in the alert.

Use `scripts/write_cron_wrapper.py` to scaffold this pattern when useful.

## Locking

Portable choices:

- `mkdir "$LOCK_DIR"` as an atomic lock on POSIX systems.
- `flock` if the host provides it and the project already uses it.

For simple shared hosting, `mkdir` locking is often the safest portable default.

Always clean the lock on normal exit, failure, and interrupt with a trap. If stale locks are possible, record the PID and timestamp inside the lock and document the manual recovery procedure.

## Timeouts

Every layer needs a bound:

- network requests inside crawler code,
- whole-command timeout in the wrapper,
- cron schedule that leaves enough gap before the next run.

If the platform lacks GNU `timeout`, use the language runtime timeout, a small shell watchdog, or a host-specific command. Do not leave unbounded browser automation or HTTP requests in cron.

## Atomic Output

For each public output:

1. Write to a temp file in the same directory, for example `data.json.tmp.$$`.
2. Validate JSON/HTML/schema/minimum row count.
3. Optionally copy current `data.json` to `data.json.previous`.
4. Rename temp to final path.

Same-directory rename keeps publication atomic on one filesystem. Do not write half-complete JSON directly to the live public file.

## Production Data Ownership

Classify files before deploying:

- **Source input**: curated static data in Git.
- **Private runtime**: crawler cache, history, queues, raw captures, auth state; keep outside public web root and usually out of Git.
- **Public generated output**: JSON, HTML region, or sitemap consumed by browsers/search engines.
- **Deploy artifact**: built JS/CSS/HTML from local source.

Deploys may overwrite deploy artifacts. They must not overwrite private runtime files or public generated outputs unless the deploy explicitly owns that file.

If a static `index.html` contains cron-injected marker regions, fetch the current live HTML before deploy and merge those regions into the new build.

## Failure-Only Alerts

Alert on:

- non-zero command exit,
- validation failure,
- permission failure,
- parse/schema failure,
- failed atomic rename,
- repeated queue failure.

Do not alert on:

- success,
- no data changed,
- lock skip,
- expected queue/defer,
- source 304 not modified.

Alert body should include:

- job name,
- host,
- cwd,
- command label,
- exit code,
- timestamp and timezone,
- log path,
- short sanitized log tail.

Never include credentials, cookies, session headers, full tokens, personal data, or huge raw responses.

## Cron Entry Example

```cron
*/15 * * * * /path/to/tools/run-example-crawler.sh >/dev/null 2>&1
```

Keep all useful logging inside the wrapper or application log. Avoid noisy cron mail on every success.
