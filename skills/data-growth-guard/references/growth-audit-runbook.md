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

The state file records sizes and sampled oldest/newest ISO dates. It must remain private, mode `0600`, and outside every scanned root. A first run normally reports `watching`, not `accumulating`.

## 4. Verdicts

| Verdict | Meaning | Action |
| --- | --- | --- |
| `short` | Record span is below the reporting threshold | Keep observing |
| `watching` | No baseline old enough to judge | Wait for evidence |
| `sliding` | Oldest sampled date moved forward | Treat as bounded; verify its documented limit |
| `steady` | Oldest date is pinned but size is flat/shrinking or below growth floor | No growth deadline; inspect only if architecture is unclear |
| `accumulating` | Oldest date is pinned or moved backward and size grew materially | Report, estimate horizon, and design a bound |

Period-named shards are skipped by the growth checker because the filename itself bounds one file. Still inspect their index, retention, empty-shard cleanup, and total directory growth.

## 5. Report format

Deliver a report with:

1. scope, time, thresholds, and state age;
2. confirmed accumulating files;
3. measured MiB/month and projected size at retention;
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

Add a project-specific adapter instead of weakening the generic checker when these formats matter.
