# Data Architecture Guidebook

## Contents

1. Start with ownership and access patterns
2. Public and private domains
3. Authoritative history and partitions
4. Indexes and locators
5. Frontend snapshots
6. Reader patterns
7. Writes, locks, and atomicity
8. Retention, media, and deletion
9. Migration
10. Review checklist

## 1. Start with ownership and access patterns

Classify every stored object before choosing a filename:

| Class | Purpose | Authority | Typical location | Bound |
| --- | --- | --- | --- | --- |
| Raw acquisition cache | Retry/merge/dedup source responses | Private operational input | Outside web root | Short time window |
| Canonical history | Durable records used by details/audits | Authoritative | Public or private by audience | Period shards + retention |
| Review/runtime state | Cursors, failures, prompts, queues, locks | Private control state | Outside web root | Key/count/time cap |
| Index/locator | Maps dates/IDs to shards | Derived from history | Beside readable shards | One entry per retained shard/record |
| Frontend snapshot | Cheap list/home/search seed | Disposable projection | Public web root | Consumer quota/window |
| Static detail | Permanent rendered record when required | Durable publication | Public route/archive | Explicit permanence policy |
| Logs/backups | Operations and recovery | Private | Outside web root | Short retention |
| Build/deploy artifact | Code and static assets | Reproducible | Build/staging | Generational cleanup |

For each class, document writer, readers, update cadence, retention, permissions, deletion authority, and recovery source.

## 2. Public and private domains

Put only browser-readable data in the public domain. Never expose:

- credentials or environment files;
- raw acquisition responses that were not selected for publication;
- incremental cursors and source failure state;
- prompts, model diagnostics, review queues, locks, logs, or repair backups;
- user/account data not explicitly public;
- notification recipients or server paths.

Private directories should normally be `0700` and private files `0600`. Public JSON normally needs only web-server readability. Permissions are defense in depth; the web-root boundary and server routing remain primary.

A public snapshot must not become the only copy of authoritative data. It may be deleted and rebuilt without losing history.

## 3. Authoritative history and partitions

Choose a partition from access patterns:

### Day shards

Use when writes are frequent and readers can derive an exact event/source date, such as feeds, evidence records, messages, audit events, or per-account activity.

Advantages:

- precise detail reads;
- small repair scope;
- simple rolling retention;
- low collision between writers.

Costs:

- long-range search needs an index and progressive/batched reads or a server query;
- quiet entities may need many dates to satisfy count-based lists.

### Month shards

Use for lower-volume histories, reports, aggregates, or readers that commonly request a whole month.

Advantages:

- fewer files and requests;
- natural reporting unit.

Costs:

- wider rewrite/repair scope;
- detail reads download more unrelated records;
- a rolling 30-day writer must merge, not replace, the partially overlapping month.

### Other periods

Use hours for very high volume, years for very low immutable data, or key/hash partitions when time is not the main locator. Document the reason and maximum expected shard size.

Do not use one growing `history.json` merely because it is easy for the first reader. Do not duplicate the same authoritative history in day and month shards without a declared source of truth and deterministic rebuild path.

Each shard must preserve the complete record required by future detail readers, including stable ID, timestamps, source locator, translations/localizations, nested/quoted records, and media locators when those are part of the product contract.

## 4. Indexes and locators

Indexes make shards usable without directory scans. Common fields:

```json
{
  "schemaVersion": 1,
  "generatedAt": "ISO-8601",
  "shards": [
    {"date": "YYYY-MM-DD", "file": "YYYY-MM-DD.json", "count": 123}
  ],
  "records": {
    "stable-id": {"file": "YYYY-MM-DD.json"}
  }
}
```

Rules:

- use stable IDs, not array positions;
- keep shard paths relative and reject traversal;
- rebuild indexes from disk when possible;
- write the shard first, then publish an index that points to it;
- remove index entries when retention removes shards;
- preserve redirects/aliases separately when old public URLs must remain valid;
- validate that every index target exists and every retained shard is represented.

Derive locators from record metadata when possible. For example, a source event ID may encode time, or a detail page may embed category/date attributes. Do not hardcode a single account or date when one detail can reference several sources across accounts and dates.

## 5. Frontend snapshots

A snapshot is a bounded projection tailored to one consumer. Examples:

- feed view: last 24 hours, then backfill each category to a minimum count;
- home news: last 120 hours, globally newest 100;
- specialist widget: five records matching a domain filter;
- account monitor: current 24-hour rows, then backfill each account to ten;
- search seed: only already-visible rows, with history loaded progressively from shards.

