---
name: cron-crawler-safety
description: Use when building, auditing, or repairing cron-driven crawlers, scrapers, scheduled feed collectors, SEO injectors, JSON generators, or static-site data refresh jobs for Sakura Server or other small websites, especially when existing cron/Python docs, live-data ownership, per-host pacing, locks, atomic writes, failure-only email, or deploy-safe cron-injected HTML are involved.
---

# Cron Crawler Safety

Use this skill for website cron jobs and crawler/scraper pipelines that update public pages, JSON feeds, SEO fallback blocks, alerts, cached data, or sitemap files.

The core rule is: start from the site's real cron scripts and docs, then preserve the production contract. Do not replace a working crawler with generic advice before reading how its live data, cache, SEO, deploy, and alert paths already behave.

## Required First Pass

Before editing or adding a job, inspect the project-specific sources:

- cron wrappers, crontab docs, deploy scripts, and SFTP manifests,
- Python/JS crawler scripts and their command-line flags,
- `README`, `SPEC`, `CHANGELOG`, maintenance docs, and recovery notes,
- public output files, private cache/history paths, lock/stamp files, and live HTML marker names.

If the project has a `README/SPEC/CHANGELOG` pattern, update those docs in the same task when changing crawler behavior, cron timing, deploy protection, SEO output, alerts, data ownership, or recovery steps.

## Required Behavior

- Preserve the production data contract:
  - classify each file as source input, private runtime/cache/history, public generated output, or deploy artifact,
  - never overwrite live cron-owned JSON/HTML with stale local snapshots,
  - fetch current live files first when repairing or merging production data,
  - keep raw history, queues, long-term cache, credentials, and logs outside the public web root.
- Enforce source-friendly crawling:
  - prefer official APIs, feeds, sitemaps, exports, or documented endpoints,
  - for authorized sources, support normal login, API, user-approved browser session, cookie/session reuse, or export flows when the user has the right to access the data,
  - do not unilaterally bypass paywalls, CAPTCHA, login checks, bot defenses, or rate limits; if one appears, stop development and discuss with the user first, guiding the user to justify access rights, purpose, risk, and an acceptable method before continuing,
  - handle source restrictions with cache, slot windows, batch limits, backoff, per-host throttling, and random sleep rather than uncontrolled retries,
  - add per-host random sleep/jitter; different URLs on the same host still share one throttle,
  - cap pages, batches, retries, and whole-run time.
- Make cron runs boring and recoverable:
  - one job instance at a time with a lock,
  - stamps for "already ran this slot/day" when cron wakes more often than the real job,
  - deterministic working directory and PATH,
  - private structured logs with retention,
  - non-zero exit on real failure,
  - success, no-op, expected defer, and lock skip exit cleanly without mail.
- Publish outputs safely:
  - write temp files in the same directory, validate, then atomic rename,
  - keep last-good or previous data for critical public outputs,
  - do not publish partial market/source batches as final output unless the page is designed for partial data,
  - after successful public data writes, refresh sitemap/robots or equivalent SEO indexes when the site uses them.
- Protect deploy-time cron injections:
  - when cron owns a `noscript`, SEO, or HTML marker region, fetch live HTML and merge that region before uploading a new static `index.html`,
  - make missing live HTML a deploy failure by default,
  - use emergency stale deploy flags only with a documented restore path,
  - combine with `static-deploy-refresh-check` when stale JS/CSS cache refresh is needed.
- Add failure-only notification:
  - send mail only when the crawler command exits non-zero or validation fails,
  - include job, slot, host, cwd, command label, status, timestamp, log path, and sanitized log tail,
  - do not include cookies, authorization headers, API keys, passwords, raw personal data, full tokens, or huge responses,
  - keep recipient/from settings in private server config or environment.

## Workflow

1. Inventory the real job.
   - List cron entry, wrapper, source URLs/APIs, source host groups, command flags, output files, logs, locks, stamps, queues, and docs.
   - Read `references/cron-job-patterns.md`.
2. Audit source access and request pacing.
   - Read `references/safe-crawling-policy.md`.
   - Add per-host throttle, randomized sleeps, bounded retries, and backoff.
   - Cache and reuse existing data; request only missing or stale data where possible.
3. Define data ownership before deploy changes.
   - Mark cron-owned public JSON/HTML, private runtime files, and build artifacts.
   - Exclude cron-owned data from static deploy packages unless explicitly doing a live-data migration from a current live baseline.
4. Harden crawler code.
   - Add request timeout on every network call.
   - Treat parse/schema changes as failure or degraded output, not empty success.
   - Validate minimum row counts, required keys, date monotonicity, and output schema before publishing.
   - Use queue/defer states when manual repair would conflict with an active or imminent cron run.
5. Harden the wrapper.
   - Use lock, slot/day stamp when needed, stable cwd/PATH, private log, log retention, and failure-only mail.
   - Use `scripts/write_cron_wrapper.py` only when the project lacks an existing wrapper pattern.
6. Protect HTML SEO regions.
   - Keep marker names stable.
   - Fetch live HTML before build packaging.
   - Merge live marker regions into the new index.
   - Keep visible data/news/post times behind `data-nosnippet`; static SEO and `noscript` should avoid real timestamps unless the page is truly an article.
7. Verify.
   - Run the crawler manually or in dry-run.
   - Test success path sends no mail.
   - Test failure path sends one sanitized mail.
   - Test lock skip and already-ran stamp send no mail.
   - Test deploy packaging refuses to overwrite missing live cron-managed HTML regions.
   - Re-read docs and changelog for consistency.

## Sakura Notes

- Sakura cron environments are minimal. Set PATH, `cd` explicitly, and avoid interactive shell assumptions.
- Keep private runtime data outside `www`, for example under an app data/job directory.
- Public JSON/HTML under `www` should be generated from validated private/runtime data, not treated as the only source of truth.
- Use Sakura `sendmail`/`mail` or the site's existing mail helper for alerts; do not store SMTP or mailbox passwords in the repository.
- For static deploys, upload new hashed assets before the new `index.html`. Clean old assets only after validation, keeping current and previous generations.

## Safety Rules

- Do not hardcode real domains, emails, account names, passwords, API keys, cookies, session tokens, or absolute private paths in reusable skill files.
- Do not collect credentials, personal data, private messages, or account-only content unless authorization is explicit and storage stays private.
- Do not unilaterally bypass paywalls, CAPTCHA, login controls, bot defenses, or source rate limits. When they appear, stop development and discuss the boundary with the user; require a clear justification before implementing any continuation path.
- Do not turn login/session handling into uncontrolled high-frequency access. Keep request pacing, cache reuse, batch limits, and retry limits in place even when the session is authorized.
- Do not publish raw scraped content wholesale when a summary, metadata, derived fact, or link is enough.
- Do not make high-frequency no-delay requests to the same host. Add random sleep and coordinate workers through a shared per-host throttle.
- Do not call a cron job healthy until failure, lock-skip, already-ran, validation, atomic-write, and deploy-overwrite paths are tested.
