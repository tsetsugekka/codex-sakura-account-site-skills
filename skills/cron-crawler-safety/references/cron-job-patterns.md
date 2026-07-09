# Cron Job Patterns

Use this reference when implementing or reviewing scheduled jobs that update website data. These patterns are distilled from real small-site crawlers that maintain public JSON, private caches, dynamic SEO `<noscript>` blocks, and failure-only cron alerts.

## Start From Existing Artifacts

Read the local truth before changing behavior:

- wrapper shell scripts and crontab examples,
- crawler flags and default values,
- `README`, `SPEC`, `CHANGELOG`, and project maintenance docs,
- deploy preparation scripts and upload manifests,
- restore scripts for SEO marker blocks or public JSON,
- live-data protection lists.

If docs disagree with code, inspect the code and live behavior, then update the docs after fixing the contract.

## File Ownership Matrix

Classify files before deploying or repairing:

| Class | Examples | Rule |
| --- | --- | --- |
| Source input | curated config, static page source, component data | Git can own it. |
| Private runtime | cache, history, raw captures, queues, stamps, auth/session state, logs | Keep outside public web root and usually outside Git. |
| Public generated output | `data.json`, `ranking.json`, public chart JSON, injected SEO block, sitemap | Cron owns it; deploy must not overwrite it with stale local data. |
| Deploy artifact | built `index.html`, JS/CSS assets, static images | Deploy can overwrite it, after preserving cron-managed regions. |

Production repairs should start from the current live file. Prefer running the server-side script that owns the file; if local repair is unavoidable, download the live file, patch only the intended fields, backup live, upload, then fetch back and verify counts/timestamps.

## Wrapper Shape

A safe wrapper should:

- set a predictable `PATH`,
- `cd` to the application directory,
- acquire an atomic lock before starting,
- exit `0` for lock skip,
- use a slot/day stamp when cron wakes more often than the real job,
- run the command with bounded runtime,
- append output to a private log,
- rotate or retain a bounded number of logs,
- refresh sitemap/robots after successful public data writes when the site uses them,
- send mail only when the crawler or validation fails.

Use `scripts/write_cron_wrapper.py` to scaffold only when the project lacks a better local wrapper pattern.

## Lock, Stamp, and Queue

Use a lock for mutual exclusion and a stamp for idempotence:

- lock means "another run is active"; skip without alert,
- stamp means "this slot/day already succeeded or was already attempted"; skip without alert,
- retry stamps can prevent an infinite same-day retry loop,
- queue means "manual work is valid but unsafe right now"; defer it into the normal production cron path.

For repair or manual backfill commands that would conflict with active cron windows, queue instead of directly writing public output. Good queue reasons include: lock held, market/source cron not started, cron starts soon, full batch not done, or output source not yet published.

## Per-Run Budgets

Long crawler universes should be split:

- cap pages per run,
- cap source requests per slot/hour,
- cap markets or source groups per wake-up,
- cap retries,
- cap enrichment/model calls,
- stop requesting an enrichment source after repeated transient failure and keep last-good data.

This avoids one slow source blocking every other source and avoids retry storms.

## Atomic Output

For each public output:

1. Write to a temp file in the same directory.
2. Validate JSON/HTML/schema/minimum row count.
3. Optionally copy current final file to `.previous` or a timestamped private backup.
4. Rename temp to final with same-filesystem atomic replace.

Do not write half-complete JSON directly to a live public file. If the job emits multiple related files, publish only after the internally consistent set is ready.

## Partial Data Rules

Decide whether partial output is allowed:

- For dashboards that must represent a complete market/source universe, write final public JSON only after the market/source batch completes.
- For feed pages designed for incremental updates, publish bounded new entries but preserve old inventory and avoid deleting unseen history.
- For enrichment-only fields, keep the base page update even if enrichment fails; mark missing values clearly and reuse cache.

Do not treat "empty because parsing broke" as a valid empty output. Parse/schema failure should keep last-good data and alert.

## SEO and HTML Marker Regions

When cron updates `noscript` or SEO HTML:

- wrap the region with stable start/end markers,
- keep the marker contract in docs,
- fetch live `index.html` before static deploy,
- merge the live marked region into the new build,
- fail packaging if the live file or markers are missing,
- document an emergency restore command that rebuilds the marker from current live data without re-scraping sources.

Static SEO fallback should avoid real data/news/post timestamps when the page is not an article. Use server-side stamp files for daily throttling instead of HTML date comments. Visible UI times can remain visible, but add `data-nosnippet`.

## Root SEO Refresh

If the site has generated `robots.txt` or `sitemap.xml`, successful public data writes should refresh them so sitemap dates move with data updates, not only with manual UI deploys.

SEO refresh failure should usually log and continue if the primary data job succeeded; do not turn a good data publish into a failed crawler solely because a secondary sitemap write failed.

## Failure-Only Alerts

Alert on:

- non-zero crawler exit,
- validation failure,
- parse/schema failure,
- permission failure,
- failed atomic rename,
- repeated queue failure.

Do not alert on:

- success,
- no data changed,
- lock skip,
- already-ran stamp,
- expected no-op schedule window,
- normal defer/queue,
- source not modified.

Alert body should include job name, slot, host, cwd, command label, exit code, timestamp/timezone, log path, and a short sanitized log tail. Never include credentials, cookies, authorization headers, full tokens, personal data, or huge raw responses.

## Cron Entry Example

```cron
*/15 * * * * /path/to/tools/run-example-crawler.sh >/dev/null 2>&1
```

Keep useful logging inside the wrapper or application log. Avoid cron daemon mail on every success.
