# Public Page SEO Patterns

Use this reference when adding SEO to a public static page, Vite app, or JavaScript-heavy tool page.

## Baseline Head Package

Every public page should have:

- `lang` on `<html>`, usually `ja` for Japanese pages.
- One stable `<title>`.
- One concise `meta description` written for humans.
- `robots: index, follow` only when the page should be indexed.
- One canonical URL for the public route.
- Open Graph metadata:
  - `og:type: website` for normal pages and tools.
  - `og:title`.
  - `og:description`.
  - `og:locale`, usually `ja_JP`.
  - `og:site_name`.
  - `og:url` matching the canonical URL.
- Twitter card metadata:
  - `twitter:card`, usually `summary`.
  - `twitter:title`.
  - `twitter:description`.
- Favicons/touch icons matching the project.

Keep titles stable. Use body text and `noscript` for secondary search intents rather than stuffing the title with every keyword.

## URL Signal Consistency

For public indexable pages, these signals should point to the same final URL:

- `<link rel="canonical" href="...">`
- `<meta property="og:url" content="...">`
- `sitemap.xml` `<loc>`
- the final public route after redirects and route normalization

Use the route that users and crawlers should keep:

- directory pages usually end with `/`,
- extensionless public aliases should stay extensionless if that is the canonical route,
- avoid mixing `/tool`, `/tool/`, `/tool/index.html`, and redirected variants.

When fixing many pages, add a small verification script that reads source and built/deploy output instead of relying on manual inspection.

## Sitemap Ownership

If the project owns `sitemap.xml`, keep it complete and generated from the deploy/build source of truth:

- include every public indexable page that should be discoverable,
- exclude login-only, staff-only, private, draft, or `noindex` pages,
- make `<loc>` match canonical and `og:url`,
- use deploy-time `<lastmod>` for pages whose public data refreshes daily,
- use source/content mtime or a conservative date for static tools and non-news pages,
- include generated `robots.txt` and `sitemap.xml` in the upload manifest when publishing to Sakura.

Do not commit hardcoded daily dates that will become stale. Generating sitemap metadata during deploy is safer for sites with cron-refreshed pages.

## Structured Data Choices

Use JSON-LD only when it improves clarity and stays truthful:

- Top page: `WebSite` with `name`, optional `alternateName`, and `url`.
- Interactive public tool: `WebApplication` with `name`, `description`, `applicationCategory`, `operatingSystem`, `inLanguage`, `url`, `author`, and optional free `Offer`.
- Avoid `Article`, `NewsArticle`, `BlogPosting`, or article date fields for dashboards, market tools, feeds, ranking pages, account systems, admin screens, or continuously updated app pages.

Do not add:

```json
"datePublished": "...",
"dateModified": "..."
```

unless the page is actually a dated article and the user wants Google to understand that date.

## Crawlable Body Context

JavaScript-heavy apps often start with an empty root. Add enough static body context so crawlers and no-JavaScript clients can understand the page:

- one `<h1>` visible or `sr-only`,
- one or two stable summary paragraphs,
- a `noscript` fallback with the page purpose, important domains/entities, and natural search intents.

For app pages with visible UI, prefer a screen-reader-only summary over large duplicate intro text if the visible product surface should stay dense.

## Noscript Static SEO

Use `noscript` for stable, public, crawlable fallback:

```html
<noscript>
  <section style="text-align:left;max-width:860px;margin:2rem auto;padding:0 1rem;line-height:1.7;">
    <!-- PAGE_STATIC_SEO_START -->
    <h2>ページ名と主要な検索意図</h2>
    <p>このページで確認できる情報、対象市場、対象ユーザーを自然な文章で説明する。</p>
    <!-- PAGE_STATIC_SEO_END -->
  </section>
</noscript>
```

Use page-specific marker names such as:

- `HOME_NEWS_STATIC_SEO_START` / `HOME_NEWS_STATIC_SEO_END`
- `PTS_STATIC_SEO_START` / `PTS_STATIC_SEO_END`
- `FEED24_STATIC_SEO_START` / `FEED24_STATIC_SEO_END`

Marker rules:

- Keep markers stable once deployed.
- Put only one managed region in each marker pair unless the deploy script explicitly supports more.
- Cron/server scripts may replace only the marked region.
- Deploy scripts must fetch the current live HTML and merge the marked region before uploading a new `index.html`.
- If the marker is missing or duplicated, stop instead of overwriting live content.

## Dynamic SEO Fallback Content

When a cron job refreshes `noscript`, content must come from the same public data the page displays. Good examples:

- ranking names and short public reasons from the visible ranking page,
- market narrative summaries that also appear in the UI,
- category labels and public summaries.

Avoid:

- raw private cache fields,
- paid/pro-only content,
- internal crawler diagnostics,
- exact publication/update timestamps,
- unrelated keyword lists.

For ranking or feed history, prefer relative batches rather than dates:

- Good: `T-1 日中取引`, `T-2 夜間取引`, `最新市場ナラティブ`.
- Avoid: `2026/07/07 12:00 更新`, `07/07 12:00`, `Reviewed 2026-07-07`.

## Sharing Cards

Open Graph and Twitter cards are for social/link previews, not the full SEO body. Keep them concise and stable:

```html
<meta property="og:type" content="website">
<meta property="og:title" content="24時間出来事 - 市場ナラティブ速報">
<meta property="og:description" content="主要Xアカウントの市場関連発言を追跡し、重要な市場ナラティブを整理します。">
<meta property="og:url" content="https://example.com/tools/24hfeed/">
<meta name="twitter:card" content="summary">
```

Use `og:image`, `twitter:image`, and `summary_large_image` only when:

- a stable image exists,
- the URL is absolute,
- the image is public,
- the image is large and clear enough for a social card,
- the image will not expose private data or old market timestamps.

Do not force a social image from:

- favicon files,
- tiny app icons,
- placeholder images,
- relative paths,
- stale screenshots,
- images that make the page look less trustworthy than no image.

## Verification Checklist

Before finishing:

- Inspect source and built HTML.
- Confirm no duplicate `<title>`, canonical, or conflicting robots tags.
- Confirm canonical, `og:url`, sitemap `<loc>`, and final public URL match.
- Confirm public sitemap coverage includes the intended indexable pages and excludes private/noindex pages.
- Confirm `og:image` is absent unless a real stable preview image passes the sharing-card checks.
- Validate JSON-LD as JSON.
- Search for real date/time patterns in static SEO regions:
  - `YYYY/MM/DD`
  - `YYYY-MM-DD`
  - `MM/DD HH:mm`
  - `更新日時`
  - `Reviewed`
  - `Updated`
  - `最終チェック`
- Confirm visible time UI uses `data-nosnippet` when the time is data/news/post freshness rather than page publication.
- Confirm deploy scripts preserve cron-managed SEO markers.
