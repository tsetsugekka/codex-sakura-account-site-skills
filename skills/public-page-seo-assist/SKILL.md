---
name: public-page-seo-assist
description: Improve SEO for public, indexable static or app pages. Use when Codex needs to add or audit Japanese SEO head tags, canonical URLs, Open Graph/Twitter cards, WebSite/WebApplication JSON-LD without article dates, visible or screen-reader summaries, noscript SEO fallback blocks, cron-updated static SEO regions, and Google-snippet-safe handling of data/news/post timestamps with data-nosnippet.
---

# Public Page SEO Assist

## Goal

Improve SEO for public pages without turning volatile app data into misleading Google publication dates.

Use this skill only for pages intended to be publicly indexable. For login-only, staff-only, or private pages, do not add indexable SEO fallback content; use `noindex` or the project's access-control pattern instead.

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
   - Twitter card,
   - `og:locale`,
   - `og:site_name`,
   - favicon/touch icon if the project has them,
   - `robots` only when appropriate.
4. Use structured data conservatively:
   - `WebSite` for the site top page,
   - `WebApplication` for interactive tools,
   - `SoftwareApplication` only when that is a better fit for the product,
   - no `datePublished`, `dateModified`, or article-style dates unless the page is genuinely an article.
5. Add crawlable body context:
   - one real or screen-reader-only `<h1>`,
   - a concise static summary near the app root when useful,
   - a `<noscript>` fallback that explains the page and major entities/search intents.
6. If cron/server scripts update SEO fallback content, add stable marker comments around only that managed region and document ownership in the updater.
7. If the page displays data update times, news times, X/SNS post times, generated-at times, or reviewed/updated labels, apply the time-snippet rules in `references/time-snippet-safety.md`.
8. If the entry HTML is deployed statically and also has cron-managed HTML regions, combine this skill with `static-deploy-refresh-check` so live `<noscript>` regions are fetched and merged before publishing.
9. Verify:
   - built HTML contains one title, one canonical when applicable, and expected meta cards,
   - JSON-LD parses as valid JSON and has no article date fields unless intentionally article-like,
   - `<noscript>` contains useful public text but no real timestamps,
   - visible UI timestamps that may be indexed use `data-nosnippet`,
   - cron-managed markers remain intact after build/deploy preparation.

## Required References

- Read `references/public-page-seo-patterns.md` before adding or restructuring SEO head/body fallback.
- Read `references/time-snippet-safety.md` whenever the page has update times, post times, news times, generated-at labels, or reviewed/updated states.

## Public Page Pattern

Prefer this shape for static app entry HTML:

```html
<title>Primary keyword / product name - concise value</title>
<link rel="canonical" href="https://example.com/tool/" />
<meta name="description" content="Human-written page summary with main search intents.">
<meta name="robots" content="index, follow">

<meta property="og:type" content="website">
<meta property="og:title" content="Share card title">
<meta property="og:description" content="Share card description.">
<meta property="og:locale" content="ja_JP">
<meta property="og:site_name" content="Site Name">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Share card title">
<meta name="twitter:description" content="Share card description.">
```

Use a `summary_large_image` Twitter card only when the page has a stable, high-quality preview image that is safe to expose.

## Noscript Pattern

For JavaScript-heavy public tools, include a real fallback:

```html
<noscript>
  <section style="text-align:left;max-width:860px;margin:2rem auto;padding:0 1rem;line-height:1.7;">
    <!-- TOOL_STATIC_SEO_START -->
    <h2>Tool name and search intent</h2>
    <p>Stable public explanation of what this page shows and who it helps.</p>
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
