# Time Snippet Safety

Use this reference whenever a public page displays data update times, post times, news times, generated-at times, reviewed/updated labels, or other volatile timestamps.

## Principle

A page may show data time to users, but Google snippets should not read those times as the page's publication date.

Handle this in two layers:

1. Static SEO and `noscript` must not contain real dates or times.
2. Visible UI timestamps must use `data-nosnippet`.

## Static SEO Must Not Include Real Time

Do not write real timestamps into:

- `<noscript>`,
- static summaries,
- SEO fallback text,
- screen-reader SEO summaries,
- JSON-LD,
- HTML comments.

Avoid text patterns such as:

```html
2026/07/07
2026-07-07
07/07 12:00
更新日時: 2026/07/07 12:00
Reviewed 2026-07-07
Updated 2026-07-07
最終チェック: 2026/07/07
<!-- PAGE_STATIC_SEO_DATE: 2026-07-07 -->
```

If a cron job needs daily refresh throttling, use a server-side stamp file, for example `.page_static_seo_stamp`, not an HTML comment.

## Visible UI Time Uses Data Nosnippet

Users can still see timestamps. Wrap them with `data-nosnippet`:

```html
<span data-nosnippet>更新日時: 2026/07/07 12:00</span>
```

For React or JSX:

```tsx
<span data-nosnippet>{formatUpdatedAt(updatedAt)}</span>
```

Apply this to:

- top-page update time,
- data update time,
- news publication time,
- X/SNS post time,
- quoted content time,
- generated-at time,
- reviewed/updated/final-check status time,
- any small timestamp in ranking cards, comments, news lists, or feed items.

If a parent row is entirely timestamp/status metadata, `data-nosnippet` can be placed on the parent element.

## Do Not Use Structured Page Date Fields

Unless the page is genuinely an article, do not add:

- `<time datetime="...">`
- `datePublished`
- `dateModified`
- JSON-LD date fields
- article/news/blog schema types

For dashboards, tools, feeds, rankings, and app pages, use `WebApplication` or `WebSite` without page date fields.

## Sitemap Lastmod Is Separate

`sitemap.xml` `<lastmod>` is allowed when it truthfully describes when the page content changed. It is not the same as `datePublished`, `dateModified`, `<time datetime>`, or article markup inside HTML.

Use it carefully:

- daily-updated public data pages can generate today's deploy date as `<lastmod>`,
- static tools and non-news pages should use source/content mtime or a conservative update date,
- avoid committing hardcoded daily `<lastmod>` values that will become stale,
- keep real dates out of `noscript`, static SEO body text, JSON-LD, and HTML comments even when sitemap uses `<lastmod>`.

## Use Relative Batches In SEO Text

Static SEO can describe freshness without dates:

- Good: `T-1 日中取引`
- Good: `T-2 夜間取引`
- Good: `最新市場ナラティブ`
- Good: `直近の注目銘柄`
- Avoid: `07/07 12:00 更新`
- Avoid: `2026年7月7日のランキング`

This keeps search snippets focused on page purpose and public content rather than stale-looking data timestamps.

## Audit Commands

Use search to find risky static dates and visible timestamps:

```bash
rg -n "noscript|datePublished|dateModified|<time|datetime|更新日時|Reviewed|Updated|最終チェック|[0-9]{4}[-/][0-9]{2}[-/][0-9]{2}|[0-9]{1,2}/[0-9]{1,2} [0-9]{1,2}:[0-9]{2}" path/to/page
```

Then classify each match:

- static SEO or `noscript`: remove real time or replace with relative batch text,
- visible UI timestamp: add `data-nosnippet`,
- true article date: keep only if the page is intended to be article-like and the user wants that date indexed.

## Completion Checklist

- No real dates/times in `noscript` or static SEO fallback.
- No HTML date-stamp comments for SEO refresh throttling.
- All visible data/news/post/generated/reviewed timestamps use `data-nosnippet`.
- No `datePublished` or `dateModified` unless the page is a true article.
- Sitemap `<lastmod>` is generated or maintained separately from HTML SEO text.
- JSON-LD stays valid and uses the correct non-article schema type.
