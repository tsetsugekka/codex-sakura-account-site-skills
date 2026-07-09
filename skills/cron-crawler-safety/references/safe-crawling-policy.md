# Safe Crawling Policy

Use this reference when deciding whether and how a scheduled crawler should fetch external pages or APIs.

## Preferred Source Order

1. Official API, export, or feed.
2. Public RSS/Atom, sitemap, static JSON, or documented endpoint.
3. Public HTML pages that are intended for indexing and do not require special access.
4. Browser automation only as a rendering tool for content the user is authorized to access.

For authenticated data, use a normal authorized API, login session, browser profile, user-approved cookie/session, or manual export flow. Keep credentials and session files private and out of logs. Do not unilaterally bypass paywalls, CAPTCHA, login checks, bot defenses, or rate limits. If one appears, stop development and discuss with the user first; guide the user to justify access rights, purpose, risk, and the acceptable method before continuing. Treat source restrictions operationally with cache reuse, slot windows, batch limits, backoff, per-host throttling, and random sleep.

## Preflight Checklist

- Check published API policy, robots.txt, or source guidance when applicable.
- Confirm the user owns or is authorized to access the data.
- Set a clear User-Agent where appropriate.
- Deduplicate URLs before fetching.
- Cap pages, batches, source groups, and per-run request counts.
- Enforce per-host pacing even when URLs differ.
- Add randomized sleep/jitter before requests to the same host, including the first request in a batch when the job wakes on a predictable cron minute.
- Route concurrent workers through a shared per-host throttle.
- Cache results and request only missing/stale data.
- Prefer conditional requests with `If-None-Match` / `If-Modified-Since` when supported.

## Rate and Retry Defaults

Use slow defaults unless the source publishes different limits:

- HTML pages: seconds between requests to the same host, not many requests per second. A low-volume public HTML crawler can start around 3-10 seconds random sleep; use slower ranges for fragile sources.
- Same-host mixed sources: page fetch, fallback fetch, and retry still share the same delay.
- APIs: follow documented limits; include backoff on `429`, `503`, network timeout, or reset.
- Retries: 1-3 max for transient failures.
- Timeout: set connect/read timeout for every request.
- Batches: split large universes into small daily/hourly batches. For enrichment APIs, fetch only missing cache entries.
- Failure stop: after repeated transient failure on an enrichment source, stop further batches for that run and keep stale cache instead of continuing to hammer the source.

Never retry parse errors aggressively. A parse error usually means the page changed; fail safely, keep previous good output, and alert.

## Practical Throttle Patterns

Use one of these shapes:

```python
last_by_host = {}

def wait_for_host(url, min_seconds=3, max_seconds=10):
    host = urllib.parse.urlparse(url).netloc
    if not host:
        return
    now = time.monotonic()
    target_gap = random.uniform(min_seconds, max_seconds)
    last = last_by_host.get(host)
    if last is not None and now - last < target_gap:
        time.sleep(target_gap - (now - last))
    last_by_host[host] = time.monotonic()
```

For batch quote/API jobs, sleep between batches rather than between every item when the API is designed for batched symbols. For single-page HTML scraping, sleep before each page fetch.

## Cache-First Enrichment

For optional enrichment, such as industry labels, quotes, summaries, or translated fields:

- merge existing server cache first,
- request only missing or invalid cached values,
- keep a hard batch cap,
- write cache atomically after successful enrichment,
- let the primary page update continue when enrichment fails,
- mark missing values as unknown/uncategorized rather than failing the whole page when that is acceptable.

## Content and Privacy

- Store only fields the site needs.
- Keep raw captures private and time-limited.
- Avoid republishing large copied text. Use metadata, links, short summaries, translated snippets, or derived facts when sufficient.
- Remove or hash direct personal identifiers when not essential.
- Keep cookies, auth headers, API tokens, session files, and browser profiles out of the repository and alert logs.

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
- schedule says no run needed,
- already-ran stamp exists,
- rate-limit or cron-window policy asks the job to defer and the job records a queue/deferred state.
