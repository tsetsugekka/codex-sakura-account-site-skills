#!/usr/bin/env python3
"""Observe dated files and report evidence of unbounded accumulation.

The checker does not use absolute size as the verdict. It compares observations:
an advancing oldest record is a sliding window, while a pinned oldest record plus
material byte growth is an accumulator. Period-named shards are already bounded
per file and are excluded from this particular check.

Exit codes:
  0  no confirmed accumulator
 10  one or more confirmed accumulators
  2  checker/configuration failure
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


ISO_DATE_RE = re.compile(rb"(20\d{2})-([01]\d)-([0-3]\d)")
PERIOD_STEM_RE = re.compile(
    r"^20\d{2}-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|[12]\d|3[01]))?$"
)
IGNORED_SUFFIXES = {
    ".br", ".css", ".gif", ".gz", ".htaccess", ".html", ".ico",
    ".jpeg", ".jpg", ".js", ".map", ".mp4", ".pdf", ".png",
    ".svg", ".webp", ".woff", ".woff2", ".zip",
}
IGNORED_DIRS = {
    ".git", "assets", "media", "node_modules", "repair_backups",
}
SAMPLE_BYTES = 4 * 1024 * 1024
MIN_RECOGNIZABLE_DATES = 8
STATE_KEEP = 40
STATE_FORGET_DAYS = 150


def parse_iso_date(value: str) -> date:
    return date.fromisoformat(value)


def days_between(earlier: str, later: str) -> int:
    return (parse_iso_date(later) - parse_iso_date(earlier)).days


def dates_in(chunk: bytes) -> list[date]:
    found: list[date] = []
    for year, month, day in ISO_DATE_RE.findall(chunk):
        try:
            found.append(date(int(year), int(month), int(day)))
        except ValueError:
            continue
    return found


def sample_dates(path: Path, size: int) -> tuple[date, date] | None:
    """Sample recognizable ISO dates from a regular file's head and tail."""
    try:
        with path.open("rb") as handle:
            if size <= SAMPLE_BYTES * 2:
                chunks = [handle.read()]
            else:
                chunks = [handle.read(SAMPLE_BYTES)]
                handle.seek(size - SAMPLE_BYTES)
                chunks.append(handle.read(SAMPLE_BYTES))
    except OSError:
        return None

    found = [item for chunk in chunks for item in dates_in(chunk)]
    if len(found) < MIN_RECOGNIZABLE_DATES:
        return None
    return min(found), max(found)


def scan_root(root: Path, min_bytes: int) -> tuple[list[dict[str, Any]], dict[str, int]]:
    items: list[dict[str, Any]] = []
    counts = {
        "regular": 0,
        "small": 0,
        "period_shard": 0,
        "ignored_type": 0,
        "undated_or_unsampled": 0,
        "sampled": 0,
    }

    for base, dir_names, file_names in os.walk(root, followlinks=False):
        dir_names[:] = [
            name for name in dir_names
            if name not in IGNORED_DIRS and not name.startswith(".")
        ]
        for name in file_names:
            path = Path(base) / name
            if path.is_symlink() or not path.is_file():
                continue
            counts["regular"] += 1
            if path.suffix.lower() in IGNORED_SUFFIXES:
                counts["ignored_type"] += 1
                continue
            if PERIOD_STEM_RE.fullmatch(path.stem):
                counts["period_shard"] += 1
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size < min_bytes:
                counts["small"] += 1
                continue
            sampled = sample_dates(path, size)
            if sampled is None:
                counts["undated_or_unsampled"] += 1
                continue
            oldest, newest = sampled
            counts["sampled"] += 1
            items.append({
                "path": str(path.resolve()),
                "root": str(root),
                "size": size,
                "mib": size / 1048576,
                "oldest": oldest.isoformat(),
                "newest": newest.isoformat(),
                "span_days": (newest - oldest).days,
            })

    return sorted(items, key=lambda item: item["size"], reverse=True), counts


def merge_counts(target: dict[str, int], source: dict[str, int]) -> None:
    for key, value in source.items():
        target[key] = target.get(key, 0) + value


def load_state(path: Path) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"schemaVersion": 1, "files": {}}, warnings
    except (OSError, ValueError) as error:
        warnings.append(f"Unreadable state; starting a new baseline: {error}")
        return {"schemaVersion": 1, "files": {}}, warnings
    if not isinstance(payload, dict) or not isinstance(payload.get("files"), dict):
        warnings.append("Invalid state schema; starting a new baseline")
        return {"schemaVersion": 1, "files": {}}, warnings
    return payload, warnings


