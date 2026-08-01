# Credential Store Contract

## Layout

Use one application-scoped file outside the public web root:

```text
/home/ACCOUNT/.config/APP/api_secrets.env
```

Required modes:

```text
/home/ACCOUNT/.config/APP/ 0700
api_secrets.env            0600
```

The file contains only canonical `NAME=value` entries. It is server-managed private configuration, not a deploy artifact, project fixture, status response, or backup copied into `www`.

## Canonical Names

Choose one stable uppercase name for each provider, for example:

```text
SEARCH_API_KEY
LLM_API_KEY
SOCIAL_DATA_API_KEY
```

Provider-standard names are also acceptable. Keep the same names in every runtime. Do not introduce `*_FILE`, alternate aliases, per-page key files, or duplicated parsers.

Maintain an explicit allowlist. Unknown names must resolve to an unconfigured result even if they exist in the file.

## Resolution Order

Use the same order in PHP, Python, and cron:

1. Non-empty process environment value.
2. Non-empty value from the managed private store.
3. Explicit `unconfigured` result.

Return the value only to the server-side caller. A status function may also return one safe label:

```text
environment
managed_private_config
unconfigured
```

Do not return the private path, key prefix/suffix, length, hash, provider response, or configuration exception to a browser.

## Parser Rules

- Ignore blank lines and lines beginning with `#`.
- Accept only `^[A-Z][A-Z0-9_]*=` names.
- Split on the first `=` so values may contain later `=` characters.
- Optionally remove one matching pair of surrounding single or double quotes.
- Never evaluate shell syntax, expand variables, execute substitutions, or source an untrusted file directly.
- In shell, export only allowlisted names and preserve a pre-existing environment value.

## Adding a Provider

Update all of these in one maintenance change:

1. Canonical allowlists in every shared resolver.
2. Server-managed credential store.
3. Every PHP/Python/cron consumer.
4. Protected operator status registry and tests.
5. Exact SFTP deployment allowlist.
6. Page/worker documentation and verification commands.

Migrate the credential before deploying a reader that requires it. Verify the safe source label and one provider-native connectivity check, then remove obsolete key files only after all consumers pass.
