---
name: public-page-seo-assist
description: Use when improving or auditing SEO for public indexable Sakura-hosted static pages, JavaScript app entry pages, dashboard/tool pages, or cron-updated pages with volatile timestamps.
---

# Public Page SEO Assist

## Goal

Improve SEO for public pages without turning volatile app data into misleading Google publication dates.

Use this skill only for pages intended to be publicly indexable. For login-only, staff-only, or private pages, do not add indexable SEO fallback content; use `noindex` or the project's access-control pattern instead.

This skill should align four public signals before considering the work complete:

- page `<head>` canonical URL,
- Open Graph `og:url`,
- `sitemap.xml` `<loc>`,
- the actual final public URL after redirects, trailing-slash handling, and extensionless aliases.

Do not add `og:image` just to fill a checklist. A missing social image is better than a tiny favicon, stale screenshot, relative path, private asset, or low-quality preview.

## Workflow

1. Confirm the page is public:
   - route is not behind login,
   - robots policy should be `index, follow`,
   - page content is safe to expose in static HTML and search snippets.
2. Inspect existing head tags, route aliases, build/deploy flow, and whether cron or server scripts write live data into the entry HTML.
3. Add or repair the page-level SEO package:
   - stable `<title>`,
   - `<meta name="description">`,
   - canonical URL,
   - Open Graph card,
   - `og:url` matching the canonical URL,
   - Twitter card,
   - `og:locale`,
   - `og:site_name`,
   - favicon/touch icon if the project has them,
   - `robots` only when appropriate.
4. Decide whether the page should have `og:image`:
   - add it only for a stable, high-quality, public, absolute URL image,
   - do not use favicon or small icon files as the fallback social image,
   - remove old relative or weak `og:image` / `twitter:image` tags when they create a worse preview than no image.
5. Use structured data conservatively:
   - `WebSite` for the site top page,
   - `WebApplication` for interactive tools,
   - `SoftwareApplication` only when that is a better fit for the product,
   - no `datePublished`, `dateModified`, or article-style dates unless the page is genuinely an article.
6. Add crawlable body context:
   - one real or screen-reader-only `<h1>`,
   - a concise static summary near the app root when useful,
   - a `<noscript>` fallback that explains the page and major entities/search intents.
7. If cron/server scripts update SEO fallback content, add stable marker comments around only that managed region and document ownership in the updater.
8. If the page displays data update times, news times, X/SNS post times, generated-at times, or reviewed/updated labels, apply the time-snippet rules in `references/time-snippet-safety.md`.
9. Repair sitemap coverage:
   - include every public indexable route that should be discoverable,
   - make each `<loc>` match the canonical URL and `og:url`,
   - use the final route form, such as trailing slash for directory pages and extensionless URL when that is the public route,
   - generate `sitemap.xml` during deploy when daily data pages need fresh `<lastmod>`,
   - use source/content mtime or a conservative date for static tool pages and non-news pages.
10. If the entry HTML is deployed statically and also has cron-managed HTML regions, combine this skill with `static-deploy-refresh-check` so live `<noscript>` regions are fetched and merged before publishing.
11. Verify:
   - built HTML contains one title, one canonical when applicable, and expected meta cards,
   - canonical, `og:url`, and sitemap `<loc>` match the final public URL,
   - `og:image` is absent unless a real preview image passes the quality/stability check,
   - JSON-LD parses as valid JSON and has no article date fields unless intentionally article-like,
   - `<noscript>` contains useful public text but no real timestamps,
   - visible UI timestamps that may be indexed use `data-nosnippet`,
   - cron-managed markers remain intact after build/deploy preparation,
   - deploy manifests upload generated `robots.txt` and `sitemap.xml` when the project owns those files.

## Required References

- Read `references/public-page-seo-patterns.md` before adding or restructuring SEO head/body fallback.
- Read `references/time-snippet-safety.md` whenever the page has update times, post times, news times, generated-at labels, or reviewed/updated states.

## Public Page Pattern

Prefer this shape for static app entry HTML:

```html
<title>PTS急騰株分析 - 上昇理由をAI分析</title>
<link rel="canonical" href="https://example.com/pts/" />
<meta name="description" content="PTSで急騰した銘柄の材料、テーマ、出来高変化を整理し、翌営業日の注目点を確認できます。">
<meta name="robots" content="index, follow">

<meta property="og:type" content="website">
<meta property="og:title" content="PTS急騰株分析">
<meta property="og:description" content="PTSで動いた銘柄の材料と市場テーマを整理します。">
<meta property="og:url" content="https://example.com/pts/">
<meta property="og:locale" content="ja_JP">
<meta property="og:site_name" content="Example Market Tools">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="PTS急騰株分析">
<meta name="twitter:description" content="PTSで動いた銘柄の材料と市場テーマを整理します。">
```

Use a `summary_large_image` Twitter card only when the page has a stable, high-quality preview image that is safe to expose. If the only available asset is a favicon, app icon, generated placeholder, or visually weak screenshot, leave `og:image` and `twitter:image` out.

## Sitemap / Canonical Pattern

When the project owns `sitemap.xml`, keep URL signals consistent:

```xml
<url>
  <loc>https://example.com/pts/</loc>
  <lastmod>2026-07-09</lastmod>
  <changefreq>daily</changefreq>
</url>
```

Rules:

- Use the same final URL as the page canonical and `og:url`.
- For daily-updated data pages, generate `<lastmod>` at deploy time instead of committing a stale static date.
- For stable tools or non-news pages, use the file/content update date and a conservative `changefreq`.
- `lastmod` in sitemap is allowed metadata; it is not the same as article/date markup in HTML.
- Include generated `sitemap.xml` and `robots.txt` in the deploy upload manifest when the site root owns them.

## Noscript Pattern

For JavaScript-heavy public tools, include a real fallback:

```html
<noscript>
  <section style="text-align:left;max-width:860px;margin:2rem auto;padding:0 1rem;line-height:1.7;">
    <!-- TOOL_STATIC_SEO_START -->
    <h2>ツール名と主要な検索意図</h2>
    <p>このページで確認できる情報、対象市場、対象ユーザーを自然な文章で説明する。</p>
    <!-- TOOL_STATIC_SEO_END -->
  </section>
</noscript>
```

Rules:

- Keep the marker names unique per page.
- Let cron update only the region between markers.
- Make fallback content consistent with what users can see in the live UI.
- Do not add hidden keyword stuffing.
- Do not put private, paid, draft, or login-only details into `noscript`.
- Do not put real dates or times in static SEO fallback.

## Safety Rules

- Do not make a private page indexable.
- Do not add article structured data to tools, dashboards, feeds, or admin pages.
- Do not use `<time datetime>`, `datePublished`, or `dateModified` for volatile data unless the page is truly an article page.
- Do not write real timestamps into `<noscript>`, static summaries, SEO fallback, JSON-LD, or HTML comments.
- Do not use HTML comments as daily SEO refresh stamps; use a server-side stamp file instead.
- Do not overwrite live cron-managed SEO blocks during deploy; merge from the current live HTML first.
