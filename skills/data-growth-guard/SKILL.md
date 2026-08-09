---
name: data-growth-guard
description: Audit servers and website data directories for single files that may grow without a ceiling, produce evidence-based growth reports, scaffold a persistent growth guard, and design bounded public/private data architecture with retention, period shards, indexes, consumer-specific frontend snapshots, exact detail reads, atomic publication, and safe migration. Use when JSON, logs, exports, caches, histories, feeds, or generated datasets keep getting larger; when setting up cron-based file-growth monitoring and alerts; or when deciding how a crawler-backed site should separate private runtime state from public archives and bounded projections.
---

# Data Growth Guard

Use this skill to answer three related questions:

1. Is a server file actually accumulating without a ceiling?
2. How should a persistent guard observe and report that risk?
3. How should the data be reorganized so authoritative history, private state, and frontend reads stay bounded and understandable?

Do not equate a large file with an unbounded file. The decisive evidence is that the oldest retained record stays pinned while the file keeps gaining bytes across observations.

## Select the workflow

### Audit a server or directory

1. Read [references/growth-audit-runbook.md](references/growth-audit-runbook.md).
2. Confirm the authorized roots and whether each is public or private. Never widen an SSH or filesystem scope merely to make discovery easier.
3. Inventory existing retention, shards, snapshots, indexes, caches, logs, cron jobs, locks, and state files before running a new scanner.
4. Run `scripts/check_data_growth.py` against each approved root with a state file outside every scanned/public root.
5. Treat the first run as a baseline, not proof. Report confirmed accumulation only after an old-enough baseline exists.
6. Deliver a Markdown report that separates confirmed findings, bounded windows, period shards, steady files, files still being watched, and blind spots.

For a server, prefer executing the public-safe checker remotely from a private operations directory. Alternatively, scan a mounted or safely exported directory. Do not copy credentials, private records, or full data dumps into the skill repository.

### Install or repair a guard

1. Read [references/guard-deployment.md](references/guard-deployment.md).
2. Inspect the site's existing cron wrapper and notification path. Reuse them when they already provide locking, logs, and failure-only mail.
3. Dry-run `scripts/scaffold_data_growth_guard.py`; review the exact output paths and cron line.
4. Generate the checker, wrapper, and cron example with `--write` only after confirming that the script and state directories are private and outside the scan root.
5. Test baseline, confirmed-growth, sliding-window, lock-skip, broken-state, and notification paths.
6. Keep the guard non-blocking: a growth finding reports status `10` but must not stop the site's primary crawler or publishing job.

### Design or migrate the data architecture

1. Read [references/data-architecture-guidebook.md](references/data-architecture-guidebook.md).
2. Produce a data ownership matrix for every file: authoritative archive, private runtime/cache, index/locator, public projection, deploy artifact, log, or secret.
3. Choose day, month, or another partition from write and read patterns—not from habit.
4. Give each list consumer a bounded, rebuildable snapshot when its quota or filter differs. Read exact shards for details and historical lookups.
5. Define retention, permissions, lock order, atomic-write order, index repair, backup, and recovery before migration.
6. Migrate in two phases: build and validate the new shape while retaining legacy data; switch all readers and verify; then back up and remove legacy files in a separate cleanup step.

## Required audit behavior

- Observe dated files from the first eligible run, even before their record span reaches the reporting threshold.
- Compare against a baseline old enough to measure a trend.
- Classify an advancing oldest date as a sliding window, even if the file is currently filling and becoming larger.
- Classify a pinned oldest date with insignificant or negative growth as steady, not accumulating.
- Exempt filenames that are already explicit period shards such as `YYYY-MM.json` and `YYYY-MM-DD.json`; audit their directory/index design separately.
- Measure actual byte growth over actual elapsed time and show the projected size at the selected retention horizon.
- State sampling limits. ISO-date sampling cannot prove that binary databases, compressed archives, unsorted records, or files without recognizable dates are bounded.
- Never delete, truncate, repartition, upload, or change cron while performing an audit-only request.

## Architecture invariants

- Put credentials, cursors, raw scrape caches, review state, locks, logs, queues, and repair backups outside the public web root.
- Treat archives as authority and snapshots as disposable projections. A snapshot must be rebuildable from authoritative data.
- Bound every mutable single file by time, count, key cardinality, or a combination with an explicit rule.
- Keep list reads cheap: a frontend should normally load one bounded projection per consumer, not fan out across years of shards.
- Keep detail reads precise: use stable IDs, indexes, event dates, and source locators to open only the required shards.
- Preserve full referenced records needed by details, including nested references, localization fields, and media locators when applicable.
- Write data atomically in the same directory, validate before rename, and update shard contents before publishing an index that points to them.
- Protect server-generated data and marked HTML regions from static deploy packages.

## Safety rules

- Never put real hostnames, usernames, emails, credentials, local home paths, private logs, state files, or data samples into reusable skill files or public commits.
- Do not store the guard state under the scanned public root.
- Do not infer confidentiality from filename or permissions alone; verify which process and audience own the data.
- Do not claim that a file is unbounded from one size reading or one date span.
- Do not bypass access controls to inspect a server. Use existing authorized SSH, mounted storage, control-panel export, or user-provided evidence.
- Do not install a second scheduler when an existing wrapper can safely invoke the checker.
- Do not send a success email every run. Notify only on confirmed growth or checker failure, using sanitized output.

## Resources

- `scripts/check_data_growth.py`: persistent, dependency-free growth observer with text, Markdown, and JSON reports.
- `scripts/scaffold_data_growth_guard.py`: dry-run-first generator for a private checker directory, locked wrapper, and cron example.
- `references/growth-audit-runbook.md`: server audit and reporting procedure.
- `references/guard-deployment.md`: deployment, scheduling, notification, validation, and recovery guidance.
- `references/data-architecture-guidebook.md`: public/private boundaries, partition selection, indexes, snapshots, readers, retention, and migration patterns.

Combine this skill with `$cron-crawler-safety` when the surrounding crawler also needs source throttling, retry limits, failure-only alerts, or deploy protection.
