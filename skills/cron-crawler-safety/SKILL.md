---
name: cron-crawler-safety
description: Use when building, auditing, or repairing cron-driven crawlers, scrapers, scheduled feed collectors, SEO injectors, JSON generators, or static-site data refresh jobs for Sakura Server or other small websites, with safe crawling, polite rate limits, locks, timeouts, atomic writes, production-data protection, failure-only email alerts, and deploy-safe handling of cron-injected HTML.
---

# Cron Crawler Safety

Use this skill for website cron jobs and crawler/scraper pipelines that update public pages, JSON feeds, SEO fallback blocks, alerts, or cached data.

The goal is not only "make the scraper work"; the goal is a production job that is polite to sources, safe for the website, observable on failure, and hard to corrupt during deploys.

## Required Behavior

- Confirm the crawler is allowed and appropriate:
  - prefer official APIs, feeds, sitemaps, or export endpoints when available,
  - respect robots.txt, published API terms, rate limits, authentication boundaries, and copyright,
  - do not bypass paywalls, CAPTCHAs, login controls, bot defenses, or access restrictions,
  - do not scrape private/personal data unless the user owns the data source or has explicit authorization.
- Make cron jobs boring and recoverable:
  - one job instance at a time with a lock,
  - bounded runtime with timeout,
  - deterministic working directory and environment,
  - structured logs outside public web roots,
  - non-zero exit on real failure,
  - no email on success, normal no-op, lock skip, or expected partial batch.
- Protect production data:
  - write to temp files first, validate, then atomic rename,
  - keep last-good data if a fetch or parse fails,
  - never overwrite live JSON/HTML with stale local snapshots,
  - backup before destructive migrations,
  - separate source data, runtime data, generated public data, and deploy artifacts.
- Protect deploy-time cron injections:
  - when cron updates a `noscript`, SEO, or HTML marker region, fetch the latest live HTML and merge that managed region before uploading a new static `index.html`,
  - do not overwrite scraper-owned SEO blocks with an older local build,
  - combine with `static-deploy-refresh-check` for stale JS/CSS cache refresh on static pages.
- Add failure-only notification:
  - use a wrapper that sends mail only when the command exits non-zero,
  - include job name, host, cwd, command, exit code, timestamp, and a short sanitized log tail,
  - do not include credentials, cookies, raw personal data, full tokens, or huge logs,
  - keep the recipient configurable in private server settings or environment, not hardcoded in source.

## Workflow

1. Inventory the job.
   - Identify cron entry, command, working directory, source URLs/APIs, output files, public page dependencies, logs, and notification path.
   - Identify whether outputs are public assets, private cache, runtime state, or source-of-truth data.
2. Review source access safety.
   - Read `references/safe-crawling-policy.md`.
   - Prefer APIs or feeds. If scraping HTML, set a clear User-Agent and conservative cadence.
   - Add exponential backoff, jitter where useful, and conditional requests (`ETag` / `Last-Modified`) when supported.
3. Design the cron wrapper.
   - Read `references/cron-job-patterns.md`.
   - Use a lock directory/file, timeout, stable PATH, explicit cwd, and log file.
   - Use `scripts/write_cron_wrapper.py` when a reusable shell wrapper is useful.
4. Harden the crawler code.
   - Request timeout on every network call.
   - Retry only transient failures, with a strict max.
   - Treat parse changes as failures or degraded output, not as empty success.
   - Validate minimum row counts, required keys, schema, and timestamp monotonicity before publish.
5. Publish outputs safely.
   - Write `output.tmp`, validate it, then atomic rename to `output.json` or equivalent.
   - Keep `output.previous` or a timestamped backup for critical public data.
   - For public HTML marker injection, update only the marked block and preserve unrelated live HTML.
6. Wire failure-only email.
   - If the project uses `sakura-auth-site-setup`, reuse its cron failure notification setting and mail helper.
   - Otherwise keep recipient/from settings in private config or environment.
   - Do not send on success or expected no-op.
7. Document operations.
   - Record cron schedule, owner, outputs, logs, lock path, data ownership, retry policy, and restore method in the project maintenance docs.
   - If the page has public SEO fallback, document which script owns each marker block.
8. Verify.
   - Run the crawler once manually with a harmless target or dry-run.
   - Run the wrapper with a command that succeeds and confirm no email.
   - Run the wrapper with a command that fails and confirm failure notification.
   - Confirm lock skip does not email.
   - Confirm deploy does not erase cron-managed live data or marker blocks.

## Sakura Notes

- Keep private runtime data outside `www`, for example under `/home/<account>/<app>_data/` or another non-public directory.
- Public JSON/HTML under `www` should be generated from validated private/runtime data, not used as the only source of truth.
- Sakura cron environments are minimal. Set PATH, cd to the project directory, and avoid relying on interactive shell startup files.
- Use Sakura `sendmail`/`mail` or the project's existing mail helper for alerts; do not store SMTP or mailbox passwords in the repository.
- If deployment uses SFTP manifests, include scripts and public outputs deliberately. Do not recursively upload runtime directories, caches, logs, user data, or secret config.

## Safety Rules

- Do not help bypass access controls, paywalls, CAPTCHAs, bot defenses, or rate limits.
- Do not collect credentials, cookies, personal data, private messages, or account-only content unless authorization is explicit and the data stays private.
- Do not publish raw scraped content wholesale when a summary, metadata, or link is sufficient.
- Do not run aggressive crawl rates. Default to slow schedules and small batches.
- Do not hide crawler identity. Use a clear site/tool User-Agent and contact URL/email when appropriate.
- Do not hardcode real domains, emails, account names, passwords, API keys, or absolute private paths in reusable skill files.
- Do not call a cron job "healthy" until its failure path, lock path, and output validation are tested.
