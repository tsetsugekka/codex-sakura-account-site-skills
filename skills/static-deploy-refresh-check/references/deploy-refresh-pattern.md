# Deploy Refresh Pattern

## What the script does

The deploy refresh script solves the stale-entry problem common to static sites with hashed assets:

1. A visitor has an old `index.html` in the browser.
2. A deploy uploads new hashed JS/CSS and then a new `index.html`.
3. The old page is still running and may continue displaying old styles.
4. The inline check fetches the live entry HTML with `cache: no-store`.
5. It extracts same-origin JS/CSS URLs from both documents.
6. If the signatures differ, it reloads once with a query parameter such as `__deploy_v=<hash>`.

This is not a replacement for hashed filenames. It is a bridge that helps already-open or stale pages move to the latest entry HTML.

## HTML metadata

Entry HTML should include:

```html
<meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
```

Use HTML revalidation as the default. Avoid `no-store` as the broad page policy because it disables useful caching even when a page has not changed.

## Injection point

Inject before `</head>` and make the injection idempotent:

```js
function injectDeployRefreshCheck(html) {
  const marker = '<!-- DEPLOY_REFRESH_CHECK_V1 -->';
  if (html.includes(marker)) return html;
  if (!/<\/head>/i.test(html)) return html;
  return html.replace(/<\/head>/i, `${DEPLOY_REFRESH_SNIPPET}\n</head>`);
}
```

Prefer patching the deploy-preparation script so generated deploy packages always include the snippet. Direct HTML injection is acceptable for simple static pages without a build step.

## Alias pages

If a deploy helper generates route aliases such as extensionless files, inject the refresh check into aliases too. The checker should fetch:

- `pathname + "index.html"` when the URL path ends with `/`,
- the current path itself for extensionless aliases.

This lets `/section/` and `/section/topic` both compare the correct live entry HTML.

## Asset signature

Compare only same-origin JavaScript and stylesheet URLs:

```js
document.querySelectorAll('script[src],link[rel~="stylesheet"][href]')
```

Normalize each URL to `pathname + search`, ignore cross-origin URLs, sort, and join with `|`. Do not include third-party analytics, fonts, or CDN files in the signature.

## One-time reload guard

Use `sessionStorage` keyed by the current path. Save the target version before reloading:

```js
sessionStorage.setItem('deploy-refresh:' + location.pathname, version);
```

If the same version was already attempted, do not reload again. This prevents loops when a proxy or server returns unexpected HTML.

## Publish order

Upload in this order:

1. new hashed `assets/*`,
2. any static non-data files,
3. route aliases if used,
4. `index.html` last.

After verifying the live page, clean old hashed assets only with a retention rule that keeps the current generation and one previous generation. Never clean production JSON or scraper/cron data as part of this skill.

## Sakura asset retention

For Sakura static hosting, keep remote storage bounded without breaking rollback:

1. Work one page at a time, scoped to that page's `assets/` directory.
2. Read the current live entry HTML and collect the asset filenames it references.
3. List remote asset files with timestamps, sizes, and names.
4. Identify the current deploy generation from the live HTML references.
5. Identify the immediately previous deploy generation by timestamp cluster or a saved manifest.
6. Dry-run deletion of all older hashed assets.
7. Apply only if the delete list contains older assets from that page's `assets/` directory.
8. Run a follow-up dry-run and expect no remaining delete candidates.

Do not delete:

- assets referenced by current live HTML,
- the previous generation kept for rollback,
- production JSON, server cache files, cron output, or account/data directories,
- shared files outside the page's asset directory.

## Protected live data

Deploy packages should be whitelist based. Exclude live server outputs unless the task explicitly asks to recover or migrate those files from a trusted live baseline.

Common protected examples:

- `data.json`,
- `news.json`,
- per-day data folders,
- account snapshots,
- generated narrative/status JSON,
- server cache files,
- market history files,
- cron-generated public data.

If a frontend build emits local mock JSON into `dist/`, do not upload it by default.

## Cron-managed HTML regions

Some projects let cron or server scripts inject content into entry HTML. Examples include static SEO `<noscript>` blocks, generated rankings, latest-run summaries, and timestamps. Publishing a local build can silently erase those live updates if Codex uploads local `index.html` directly.

Use a merge-before-publish flow:

1. Locate stable markers for server-managed regions, such as `<!-- STATIC_SEO_START -->` and `<!-- STATIC_SEO_END -->`.
2. Fetch the current live HTML from Sakura before preparing the final deploy HTML.
3. Extract marked regions from live HTML.
4. Replace the corresponding regions in the new deploy HTML.
5. Preserve or inject the deploy refresh check after the merge.
6. Abort if the live marker exists but the local marker is missing, or if either boundary is ambiguous.

This keeps new UI assets and styles while preserving server-generated content.

## Service workers

If a project has a service worker, first check whether it intercepts entry HTML or asset requests. Do not add broad service worker changes unless the stale-style issue is proven to involve the service worker.
