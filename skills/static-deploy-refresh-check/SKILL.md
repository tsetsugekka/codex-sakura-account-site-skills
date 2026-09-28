---
name: static-deploy-refresh-check
description: Diagnose and fix stale static HTML or JS/CSS after deployment. Use for static or Vite-built pages when configuring HTTP cache headers, verifying published assets, optionally retaining an existing startup refresh check, or protecting live generated content during deploy and asset cleanup.
---

# サイト更新後に古い画面が残るキャッシュ問題を防ぐ

## Start with the published responses

Read the site's source, build, server configuration, service worker (if any), and deploy flow. Separate entry HTML, fingerprinted JS/CSS, fixed-name files, generated data, and authenticated responses. Check real HTTP GET/HEAD response headers, including compressed variants; HTML `http-equiv` meta tags do not set the HTTP cache policy. Legacy meta tags may remain for compatibility, but do not rely on or newly inject them as the cache guarantee.

Use two HTTP cache layers:

- Entry HTML and aliases: return `Cache-Control: no-cache` so browsers revalidate before reuse. Keep working validators such as `ETag` or `Last-Modified` where supported; a valid `304` may reuse the stored body. Configure the actual server/CDN response, not only the HTML source.
- Fingerprinted JS/CSS: after verifying the filename changes whenever its bytes change, return `Cache-Control: public, max-age=31536000, immutable` for those URLs. Upload the new assets before changing the HTML references. Scope the rule to the build's fingerprinted files or manifest, not every `.js`/`.css` file.

Do not apply `immutable` to fixed-name assets, HTML, JSON/data/API responses, auth or account pages, or files whose content can change at the same URL. Give those resources their own cache policy under the site's contract. Do not solve stale HTML by making all content `no-store` or adding a random query parameter on every visit. Verify the actual header and returned body for a direct URL and normal navigation after deployment. See [the HTTP and deploy checks](references/deploy-refresh-pattern.md) when configuring or validating a site.

## Optional check for an already loaded page

HTTP revalidation handles the next navigation. If the site already uses a startup asset check, or the requested behavior includes a one-time check shortly after page load, keep one equivalent mechanism. It is optional; do not inject a second check into a site that already has one. It does not monitor an open tab continuously or detect changes to HTML body/data at unchanged asset URLs.

The bundled [injector](scripts/inject_deploy_refresh.py) adds one inline check to entry HTML. It revalidates the originally loaded document URL with `fetch(..., {cache: 'no-cache'})`, compares same-origin JS/CSS references, and attempts at most one reload per target signature and original route/query. It skips automatic reload after interaction, after programmatic navigation to another route, while an edit control is active, when the tab is hidden, or when `sessionStorage` cannot guard the attempt. It does not poll or add UI. A successful reload removes `__deploy_v` from the visible URL. Existing `DEPLOY_REFRESH_CHECK_V1` markup is left intact by the injector; update its authoritative template/generator when changing that installed script.

Prefer changing the source template or deploy-preparation step so rebuilding preserves the check. For direct HTML, dry-run before `--write`; include extensionless aliases only when they are HTML:

```bash
python3 skills/static-deploy-refresh-check/scripts/inject_deploy_refresh.py --include-extensionless path/to/page/index.html path/to/page/alias
python3 skills/static-deploy-refresh-check/scripts/inject_deploy_refresh.py --write --include-extensionless path/to/page/index.html path/to/page/alias
```

## Publish without overwriting live state

- Stage from the authoritative source/generator and upload by whitelist: new fingerprinted assets first, entry HTML and aliases last. Include only approved static extras. Exclude live JSON/data, account snapshots, server caches, credentials, and internal maintenance files.
- For cron/server-managed HTML regions, fetch the current live HTML, merge the marked regions into the new entry, and stop if markers are missing or ambiguous. Do not overwrite them with a stale local build.
- Verify live HTML, JS/CSS URLs and bodies, gzip/Brotli counterparts where used, protected regions, and data separately. A successful build or upload does not prove the public response changed; verify the next normal generation path when automation owns the output.
- Scope asset cleanup to the page's own asset directory. Keep the complete current and immediately previous deploy generations, plus assets still needed by every live entry, alias, independent detail page, and permanent archived HTML, including imported chunks. Review a dry-run list and delete only identified older fingerprinted assets. Missing HTML/assets, incomplete reference or dependency enumeration, or uncertain generations must stop cleanup. Never include shared files or production data.

For deployment-script details, aliases, HTTP verification, and cleanup boundaries, read [the reference](references/deploy-refresh-pattern.md).
