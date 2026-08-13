# API Configuration Store Contract

## Layout

Use one application-scoped file outside the public web root, shared by that application's PHP, Python, cron, and worker copies:

```text
/home/ACCOUNT/.config/APP/api_secrets.env
```

Required modes:

```text
/home/ACCOUNT/.config/APP/ 0700
api_secrets.env            0600
```

The directory and file must be owned by the intended runtime account and must not be symlinks. The file contains only canonical `NAME=value` entries. The `.env` suffix describes a line-oriented format; it does not mean the entries are process environment variables. The file is server-managed private configuration, not a deploy artifact, project fixture, status response, or backup copied into `www`.

## Canonical Names

Choose one stable uppercase name for each credential and API setting, for example:

```text
SEARCH_API_KEY
LLM_API_KEY
LLM_ANALYSIS_MODEL
LLM_TRANSLATION_MODEL
SOCIAL_DATA_API_KEY
```

Provider-standard names are also acceptable. Keep the same names in every runtime. Do not introduce alternate aliases, per-page key files, per-job model flags, code defaults that silently override the store, or duplicated parsers.

Maintain an explicit allowlist. Unknown names must resolve to an unconfigured result even if they exist in the file. A canonical name appearing more than once rejects the whole store instead of using first-wins or last-wins behavior.

## Source Policy

Choose exactly one policy for the application.

### Managed-file-only

Use this when the operator wants one persistent source that multiple programs can read directly. Readers use only the fixed application-scoped file and ignore same-name environment values. Production must not accept an environment-controlled store-path override. This is a valid security design when the directory, file permissions, ownership, deployment boundary, and logging rules are enforced; process environment variables are not categorically safer.

Resolution:

1. Non-empty allowlisted value from the managed private store.
2. Explicit `unconfigured` result.

### Injection-first

Use this only when a service manager or deployment platform deliberately injects runtime secrets and the application contract says that injected values may override the file.

Resolution:

1. Non-empty process environment value.
2. Non-empty allowlisted value from the managed private store.
3. Explicit `unconfigured` result.

Do not use injection-first merely because the file is named `.env`. Keep the selected policy identical in PHP, Python, cron, tests, and deployed reader copies.

Return values only to server-side callers. A diagnostic function may return one safe label:

```text
environment
managed_private_config
unconfigured
```

Do not return the private path, key prefix/suffix, length, hash, provider response, or configuration exception to a browser.

## Models and Non-secret Settings

Model IDs, signing algorithms, and other API routing values are not necessarily credentials, but they should use canonical keys and the same managed configuration when consistent rollout matters. Consumers should not carry hidden model defaults or per-job overrides. A protected operator view may show a non-secret model ID and purpose when useful, but it must not expose credential values or private paths.

## Asymmetric Credentials

Do not put a private-key body or base64-encoded private key in the line-oriented store or a process environment variable. Use a separate application-private PEM file:

```text
/home/ACCOUNT/.config/APP/provider/private_key.pem
```

Require the provider directory to be exactly `0700`, the PEM to be a non-empty regular file with mode `0600`, and the signing algorithm to be an explicit allowlisted value. The shared store contains only canonical entries such as the app/client ID, signing algorithm, and absolute private-key path.

## Parser Rules

- Ignore blank lines and lines beginning with `#`.
- Accept only `^[A-Z][A-Z0-9_]*=` names.
- Split on the first `=` so values may contain later `=` characters.
- Optionally remove one matching pair of surrounding single or double quotes.
- Never evaluate shell syntax, expand variables, execute substitutions, or source an untrusted file directly.
- Reject the entire store when a canonical name is duplicated.
- In injection-first shell readers, export only allowlisted names and preserve a pre-existing injected value. In managed-file-only mode, do not export persistent values through shell profiles or cron assignments.

## Concurrent Reads and Atomic Writes

Many cron jobs and web requests may read the same file concurrently. Ordinary read-only opens are safe when writers follow this protocol:

1. Set `umask 077`.
2. Create a complete temporary file in the same private directory.
3. Validate required names, uniqueness, and non-empty values without printing values.
4. Set the temporary file to `0600`.
5. Atomically rename it over the live file.
6. Remove temporary incoming files on success, failure, signal, and disconnect.

Never redirect into, truncate, or append to the live file in place. Same-directory rename ensures readers see either the old complete version or the new complete version.

## Adding a Provider

Update all of these in one maintenance change:

1. Canonical allowlists and source policy in every shared resolver.
2. Server-managed configuration store.
3. Every PHP/Python/cron consumer.
4. Required model/runtime settings and any asymmetric-key files.
5. Protected operator status registry and tests.
6. Exact SFTP deployment allowlist.
7. Page/worker documentation and verification commands.

Migrate credentials and required settings before deploying readers that require them. Verify every runtime, permissions, uniqueness, safe source labels, and only the smallest necessary provider-native check. Then remove obsolete key files, shell-profile exports, and temporary incoming files.