Create separate snapshots when consumers have different filters or quotas. A single universal snapshot tends either to omit required data or to become another unbounded history file.

Snapshot rules:

- encode the exact bound in code and docs;
- include generation/source batch metadata without manufacturing false “new” states on rebuild;
- deep-copy complete display records rather than storing references to private caches;
- generate atomically from authoritative shards;
- optionally publish a precompressed sibling when the host does not compress JSON dynamically;
- exclude protected/private entities before publication, not only in frontend CSS;
- record boundary metadata when progressive history reads must avoid reloading already covered shards;
- treat a missing snapshot as a degraded list, not a reason to delete history.

## 6. Reader patterns

### List pages

Read one consumer-specific snapshot. Avoid N-account × N-day startup fan-out.

### Detail pages

Use a stable detail ID and locator to read the exact narrative/event shard. Resolve every referenced source independently by owner/account and event date; one detail may require several shards.

### Historical date view

Read the exact date shard for each visible owner. Do not reinterpret a current snapshot as historical authority.

### Search

Search already displayed snapshot rows first. Then use indexes to read only the uncovered retention window, in batches. Keep new historical matches below already visible newer matches unless the UI explicitly promises relevance-only reordering. Cancel and reset search when leaving the search surface.

### Permanent static details

If a permanent page is required, render the durable baseline language/content into the HTML. Enhance other languages only when all required authoritative shards are available; avoid partially mixing languages or records. Keep stable asset references or a documented archive migration strategy.

## 7. Writes, locks, and atomicity

- Acquire locks in one documented global order across jobs that share data.
- Build updates from the latest live/authoritative state, not an old local download.
- Write a temp file in the destination directory, set permissions, validate schema/counts/references, then rename atomically.
- Preserve same-shard siblings during partial updates.
- For snapshot/index sets, publish data files first and indexes/manifests last.
- A failed partial translation/enrichment must not overwrite a previously complete record with an incomplete one.
- Rebuild disposable projections while the relevant data locks are held, or split projection rebuilds by ownership so unrelated locks are unnecessary.
- Deploy code/assets through an allowlist and protect cron-generated JSON, indexes, archives, and server-managed HTML regions.

## 8. Retention, media, and deletion

Define retention independently for:

- raw acquisition cache;
- canonical history;
- snapshots;
- logs;
- repair backups;
- media bytes;
- permanent details and redirects.

Snapshots need no historical retention beyond their current bound. Shards need a prune sweep that also reaches idle categories/accounts. A writer-only prune misses paused entities.

Media cleanup must use every durable public authority that still references a file: retained shards, permanent-page indexes, and other explicit archives. A short private scrape cache should not decide whether an older public image remains valid.

Deletion workflow:

1. resolve exact records and all derived files read-only;
2. take all locks needed by the write set;
3. back up material authoritative data;
4. update shard, index, snapshot, media references, static page, sitemap, and redirects as applicable;
5. validate no dangling references;
6. report what was removed and recovery location/retention.

## 9. Migration

Use two phases:

### Phase 1: Build without deleting

- freeze the target schema and ownership matrix;
- acquire writer locks;
- migrate legacy monoliths and all existing shards by union, not by current-window replacement;
- preserve metadata, nested references, redirects, and localization fields;
- validate counts, ID sets, exact detail reads, permissions, retention boundaries, and snapshot quotas;
- deploy readers that prefer the new shape while legacy data remains available.

### Phase 2: Clean up separately

- observe production readers and cron through at least one real write cycle;
- re-run completeness and dangling-reference audits;
- back up every legacy target;
- remove legacy readers first, then legacy files;
- keep one-time cleanup tools out of routine cron/deploy after completion;
- verify public routes, details, search, sitemap, media, and restore procedures.

Never let a static deploy upload a local copy of live production data. Fetch and merge current live state when a data repair is truly authorized.

## 10. Review checklist

- Does every mutable single file have an explicit bound?
- Is every public file intentionally public and free of private state?
- Can every snapshot be rebuilt from authoritative data?
- Can a detail resolve exact shards without scanning all history?
- Do indexes cover all retained shards and point only to existing files?
- Are long-range search and cold-list backfill progressive and bounded?
- Are nested references and localization/media fields preserved?
- Are writes atomic and lock order consistent?
- Does retention prune idle entities and repair index entries?
- Can deploys avoid overwriting server-generated data?
- Is migration reversible until the cleanup phase?
- Does the growth guard observe the new layout without reporting period shards as monoliths?
