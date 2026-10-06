# Growth Audit Runbook

## Contents

1. Scope and evidence
2. Inventory
3. Persistent observation
4. Verdicts
5. Report format
6. Server workflow
7. Blind spots

## 1. Scope and evidence

An audit starts with explicit roots and access authority. Record for each root:

- public web root, private application data, logs, backups, or another role;
- owner process and writer schedule;
- expected retention and partitioning;
- whether the scan may update a private observation state file;
- whether the request is audit-only or also authorizes guard installation.

Do not call a file unbounded because it is large. Useful evidence needs at least two observations separated by enough time to distinguish a filling/sliding window from accumulation.

## 2. Inventory

Before scanning, inspect:

- cron/systemd wrappers and deploy manifests;
- JSON, JSONL, CSV, SQLite, logs, compressed archives, and generated exports;
- directory names such as `days`, `months`, `history`, `cache`, `snapshots`, `logs`, and `backups`;
- filename periods such as `YYYY-MM` or `YYYY-MM-DD`;
- indexes and locators that point into shards;
- retention/prune functions and tests;
- public files that are rebuildable projections versus authoritative history;
- private caches, cursors, locks, state, queues, and failure records.

Build a table with: path pattern, public/private, writer, readers, authority/projection, current size, oldest/newest record, update cadence, retention, and known bound.

## 3. Persistent observation

Run the bundled checker from a private operations directory:

```bash
python3 scripts/check_data_growth.py \
  --root /path/to/approved/data \
  --state /path/to/private-state/observations.json \
  --date-field recorded_at \
  --format markdown
```

Important defaults:

- minimum file size: 1 MiB;
- reporting span: 40 days;
- minimum baseline age: 14 days;
- meaningful growth: 0.25 MiB/month;
- projection horizon: 1,095 days;
- observation history: 40 daily samples;
- stale state removal: 150 days.

Tune thresholds to the project. The reporting span is patience, not a storage recommendation. Shorter windows may be correct for fast-growing data; slow systems may need a longer baseline.

Verify that `recorded_at` is the actual JSON record-time field before using the example. Repeat `--date-field` only for equivalent fields; split scans/state files when schemas or meanings differ. Field names match at any nesting depth, so a same-named control or nested field requires a project adapter instead. The selector accepts ISO date or datetime strings, not epoch values or escaped JSON key names. It is bounded lexical sampling, not a complete JSON parser.

Without `--date-field`, arbitrary text dates are discovery hints classified `unverified`, never status `10`. This change deliberately prevents old guards from mailing false confirmations; configure a verified field or adapter before relying on unattended alerts. An old-enough baseline alone does not verify date semantics.

The state file records sizes, sampled oldest/newest ISO dates and the date-field selection. It must remain private, mode `0600`, and outside every scanned root. A first record-date run normally reports `watching`, not `accumulating`. Changing fields or upgrading legacy state without field metadata starts a new baseline for that file.

## 4. Verdicts

| Verdict | Meaning | Action |
| --- | --- | --- |
| `short` | Record span is below the reporting threshold | Keep observing |
| `watching` | No baseline old enough to judge | Wait for evidence |
| `sliding` | Oldest selected record date moved forward | Verify the writer's window; this alone does not prove a ceiling |
| `steady` | Oldest date is pinned but size is flat/shrinking or below growth floor | No growth deadline; inspect only if architecture is unclear |
| `accumulating` | Verified record field's oldest date is identical across compared samples and size grew materially | Growth signal: verify writer/pruner, peaks and bounds before migration |
| `changed` | Oldest date moved backward or changed within the comparison period | Inspect backfill, schema changes and window membership; not pinned accumulation |
| `unverified` | Text-date discovery only, or selected field contains future dates | No growth hook; verify date semantics/clock and document the coverage gap |

Period-named shards are skipped by the growth checker because the filename itself bounds one file. Still inspect their index, retention, empty-shard cleanup, and total directory growth.

## 5. Report format

Deliver a report with:

1. scope, time, thresholds, and state age;
2. confirmed accumulating files;
3. measured MiB/month and conditional projected size at a stated horizon, independently of actual retention;
4. bounded sliding windows and period shards;
5. files still waiting for a baseline;
6. files ignored because they are small, undated, binary, compressed, or explicitly excluded;
7. architecture recommendation and migration risk;
8. next observation date.

For every confirmed file, include:

- path pattern or sanitized label;
- current size;
- sampled oldest/newest dates and span;
- baseline date and elapsed days;
- actual bytes gained and MiB/month;
- projected size at the chosen retention horizon;
- likely writer/readers;
- recommended bound: retention window, period shard, cardinality cap, or rebuildable snapshot.

Do not publish real server paths or private filenames in a public issue or repository. Sanitize reports before sharing.

## 6. Server workflow

For an authorized SSH server:

1. inspect the existing private operations directory and Python version;
2. upload only the public-safe checker, or run an already deployed copy;
3. place state and reports outside the web root;
4. run manually once and preserve the baseline;
5. review sampled files for false assumptions about dates or ordering;
6. integrate with the existing scheduler only when installation is authorized;
7. make alerting consume sanitized report output;
8. re-run through the scheduler and verify state permissions.

The checker is non-blocking by design: exit `10` means a finding, not a broken application. A wrapper may translate `10` into an alert while still allowing the primary crawler to finish.

## 7. Blind spots

The bundled checker samples ISO dates from the head and tail of regular files. It does not fully parse every schema. Explicitly call out these blind spots:

- SQLite and other databases need table-level row/time metrics;
- gzip/zip files need archive-specific inventory;
- epoch-only timestamps need a project adapter;
- unsorted files may hide the true oldest record in the middle;
- fewer than eight recognizable dates are treated as undated;
- a fixed-size database may still accumulate rows while reclaiming pages internally;
- a directory can grow without any single file growing, so shard count and retention also need inspection;
- a period shard can be too large for practical reads even though it is bounded.

Add a project-specific adapter instead of weakening the generic checker when these formats matter. Even field-based samples can miss middle records; they remain signals, not proof that no ceiling exists.

## False-positive case: quoted dates in a working cache

A monitored cache produced a multi-year span and a multi-year growth projection. Inspection located its oldest ISO date inside a quoted comment, not the record timestamp; another text quote contained a future date. The writer kept a current working set plus recently active keys, and observations included a size peak larger than the latest sample. Generic date sampling had conflated prose with retained history, while comparing only endpoints hid the cache's fluctuations.

The fix is to verify record-time fields and the actual writer/prune contract, retain unrelated body text unchanged, and classify free-text dates as unverified. Do not repartition or truncate a bounded cache solely because of this alert. Tests cover quoted old/future dates, real pinned growth, backward/mixed dates and re-baselining. The projection horizon never implied automatic cleanup.
