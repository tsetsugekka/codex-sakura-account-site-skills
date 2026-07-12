# Private Page Sharing Patterns

Use this reference when a login-only, staff-only, or permission-protected page needs a useful preview in LINE, Telegram, Slack, or another social/chat client.

## Boundary

Private share metadata is not search-engine SEO:

- keep `robots` as `noindex, nofollow`;
- do not add the route to `sitemap.xml`;
- do not expose private records, user names, account data, raw post text, or exact volatile timestamps;
- preserve authorization for the page HTML, data APIs, and post-login destination.

## Redirect Pattern

When an unauthenticated request reaches a protected route:

1. Read the original request path and query string.
2. Accept it only when it is an internal path beginning with `/` and not `//`; otherwise fall back to the protected route's safe base path.
3. Redirect to the login/gate page with a URL-encoded return parameter, for example:

```text
/?return=%2Fprivate-tool%2Fdetail%2F%3Fid%3D123
```

4. The login/gate page resolves a safe metadata record from that return path. It must not fetch or render protected data just to build a card.
5. After successful login, return the user to the original internal path and query.

Do not redirect every protected page to `/` without context. A social crawler follows the redirect and then sees the portal's generic title and description.

## Metadata Pattern

The unauthenticated gate response may be a metadata-only/login page, but it should identify the intended target:

```html
<title>キャンペーン - Example Monitor</title>
<link rel="canonical" href="https://example.com/private-tool/campaign/">
<meta name="description" content="キャンペーンに関する情報を確認するページです。">
<meta name="robots" content="noindex, nofollow">
<meta property="og:type" content="website">
<meta property="og:title" content="キャンペーン - Example Monitor">
<meta property="og:description" content="キャンペーンに関する情報を確認するページです。">
<meta property="og:url" content="https://example.com/private-tool/campaign/">
<meta property="og:locale" content="ja_JP">
<meta property="og:site_name" content="Example Site">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="キャンペーン - Example Monitor">
<meta name="twitter:description" content="キャンペーンに関する情報を確認するページです。">
```

The protected page itself should also emit equivalent page-specific metadata for authenticated browsers and share tools that retain a session.

## Query-Based Views

For a protected shell with views such as `?view=topics`, resolve a stable label from an allowlisted view map. Do not copy arbitrary query text into `<title>` or descriptions. If a selected topic is private or volatile, use a generic safe label such as `テーマ詳細`.

## Verification

Run an unauthenticated request with redirects enabled and inspect both responses:

```bash
curl -sS -L -D /tmp/headers -o /tmp/page.html https://example.com/private-tool/campaign/
```

Verify that:

- the first redirect contains the internal return path and no external host;
- the final HTML has the target-specific title and `og:title`;
- canonical and `og:url` point to the original target URL;
- `robots` is `noindex, nofollow`;
- the response contains no private content or exact volatile data;
- authenticated navigation still returns to the original target after login.

Open Graph controls the preview card. It does not control the plain text that a chat client places above the card; that text comes from the client, pasted message, or an explicit Web Share/share action.
