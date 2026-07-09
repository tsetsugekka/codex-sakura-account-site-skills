# Safe Crawling Policy

Use this reference when deciding whether and how a scheduled crawler should fetch external pages or APIs.

## Preferred Source Order

1. Official API, export, or feed.
2. Public RSS/Atom, sitemap, static JSON, or documented endpoint.
3. Public HTML pages that are intended for indexing and do not require login.
4. Browser automation only when the source permits it and no simpler source exists.

Do not treat browser automation as a way around access controls. It is a last-mile rendering tool, not a permission bypass.

## Preflight Checklist

- Check robots.txt or published developer/API policy when applicable.
- Confirm the target content is public and does not require login, payment, invitation, or private cookies unless the user owns or is authorized to access it.
- Confirm the crawler does not bypass CAPTCHA, bot checks, rate limits, geo restrictions, or paywalls.
- Set an honest User-Agent, for example `ExampleSiteBot/1.0 (+https://example.com/contact)`.
- Use a conservative interval and cap per-run fetch count.
- Cache results and avoid refetching unchanged resources.
- Prefer conditional requests with `If-None-Match` / `If-Modified-Since` when the source supports them.

## Rate and Retry Defaults

Use slow defaults unless the source publishes different limits:

- HTML pages: seconds between requests, not many requests per second.
- APIs: follow documented limits and include backoff on `429`, `503`, network timeout, or reset.
- Retry count: 2 or 3 max for transient failures.
- Timeout: set connect and read timeout for every request.
- Jitter: add small random delay for multi-source jobs so cron does not hit all sources at once.

Never retry parse errors aggressively. A parse error usually means the page changed; fail safely and keep the previous good output.

## Content and Privacy

- Store only the fields the site actually needs.
- Avoid saving full raw HTML unless needed for debugging, and keep debug captures private and time-limited.
- Avoid republishing large copied text. Use metadata, links, short summaries, or derived facts when possible.
- Remove or hash direct personal identifiers when they are not essential.
- Keep cookies, auth headers, API tokens, session files, and browser profiles out of the repository and logs.

## Failure Classification

Treat these as real failures:

- source unavailable after bounded retries,
- schema or parse change,
- output row count unexpectedly drops to zero,
- required fields missing,
- generated timestamp goes backward unexpectedly,
- output validation fails,
- atomic write or permission failure.

Treat these as normal no-op/skip, not alert-worthy:

- lock already held by another active run,
- source says not modified,
- market/source schedule says no run needed,
- rate-limit window asks the job to defer and the job records a queue/deferred state.
