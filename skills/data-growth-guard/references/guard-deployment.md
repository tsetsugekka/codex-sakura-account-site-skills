# Guard Deployment

## Contents

1. Deployment model
2. Scaffold workflow
3. Wrapper contract
4. Scheduling and notifications
5. Validation
6. Recovery and maintenance

## 1. Deployment model

Keep the guard in a private operations directory. Separate:

- checker code: deployable and version-controlled;
- observation state: private runtime data, mode `0600`;
- latest report: private operational output;
- lock: private runtime directory;
- cron log: private and retained;
- notification recipient/config: existing private site settings or environment.

Never place state, reports, locks, or notification configuration under the public web root.

## 2. Scaffold workflow

The scaffold script is dry-run by default:

```bash
python3 scripts/scaffold_data_growth_guard.py \
  --output-dir /path/to/private/jobs/data-growth-guard \
  --scan-root /path/to/approved/data \
  --state-dir /path/to/private/state/data-growth-guard
```

After reviewing the resolved paths and cron example, generate files:

```bash
python3 scripts/scaffold_data_growth_guard.py \
  --output-dir /path/to/private/jobs/data-growth-guard \
  --scan-root /path/to/approved/data \
  --state-dir /path/to/private/state/data-growth-guard \
  --write
```

It creates:

- `check_data_growth.py`;
- `run_data_growth_guard.sh`;
- `cron.example`.

The generator refuses overlapping public/state/script roots and refuses to overwrite existing files unless `--force` is explicitly supplied. Do not use `--force` until the existing guard has been reviewed and backed up.

## 3. Wrapper contract

The generated wrapper:

- uses an atomic directory lock;
- creates private state/report directories;
- writes a temporary Markdown report in the report directory;
- atomically replaces `latest-report.md` after checker exit `0` or `10`;
- returns `0` for no finding or lock skip;
- invokes an optional executable notification hook on finding or checker failure;
- does not use `eval` or embed credentials.

Notification hooks use these optional environment variables:

```text
DATA_GROWTH_FINDING_HOOK=/absolute/path/to/finding-hook
DATA_GROWTH_FAILURE_HOOK=/absolute/path/to/failure-hook
```

Each hook receives the report path as its only argument. Keep mail recipients and sender details inside the hook's existing private configuration, not in the generated wrapper.

## 4. Scheduling and notifications

Use the site's existing scheduler when possible. Weekly observation is usually sufficient for multi-year storage risk; faster-growing systems may choose daily. Running every few minutes does not create better daily evidence.

The generated `cron.example` defaults to Sunday at 04:00 local server time. Confirm the server timezone before installing it.

Notify on:

- status `10`: confirmed accumulation;
- status `2` or another unexpected non-zero status: checker failure.

Do not notify on:

- status `0`;
- first baseline only;
- short span;
- sliding window;
- steady file;
- lock skip.

Sanitize reports before email. They may contain private server paths even though the checker source is public-safe.

## 5. Validation

Test in a temporary directory before production integration:

1. First run creates one private baseline and reports no finding.
2. A synthetic file with a pinned oldest date and an old baseline grows enough to return `10`.
3. A file whose oldest date advances returns `0` and is classified `sliding`.
4. A period shard such as `2026-08.json` is skipped.
5. An undated large file is ignored and listed in blind-spot counts.
6. A state path inside the scan root is rejected.
7. Two wrapper runs cannot overlap.
8. State is `0600`; private directories are `0700`.
9. Finding hook fires once for a scheduled run; success and lock skip do not fire.
10. Broken JSON state starts a new baseline but emits a visible warning.

Run `python3 -m py_compile` and the repository's tests after changing the scripts.

## 6. Recovery and maintenance

- Back up observation state before changing path keys or scan roots; losing it delays a verdict but does not corrupt site data.
- Keep a bounded number of observations per file and forget paths not seen for a season.
- Treat renamed/moved files as new unless a deliberate migration carries their state.
- If false positives recur, fix the project adapter or recorded ownership contract. Do not merely raise thresholds until alerts disappear.
- If a confirmed accumulator is repartitioned, retain the old observation record long enough to document that growth stopped, then allow stale-state cleanup.
- Keep checker upgrades separate from data migration. The guard should observe the migration, not perform it.
