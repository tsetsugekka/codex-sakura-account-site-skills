# Deployment and Migration Runbook

## Before Editing

- Identify production, staging, old, and backup directories from configuration and manifests.
- Enumerate all browser APIs, CLI workers, shared libraries, cron wrappers, and deployed copies.
- Check whether a protected page and its API are deployed by separate manifests.
- Record current credential/configuration names, model assignments, source policy, consumers, shell-profile exports, cron assignments, and per-provider files without printing values.
- Inspect Git status and preserve unrelated work.

## Safe Migration Sequence

1. Choose and document `managed-file-only` or `injection-first` for the application.
2. Create the private directory and configuration store outside the public web root.
3. Apply exact mode `0700` to the directory and `0600` to the file.
4. Migrate existing credentials plus required model/runtime settings without logging or printing values. For asymmetric providers, migrate the private-key body to its own `0700`/`0600` path and store only its path and signing metadata.
5. Install/update shared resolvers and tests, including wrong-mode rejection, duplicate rejection, missing-setting behavior, and source-policy behavior.
6. Update every consumer to canonical names and remove code defaults, aliases, direct parsers, per-job key files, and unintended CLI model overrides.
7. Update browser API gates and outbound-request controls.
8. Build locally and lint PHP/Python/shell files.
9. Prepare an exact SFTP allowlist. Include code and resolvers only, never the configuration store or private-key file from a repository staging directory.
10. Upload new hashed assets first, APIs/private application files next, and the live entry HTML last.
11. Run remote syntax checks against exact deployed paths.
12. Verify every runtime can read all settings it requires, duplicate count is zero, permissions are exact, endpoint behavior is correct, and configured model routing matches the intended workload.
13. Remove legacy per-provider key files and shell-profile/cron exports only after all consumers pass. Delete temporary incoming files immediately.
14. Start a fresh login/cron process to confirm persistent exports are gone. Already-running parent processes may retain inherited environment values until restarted, so readers in managed-file-only mode must ignore them throughout the migration.

Do not deploy readers before the managed values and required models exist; doing so can interrupt production jobs. Do not remove a legacy source before every deployed runtime passes; doing so can make rollback impossible.

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

Production checks should print only safe metadata such as required-name count, duplicate count, source label, exact file modes, HTTP status, and a deliberately non-secret model ID. Do not print file contents, environment dumps, private paths, credential fragments, raw provider bodies, or headers.

## Incident Follow-up

When an API was publicly reachable:

- review raw access logs, response codes, sizes, methods, user agents, and follow-up paths,
- compare provider usage and billing history,
- distinguish scanner requests from successful provider calls,
- rotate only the affected credential when abuse or exposure is confirmed,
- record unknowns as unconfirmed.

Do not infer compromise from a referrer report or an endpoint name alone.
