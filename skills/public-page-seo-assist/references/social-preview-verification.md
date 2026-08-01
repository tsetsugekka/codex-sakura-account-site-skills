# Social Preview Verification

Use this reference when a pasted URL has no card, a generic title, stale metadata, or a missing image in Discord, X, Slack, LINE, Telegram, or similar clients.

## Response Contract

Link-preview crawlers usually fetch HTML without running application JavaScript. The final response after redirects must therefore contain literal, non-empty values for:

- `title`
- `meta name="description"`
- canonical URL
- `og:type`, `og:url`, `og:title`, `og:description`, `og:site_name`, and `og:locale`
- `twitter:card`, `twitter:title`, and `twitter:description`

Declare UTF-8 within the first 1024 bytes of `<head>`. Put the core metadata before analytics, import maps, app boot scripts, or blocking third-party scripts. The response should be `200` and `Content-Type: text/html`; a JSON response, generic login redirect, bot challenge, or HTML shell whose tags are injected later is not sufficient.

## No-Image Cards

Pages without a suitable image should use `twitter:card=summary` and omit `og:image`/`twitter:image`. Do not add a favicon or placeholder solely to force a picture. This is an intentional text-only degradation, not a guarantee that every client will render the title and description: the Open Graph basic object includes `og:image`, and clients are free to show a more compact link when it is absent.

## Image Cards

For a real preview image:

- use an absolute public HTTPS URL;
- require `200` without cookies or referer;
- require a real image MIME type;
- keep the image stable for the page's retention period;
- add `og:image:secure_url`, `og:image:type`, truthful `og:image:width`/`og:image:height`, and `og:image:alt`;
- place those structured properties directly after the corresponding `og:image` root;
- explicitly add `twitter:image` and `twitter:image:alt` for predictable X cards;
- use `summary_large_image` only when the image is appropriate for a large card.

There is no universal Open Graph crop requirement. Do not invent `1200x630` dimensions for an uncropped source file. A representative original image with correct dimensions is valid; crop only when the product intentionally needs a consistent card composition.

If an upstream image host blocks crawlers or hotlinks, cache the one approved preview image on the same public site. Do not claim that changing URL query parameters will force every platform to refetch; many clients cache by normalized URL or retain failed previews.

## Dynamic Detail Routes

A dynamic article or narrative route needs route-specific metadata in its initial response. Keep the interactive shell and modal experience if desired, but render the detail URL server-side or generate a static HTML entry that includes:

- its permanent canonical URL and matching `og:url`;
- its own title and summary;
- article-like time metadata only when the route is intentionally a strong time-sensitive detail page;
- the first eligible evidence image when approved;
- visible/fallback body content consistent with the selected detail.

Redirect aliases should resolve to one canonical permanent route. When an item changes category, update the canonical prefix according to the project's ID policy and retain a redirect from the old URL.

## Commands

Inspect the crawler response and redirect chain:

```bash
curl -sS -L -A 'Discordbot/2.0' -D /tmp/preview.headers \
  -o /tmp/preview.html https://example.com/page/
```

Repeat the live check with Telegram's crawler. A page can work in X while Discord or Telegram still sees an incomplete initial response:

```bash
curl -sS -L -A 'TelegramBot (like TwitterBot)' -D /tmp/telegram-preview.headers \
  -o /tmp/telegram-preview.html https://example.com/page/
```

Inspect a declared image independently:

```bash
curl -sS -L -I -A 'Discordbot/2.0' https://example.com/cards/page.jpg
```

Run the bundled deterministic checker against source files or deployed URLs:

```bash
python3 scripts/check_social_preview.py path/to/index.html
python3 scripts/check_social_preview.py https://example.com/page/
```

Finally paste a fresh test URL into the actual target client and send a private test message. A successful curl proves the response contract, but the client can still show an older cached card. Telegram and Discord can both show a reduced pre-send/composer preview; do not mistake that temporary UI for the final sent card. Validate the sent message, where the client can show the complete site name, title, description, and photo. Telegram can also retain an old preview by URL; use a disposable query parameter only to diagnose that cache, never as the permanent canonical or `og:url`.

## Standards Boundary

- Open Graph is the shared cross-platform metadata contract. Its official basic properties are title, type, image, and canonical object URL; description, site name, locale, and structured image properties enrich the object.
- Telegram officially exposes preview fields for site name, title, description, author, and photo, plus controls for large/small media. Its public API does not define a separate webpage-meta syntax, so use standards-compliant Open Graph and verify the sent result.
- Discord documents rich embed fields and limits but does not publish a separate Open Graph parser contract for arbitrary pasted webpages. Use Open Graph as the baseline and verify the actual `Discordbot/2.0` response.
- X-specific tags remain useful even when Open Graph fallbacks work. Keep explicit `twitter:card`, title, description, and image fields so X behavior is not coupled to an undocumented fallback.

Primary references:

- Open Graph protocol: https://ogp.me/
- Telegram link preview object: https://core.telegram.org/tdlib/docs/classtd_1_1td__api_1_1link_preview.html
- Telegram link preview options: https://core.telegram.org/bots/api#linkpreviewoptions
- Discord embed resource: https://docs.discord.com/developers/resources/message#embed-object
