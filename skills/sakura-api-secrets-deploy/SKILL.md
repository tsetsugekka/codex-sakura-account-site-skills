---
name: sakura-api-secrets-deploy
description: Secure server-side API integrations on Sakura Server. Use when Codex needs to centralize API credentials and model/runtime configuration outside the public web root, choose and enforce a managed-file-only or injection-first source policy across PHP/Python/cron, handle asymmetric private keys, protect browser-facing APIs, prevent SSRF, migrate legacy files and shell exports, deploy through an exact SFTP allowlist, and verify production without exposing secrets or consuming unnecessary provider quota.
---

# Sakura API Secrets Deploy

## Goal

Deploy server-side API integrations on Sakura Server without exposing credentials, creating an unauthenticated quota proxy, or allowing a URL-fetching endpoint to reach private network targets.

Use `sakura-ssh-deploy-setup` for SSH/SFTP credential helpers and base deployment manifests. Use `sakura-auth-site-setup` when the site also needs login, roles, page permissions, or browser-session CSRF infrastructure.

## Required Contract

- Keep one application-scoped managed configuration store outside the public web root. Do not split it by program or provider.
- Require its parent directory to be exactly `0700` and the file to be exactly `0600`; reject the store when either mode is wrong.
- Use one canonical configuration key per credential, model, signing setting, or other API routing value. These names are file keys unless the selected policy explicitly treats them as process environment variables.
- Choose one source policy for the application and document it: `managed-file-only` or `injection-first`. Never silently mix policies between PHP, Python, cron, tests, and deployed copies.
- In `managed-file-only` mode, ignore same-name process environment values and environment-controlled path overrides. In `injection-first` mode, resolve a non-empty injected value before the managed store only when that fallback is explicitly part of the contract.
- Maintain the same canonical allowlist and policy in every shared reader. Unknown names resolve unconfigured; duplicate canonical entries reject the whole store.
- Multiple programs may read the store concurrently. Every writer must create a complete `0600` temporary file in the same `0700` directory and atomically rename it over the live file; never truncate the live file in place.
- Keep asymmetric private-key bodies in a separate non-empty PEM file with parent directory `0700` and file `0600`. Store only the canonical app/client ID, signing algorithm, and private-key path in the managed configuration.
- Diagnostic surfaces may expose a configured boolean, a safe source label such as `environment`, `managed_private_config`, or `unconfigured`, and deliberately non-secret model IDs. Show internal canonical key names only when they add operator value; in managed-file-only mode, never label file keys as environment variables.
- Never expose a value, masked length, private file path, raw upstream body, authorization header, or provider error body to browsers or logs.
- Require server-side authentication and the page-defined permission on every browser-facing business API.
- Require CSRF on cookie-authenticated writes, quota-consuming calls, job control, uploads, and other side effects.
- Allow scoped bearer-token APIs only when they never fall back to browser cookie authentication.
- Make include-only PHP libraries return `404` when requested directly. Make CLI workers reject HTTP execution.

## Workflow

1. Inventory the real environment:
   - public web root, private application root, cron/job directories,
   - every HTTP API endpoint and helper file,
   - every provider credential name and reader,
   - every SFTP manifest, worker, health/status UI, legacy key file, and deployed copy.
2. Classify endpoints before editing:
   - intentionally anonymous account lifecycle,
   - cookie-authenticated browser API,
   - scoped bearer-token API,
   - CLI-only worker,
   - include-only library,
   - public read-only data that intentionally needs no account.
3. Define the canonical configuration allowlist, source policy, private store, model assignments, and any asymmetric-key exception. Read `references/credential-store.md`.
4. Implement shared PHP, Python, and shell resolvers. Fail closed when a name is unknown or unconfigured.
5. Add endpoint gates before reading credentials, request bodies, job data, or private records. Read `references/api-gateway-security.md`.
6. For any user-controlled URL, add outbound-request validation before the first request and at every redirect hop.
7. Prepare a migration and exact-file deployment. Read `references/deployment-runbook.md`.
8. Migrate credentials and required model/runtime settings before deploying readers that depend on the new store.
9. Build locally, lint every changed server file, deploy by allowlist, then run low-frequency production verification.
10. Verify every deployed runtime, then remove legacy per-provider key files and shell-profile exports. Review provider usage and server logs when an endpoint was previously public. Rotate a credential only when exposure or abuse is confirmed, or when the provider's policy requires it.

## Endpoint Gate Matrix

| Endpoint class | Authentication | Permission | CSRF | Direct HTTP |
| --- | --- | --- | --- | --- |
| Browser GET business API | Session | Page-defined | No | Allowed after gate |
| Browser POST/PUT/PATCH/DELETE | Session | Page-defined | Required | Allowed after gate |
| Quota-consuming provider proxy | Session | Page-defined | Required | Allowed after gate |
| Scoped bearer API | Bearer only | Token scope | Not cookie CSRF | Allowed after token gate |
| Anonymous login/verification/reset bootstrap | Intentionally anonymous | Narrow lifecycle rules | Use the site's anonymous-CSRF/origin policy | Allowed |
| Intentional public read-only data | None by design | Fixed public dataset only | No | Allowed and documented |
| CLI worker | None over HTTP | CLI/runtime account | Not applicable | `404` |
| Include-only PHP library | Not applicable | Not applicable | Not applicable | `404` |

Do not treat a protected page entrypoint as protection for a sibling `/api/*.php` URL. Repeat the authorization decision inside every business endpoint.

## Verification

- Confirm the configuration directory is exactly `0700` and the file exactly `0600` without printing contents.
- Confirm every required canonical key is present once, duplicate count is zero, and model/runtime routing matches the intended workload.
- Confirm the managed store and local secret files are ignored and untracked.
- Confirm source and deployed copies use the same canonical allowlist.
- In managed-file-only mode, confirm a same-name process environment value does not override the file and a fresh login/cron environment contains no legacy exports.
- Confirm unauthenticated business API requests return `401`, insufficient permission returns `403`, and direct helper/worker requests return `404`.
- Confirm cookie-authenticated mutations without a valid CSRF token return `403` before any provider call or state change.
- Confirm status UI never returns values, paths, or raw provider responses.
- Confirm private, loopback, link-local, reserved, userinfo, nonstandard-port, and unsafe redirect targets are rejected.
- Confirm normal authorized provider calls and front-end routes still work.
- Run `git diff --check`, language-specific tests, and a public-safe secret scan before publishing.

## Safety Rules

- Never print or commit live credentials, cookies, private keys, private config, provider bodies, or production logs.
- Never upload `.env`, the managed credential store, databases, user data, caches, logs, backups, or a whole repository.
- Never write an asymmetric private-key body or its base64 form into process environment variables, the shared line-oriented store, browser responses, or logs.
- Never update the live store by redirecting, truncating, or appending in place while readers may be active.
- Never perform high-volume provider tests. Prefer configuration checks or one harmless provider-native status request.
- Never follow redirects automatically for user-controlled fetches.
- Never accept a caller-provided arbitrary upstream URL for a credentialed provider proxy.
- Never claim production is fixed until the deployed endpoint behavior is verified.
- Never delete legacy key files before all deployed consumers have switched and passed verification.
- After verified migration, do not retain legacy per-provider files or shell-profile exports as undocumented fallback sources.

## References

- Read `references/credential-store.md` before designing names, files, or language resolvers.
- Read `references/api-gateway-security.md` before changing endpoint authentication, CSRF, health checks, or URL fetching.
- Read `references/deployment-runbook.md` before migration, SFTP deployment, production verification, or legacy cleanup.