def atomic_save_state(path: Path, state: dict[str, Any], today: date) -> None:
    files = state.setdefault("files", {})
    for key in list(files):
        entry = files.get(key)
        seen = entry.get("seen", "") if isinstance(entry, dict) else ""
        try:
            stale = not seen or days_between(seen, today.isoformat()) > STATE_FORGET_DAYS
        except (TypeError, ValueError):
            stale = True
        if stale:
            files.pop(key, None)

    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    try:
        temp.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        os.chmod(temp, 0o600)
        os.replace(temp, path)
        os.chmod(path, 0o600)
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def observe(state: dict[str, Any], item: dict[str, Any], today: date) -> list[dict[str, Any]]:
    entry = state.setdefault("files", {}).setdefault(item["path"], {})
    history = entry.get("observations", [])
    if not isinstance(history, list):
        history = []
    today_iso = today.isoformat()
    current = {
        "at": today_iso,
        "size": item["size"],
        "oldest": item["oldest"],
        "newest": item["newest"],
    }
    valid_history = []
    for past in history:
        if not isinstance(past, dict) or not {"at", "size", "oldest"} <= set(past):
            continue
        if str(past["at"]) < today_iso:
            valid_history.append(past)
    valid_history.append(current)
    entry["observations"] = valid_history[-STATE_KEEP:]
    entry["seen"] = today_iso
    return entry["observations"]


def judge(
    item: dict[str, Any],
    history: list[dict[str, Any]],
    *,
    span_warn_days: int,
    min_observe_days: int,
    min_growth_mib_per_month: float,
    retention_days: int,
) -> dict[str, Any]:
    if item["span_days"] < span_warn_days:
        return {"verdict": "short"}

    baseline = None
    for past in history[:-1]:
        try:
            elapsed = days_between(str(past["at"]), str(history[-1]["at"]))
        except (TypeError, ValueError):
            continue
        if elapsed >= max(1, min_observe_days):
            baseline = past
            break
    if baseline is None:
        return {"verdict": "watching"}

    elapsed = days_between(str(baseline["at"]), str(history[-1]["at"]))
    if item["oldest"] > str(baseline["oldest"]):
        return {
            "verdict": "sliding",
            "elapsed_days": elapsed,
            "oldest_moved_days": days_between(str(baseline["oldest"]), item["oldest"]),
            "baseline_at": baseline["at"],
        }

    gained_bytes = item["size"] - int(baseline["size"])
    gained_mib = gained_bytes / 1048576
    per_month = gained_mib / (elapsed / 30.44)
    common = {
        "elapsed_days": elapsed,
        "baseline_at": baseline["at"],
        "gained_bytes": gained_bytes,
        "gained_mib": gained_mib,
        "growth_mib_per_month": per_month,
    }
    if per_month < min_growth_mib_per_month:
        return {"verdict": "steady", **common}
    return {
        "verdict": "accumulating",
        **common,
        "projected_mib": item["mib"] + per_month * (retention_days / 30.44),
    }


def summarize_verdicts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = {name: 0 for name in ("short", "watching", "sliding", "steady", "accumulating")}
    for record in records:
        counts[record["verdict"]] += 1
    return counts


