# Deployment and Migration Runbook

## Before Editing

- Identify production, staging, old, and backup directories from configuration and manifests.
- Enumerate all browser APIs, CLI workers, shared libraries, cron wrappers, and deployed copies.
- Check whether a protected page and its API are deployed by separate manifests.
- Record current credential names and consumers without printing values.
- Inspect Git status and preserve unrelated work.

## Safe Migration Sequence

1. Create the private directory and credential store outside the public web root.
2. Apply `0700` to the directory and `0600` to the file.
3. Migrate existing values without logging or printing them.
4. Install/update shared resolvers and tests.
5. Update every consumer to canonical names.
6. Update browser API gates and outbound-request controls.
7. Build locally and lint PHP/Python/shell files.
8. Prepare an exact SFTP allowlist. Include code and resolvers only, never the credential store.
9. Upload new hashed assets first, APIs/private application files next, and the live entry HTML last.
10. Run remote syntax checks against exact deployed paths.
11. Verify configuration source labels and endpoint behavior.
12. Remove legacy key files only after all consumers pass.

Do not reverse steps 3 and 5: deploying readers before the managed value exists can interrupt production jobs. Do not reverse steps 11 and 12: deleting the legacy source before verification can make rollback impossible.

## Production Verification

Use low-frequency checks against only the owned site:

```sh
curl -sS -D - -o /dev/null --max-time 10 https://example.com/protected/api/health.php
curl -sS -D - -o /dev/null --max-time 10 \
  -X POST -H 'Content-Type: application/json' --data '{}' \
  https://example.com/protected/api/provider.php
```

Expected unauthenticated results:

- business GET/POST: `401`,
- insufficient page permission: `403`,
- include-only helper and HTTP worker: `404`,
- mutation with session but without CSRF: `403`.

For an authenticated happy-path check, use the smallest request that proves routing and permission. Avoid a real provider call when a local configuration check is sufficient. If a provider request is necessary, use one harmless native status request and document quota impact.

## Incident Follow-up

When an API was publicly reachable:

- review raw access logs, response codes, sizes, methods, user agents, and follow-up paths,
- compare provider usage and billing history,
- distinguish scanner requests from successful provider calls,
- rotate only the affected credential when abuse or exposure is confirmed,
- record unknowns as unconfirmed.

Do not infer compromise from a referrer report or an endpoint name alone.
