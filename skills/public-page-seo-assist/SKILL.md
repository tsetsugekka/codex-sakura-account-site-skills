---
name: public-page-seo-assist
description: Audit or improve initial HTML body, metadata, canonical URLs and social previews for website pages. Use when public content is missing after JavaScript rendering, search finds only the URL, or sharing shows a wrong title; preserve protected content and existing page contracts.
---

# Public Page SEO Assist

Inspect source HTML, the generator/build path, the live response and rendered DOM. Distinguish public/indexable pages from protected/shareable pages; preserve the site's access and indexing policy. Search results, a readable source response and an actual Google indexed version are different evidence.

## Body delivery

Read [public-page-seo-patterns.md](references/public-page-seo-patterns.md) when changing head or body delivery.

- Identify what the user wants searchable. Fixed explanations can be ordinary HTML; articles, reports and rankings need their actual relevant content, not merely a product description. Chart/calculation tools need not embed their entire history.
- JSON can remain the source of truth. Choose build-time generation, the existing content update process or server rendering to fit the project; do not require a new scheduler or framework for every page.
- `noscript` is a no-JavaScript fallback, not proof that Google received the intended rendered body. Inspect whether application mounting replaces it or other initial content.
- Define which code owns initial HTML and interactive content. Do not remove useful initial content simply because JS started. Hydration needs matching markup and initial data; plain generated HTML cannot be arbitrarily hydrated. Avoid duplicate visible bodies or unstyled flashes.
- Test first-visit data failure separately from refresh failure: a new visitor has no previously loaded data. Preserve an available, valid snapshot under the site's freshness rules and show its status truthfully. Do not invent a snapshot or remove generation validation to suppress errors.
- Report uncertain causes precisely. A generic generation-mismatch message may represent mode, count or timestamp validation too; inspect the actual condition before naming a root cause.

These are design and verification criteria, not a claim that an untested architecture has already fixed indexing. Retrofit only the requested routes/generators. Preserve excluded subsystems and their independently maintained metadata contracts.

## Metadata and sharing

1. Emit charset, title, description, canonical, OG/Twitter and appropriate robots in the initial response before application/analytics scripts. Charset belongs near the start of head. Align canonical and `og:url` with the final route, and sitemap `loc` when listed.
2. Follow the project's favicon and language conventions. Choose structured data matching the page: tools are not articles merely because their data changes. Read [time-snippet-safety.md](references/time-snippet-safety.md) for data times versus genuine publication dates.
3. Use truthful significant-content modification dates for sitemap `lastmod` when available and permitted by the project; omit when not known or the project omits it. A deploy/cron wakeup alone is not a content change.
4. For protected sharing, read [private-page-sharing-patterns.md](references/private-page-sharing-patterns.md). Expose only safe route-specific metadata at the gate; do not weaken login or API authorization.
5. For image cards and social-client problems, read [social-preview-verification.md](references/social-preview-verification.md). Use a representative public image with truthful dimensions, not a favicon or private asset. A text-only card is an intentional compatibility limitation.
6. Identify server-owned HTML regions. Preserve their markers and current content through the existing generator/deploy process; combine with `static-deploy-refresh-check` when relevant.

## Verification

- Initial response and JS-disabled view contain the agreed public body; normal rendered DOM still contains it. Check first-load errors, relevant generation mismatch and direct detail URLs.
- Built and live head have the expected single title/canonical, valid JSON-LD and final URL signals. Inspect real response status and redirect chain.
- Data timestamps use the project's snippet policy without disguising stale data as current. Keep internal prompts, permissions and operational notes out of public HTML, comments and payloads.
- For sharing, request with the relevant crawler user agents and inspect response/image metadata. Actual chat sending needs user authorization; a composer preview is not final-card evidence.
- Search Console rendered/crawled HTML, when available, is separate from local browser evidence. Do not promise indexing from tags, `noscript`, `site:` results or a different search backend.
