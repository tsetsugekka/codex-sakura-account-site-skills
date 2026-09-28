# Static deploy cache and refresh pattern

## HTTP contract and verification

Set cache headers in the server/CDN rule that serves each response. HTML `http-equiv` tags cannot prove the response policy. Match only known fingerprinted JS/CSS from the build manifest or a verified filename pattern; a blanket extension rule also catches mutable fixed-name files. Keep data, API, authenticated content, and server-generated files on their own policies.

| Response | Expected `Cache-Control` | Reason |
| --- | --- | --- |
| Entry HTML and HTML aliases | `no-cache` | Revalidate before reusing stored HTML; validators can yield `304`. |
| Verified fingerprinted JS/CSS | `public, max-age=31536000, immutable` | A changed file gets a different URL. |
| Fixed-name assets, data, API, auth | Site-specific | They are not eligible for the fingerprint rule. |

Inspect real GET or HEAD responses for representative direct URLs, including gzip/Brotli responses and an alias. If the server provides an `ETag` or `Last-Modified`, repeat with `If-None-Match` or `If-Modified-Since` and confirm the conditional response is valid; a `304` has no new body. Then fetch normally and confirm the HTML references the uploaded asset names and the body/other data is current. Query-busted requests alone do not test ordinary cache behavior. If a service worker intercepts navigation or assets, inspect its cache policy before changing it.

## Optional startup check

Use the bundled injector only when a one-time check for an already loaded static page is part of the site's behavior. Add it in the source template or deploy-preparation stage before `</head>`; include aliases only if the server actually serves them as HTML. The default marker `<!-- DEPLOY_REFRESH_CHECK_V1 -->` makes insertion idempotent. Already marked pages are not rewritten, so update an older embedded check in its authoritative template/generator and avoid parallel checks.

The check uses the original navigation URL, not a later `pushState` alias. It removes its own version parameter before revalidating with `fetch` cache mode `no-cache`, allowing a conditional request and a `304`-backed browser body. It compares same-origin script and stylesheet URLs, ignoring third-party files. On a change it reloads once with `__deploy_v=<short-hash>`, then removes that visible parameter with `history.replaceState`. Before reload it confirms the current URL still matches the original route and business query after ignoring the deploy parameter and hash. `sessionStorage` records each target signature separately for that route/query, so alternating responses cannot trigger repeated reloads. If the user has interacted, an edit control is active, the tab is hidden, or storage fails, it leaves the page alone. It never retries on a timer or adds an update prompt. The check does not detect changed file contents at a fixed URL, body-only updates, or JSON changes.

## Staging, merge, and retention

Upload new fingerprinted assets before HTML/aliases. Keep deployment whitelists explicit; local mock JSON and generated `dist/` data are not automatically publishable. Do not include live data, credentials, account files, or internal documentation. Regenerate compressed HTML/assets with their source and inspect the response actually served.

If cron or server scripts own marked HTML regions (for example SEO text or latest-run summaries), fetch the current live HTML immediately before staging, copy those regions into the new HTML, and stop on absent or ambiguous markers. Do not overwrite live-owned regions from an old local template.

After confirming the new live HTML and assets, scope cleanup to that page's asset directory. Enumerate every still-live HTML owner of that directory: main entry, independent entry/detail templates, route aliases, and permanent archived detail pages, including older pages that are not rebuilt by a routine deploy. Read their current server copies or a trusted complete manifest. Keep the complete current and immediately previous deploy generations, then add every asset still reachable from those HTML references, including imported JS/CSS chunks identified through the build manifest or equivalent dependency evidence. Review a dry-run delete list and delete only identified older fingerprinted assets outside that keep set. If an HTML owner or referenced asset is missing, a dependency graph is incomplete, or generations cannot be identified reliably, stop cleanup. Never include JSON, caches, cron output, account data, or shared assets in cleanup.
