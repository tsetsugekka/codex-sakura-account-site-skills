# API Gateway and Egress Security

## Authorization Order

For cookie-authenticated business endpoints, use this order:

1. Require the expected HTTP method.
2. Load the authentication bootstrap.
3. Require a valid session.
4. Require the page-defined permission.
5. Require CSRF for mutations, provider quota calls, task control, or uploads.
6. Only then read the credential, request body, job identifier, private record, or upload.
7. Validate a resource owner or administrator when the data is user-scoped.

This ordering prevents unauthenticated callers from using validation differences to enumerate jobs, configuration, or private records.

For scoped bearer endpoints, reject cookie fallback. A cross-site form cannot set a custom bearer header, but a mixed bearer-or-cookie endpoint restores CSRF risk and must use the cookie-authenticated rules.

## Anonymous Lifecycle Exceptions

Login, registration, verification, password-reset request, reset completion, OAuth start/callback, and session bootstrap may need anonymous access. Keep them narrow:

- fixed methods and payload limits,
- generic responses where account enumeration is possible,
- rate limits/cooldowns,
- single-use hashed tokens with expiry,
- CSRF or strict same-origin handling appropriate to the site's bootstrap design,
- no provider credential status, arbitrary URL fetch, file access, or admin action.

## Helper and Worker Paths

PHP files that only declare functions should fail direct execution:

```php
if (realpath((string) ($_SERVER['SCRIPT_FILENAME'] ?? '')) === __FILE__) {
    http_response_code(404);
    exit;
}
```

HTTP-deployed workers should fail unless invoked from CLI:

```php
if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}
```

Prefer placing workers and shared private application code outside the public web root when the deployment supports it.

## Safe Status UI

Protect status endpoints with administrator or explicit operator permission. Return only:

- service display name,
- canonical variable name,
- configured boolean,
- safe source label,
- normalized test result and timestamp.

Never return a value, private path, environment dump, PHP error, stack trace, authorization header, or raw provider body. Rate-limit manual tests and disclose when a test consumes provider quota.

## Fixed Provider Upstreams

Credentialed provider proxies should call code-defined HTTPS origins and paths. Do not accept a caller-provided provider base URL. Disable automatic redirect following unless each target is independently allowlisted and revalidated.

## User-Controlled URL Fetches

When a feature must fetch article or page URLs:

1. Allow only `http` and `https`.
2. Reject URL userinfo and control characters.
3. Allow only explicitly required ports; default to `80/443`.
4. Resolve all A and AAAA records.
5. Reject the entire host when any answer is loopback, private, link-local, reserved, multicast, or otherwise non-public.
6. Pin the validated resolution for the connection to reduce DNS rebinding risk.
7. Disable automatic redirects.
8. Resolve relative redirects safely and repeat every validation at every hop.
9. Cap redirects, timeouts, response bytes, and accepted content types.
10. Do not place fetched raw content or upstream errors in logs.

An explicit domain allowlist or a reviewed outbound proxy is safer when the business can tolerate it.