def markdown_report(report: dict[str, Any], limit: int) -> str:
    verdicts = report["verdictCounts"]
    scan = report["scanCounts"]
    lines = [
        "# Data Growth Report",
        "",
        f"Generated: `{report['generatedAt']}`",
        "",
        "## Scope and thresholds",
        "",
        f"- Roots: {', '.join(f'`{root}`' for root in report['roots'])}",
        f"- Minimum file size: {report['thresholds']['minMiB']:.2f} MiB",
        f"- Reporting record span: {report['thresholds']['spanWarnDays']} days",
        f"- Minimum baseline age: {report['thresholds']['minObserveDays']} days",
        f"- Meaningful growth: {report['thresholds']['minGrowthMiBPerMonth']:.2f} MiB/month",
        f"- Projection horizon: {report['thresholds']['retentionDays']} days",
        "",
        "## Summary",
        "",
        "| Classification | Count |",
        "| --- | ---: |",
        f"| Confirmed accumulating | {verdicts['accumulating']} |",
        f"| Sliding windows | {verdicts['sliding']} |",
        f"| Steady/shrinking | {verdicts['steady']} |",
        f"| Waiting for baseline | {verdicts['watching']} |",
        f"| Under reporting span | {verdicts['short']} |",
        f"| Explicit period shards skipped | {scan.get('period_shard', 0)} |",
        f"| Large undated/unsampled files | {scan.get('undated_or_unsampled', 0)} |",
        "",
        "## Confirmed accumulation",
        "",
    ]
    findings = [record for record in report["records"] if record["verdict"] == "accumulating"]
    findings.sort(key=lambda record: record.get("projected_mib", 0), reverse=True)
    if not findings:
        lines.append("No confirmed accumulator in this observation.")
    else:
        lines.extend([
            "| File | Current MiB | Span | Oldest | Growth MiB/month | Projected MiB |",
            "| --- | ---: | ---: | --- | ---: | ---: |",
        ])
        for item in findings[:limit]:
            lines.append(
                f"| `{item['path']}` | {item['mib']:.1f} | {item['span_days']}d | "
                f"{item['oldest']} | {item['growth_mib_per_month']:.2f} | "
                f"{item['projected_mib']:.0f} |"
            )
        if len(findings) > limit:
            lines.append(f"\n... and {len(findings) - limit} more confirmed findings.")

    lines.extend(["", "## Sampled files by verdict", ""])
    observed = sorted(
        report["records"],
        key=lambda item: (item["verdict"], -item["size"]),
    )
    if observed:
        lines.extend([
            "| Verdict | File | MiB | Oldest | Newest |",
            "| --- | --- | ---: | --- | --- |",
        ])
        for item in observed[:limit]:
            lines.append(
                f"| {item['verdict']} | `{item['path']}` | {item['mib']:.1f} | "
                f"{item['oldest']} | {item['newest']} |"
            )
        if len(observed) > limit:
            lines.append(f"\n... and {len(observed) - limit} more sampled files.")
    else:
        lines.append("No eligible dated files were sampled.")

    if report["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in report["warnings"])
    lines.extend([
        "",
        "## Interpretation",
        "",
        "A finding means the sampled oldest record stayed pinned while the file grew materially. "
        "Split it by period, shorten its retained window, or replace it with a bounded projection. "
        "Period shards and undated/binary formats still require a separate architecture review.",
        "",
    ])
    return "\n".join(lines)


def text_report(report: dict[str, Any], limit: int) -> str:
    verdicts = report["verdictCounts"]
    lines = [
        "[data-growth] "
        f"sampled={sum(verdicts.values())} "
        f"short={verdicts['short']} watching={verdicts['watching']} "
        f"sliding={verdicts['sliding']} steady={verdicts['steady']} "
        f"reported={verdicts['accumulating']}",
    ]
    findings = [record for record in report["records"] if record["verdict"] == "accumulating"]
    findings.sort(key=lambda record: record.get("projected_mib", 0), reverse=True)
    for item in findings[:limit]:
        lines.append(
            "[data-growth]   "
            f"{item['mib']:7.1f}MiB span={item['span_days']}d oldest={item['oldest']} "
            f"+{item['growth_mib_per_month']:.2f}MiB/month "
            f"projected={item['projected_mib']:.0f}MiB {item['path']}"
        )
    lines.extend(f"[data-growth] warning: {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", type=Path, required=True,
                        help="Approved directory to scan; may be repeated")
    parser.add_argument("--state", type=Path, required=True,
                        help="Private observation state outside every scanned root")
    parser.add_argument("--format", choices=("text", "markdown", "json"), default="text")
    parser.add_argument("--min-mib", type=float, default=1.0)
    parser.add_argument("--span-warn-days", type=int, default=40)
    parser.add_argument("--min-observe-days", type=int, default=14)
    parser.add_argument("--min-growth-mib-per-month", type=float, default=0.25)
    parser.add_argument("--retention-days", type=int, default=365 * 3)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--as-of", type=parse_iso_date, default=date.today(),
                        help="Observation date (YYYY-MM-DD); useful for controlled tests")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    roots = sorted({path.expanduser().resolve() for path in args.root}, key=str)
    missing = [root for root in roots if not root.is_dir()]
    if missing:
        print(f"[data-growth] missing root: {missing[0]}", file=sys.stderr)
        return 2
    state_path = args.state.expanduser().resolve()
    for root in roots:
        if state_path == root or root in state_path.parents:
            print(f"[data-growth] state must be outside scanned root: {state_path}", file=sys.stderr)
            return 2

    state, warnings = load_state(state_path)
    all_items: list[dict[str, Any]] = []
    scan_counts: dict[str, int] = {}
    for root in roots:
        items, counts = scan_root(root, max(0, int(args.min_mib * 1048576)))
        all_items.extend(items)
        merge_counts(scan_counts, counts)

    records = []
    for item in all_items:
        history = observe(state, item, args.as_of)
        verdict = judge(
            item,
            history,
            span_warn_days=max(0, args.span_warn_days),
            min_observe_days=max(1, args.min_observe_days),
            min_growth_mib_per_month=max(0.0, args.min_growth_mib_per_month),
            retention_days=max(1, args.retention_days),
        )
        records.append({**item, **verdict})

    try:
        atomic_save_state(state_path, state, args.as_of)
    except OSError as error:
        print(f"[data-growth] cannot write private state: {error}", file=sys.stderr)
        return 2

    report = {
        "schemaVersion": 1,
        "generatedAt": args.as_of.isoformat(),
        "roots": [str(root) for root in roots],
        "state": str(state_path),
        "thresholds": {
            "minMiB": args.min_mib,
            "spanWarnDays": args.span_warn_days,
            "minObserveDays": args.min_observe_days,
            "minGrowthMiBPerMonth": args.min_growth_mib_per_month,
            "retentionDays": args.retention_days,
        },
        "scanCounts": scan_counts,
        "verdictCounts": summarize_verdicts(records),
        "records": records,
        "warnings": warnings,
    }

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    elif args.format == "markdown":
        print(markdown_report(report, max(1, args.limit)), end="")
    else:
        print(text_report(report, max(1, args.limit)), end="")
    return 10 if report["verdictCounts"]["accumulating"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
