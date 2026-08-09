#!/usr/bin/env python3
"""Generate a private, locked data-growth guard without installing cron.

Dry-run is the default. Pass --write after reviewing all resolved paths.
"""

from __future__ import annotations

import argparse
import os
import shlex
import sys
from pathlib import Path


CHECKER_NAME = "check_data_growth.py"
WRAPPER_NAME = "run_data_growth_guard.sh"
CRON_NAME = "cron.example"


def paths_overlap(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def shell_value(path: Path | str) -> str:
    return shlex.quote(str(path))


def atomic_write(path: Path, content: str, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    try:
        temp.write_text(content, encoding="utf-8")
        os.chmod(temp, mode)
        os.replace(temp, path)
        os.chmod(path, mode)
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def wrapper_text(
    checker: Path,
    scan_root: Path,
    state_dir: Path,
    python_command: str,
    span_warn_days: int,
    retention_days: int,
) -> str:
    return f"""#!/bin/sh
set -u
umask 077

CHECKER={shell_value(checker)}
SCAN_ROOT={shell_value(scan_root)}
STATE_DIR={shell_value(state_dir)}
PYTHON_BIN={shell_value(python_command)}
STATE_FILE="$STATE_DIR/observations.json"
REPORT_FILE="$STATE_DIR/latest-report.md"
ERROR_REPORT_FILE="$STATE_DIR/latest-error.md"
LOCK_DIR="$STATE_DIR/run.lock"

mkdir -p "$STATE_DIR" || exit 2
chmod 700 "$STATE_DIR" 2>/dev/null || true
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT INT TERM

TEMP_REPORT="$STATE_DIR/.report.tmp.$$"
"$PYTHON_BIN" "$CHECKER" \
  --root "$SCAN_ROOT" \
  --state "$STATE_FILE" \
  --span-warn-days {span_warn_days} \
  --retention-days {retention_days} \
  --format markdown > "$TEMP_REPORT" 2>&1
STATUS=$?

if [ "$STATUS" -eq 0 ] || [ "$STATUS" -eq 10 ]; then
  mv "$TEMP_REPORT" "$REPORT_FILE" || exit 2
  chmod 600 "$REPORT_FILE" 2>/dev/null || true
  if [ "$STATUS" -eq 10 ] && [ -n "${{DATA_GROWTH_FINDING_HOOK:-}}" ] \
     && [ -x "$DATA_GROWTH_FINDING_HOOK" ]; then
    "$DATA_GROWTH_FINDING_HOOK" "$REPORT_FILE" || true
  fi
  # A finding is operational debt, not a reason to break the site's main job.
  exit 0
fi

mv "$TEMP_REPORT" "$ERROR_REPORT_FILE" 2>/dev/null || true
chmod 600 "$ERROR_REPORT_FILE" 2>/dev/null || true
if [ -n "${{DATA_GROWTH_FAILURE_HOOK:-}}" ] && [ -x "$DATA_GROWTH_FAILURE_HOOK" ]; then
  "$DATA_GROWTH_FAILURE_HOOK" "$ERROR_REPORT_FILE" || true
fi
exit "$STATUS"
"""


def cron_text(wrapper: Path, state_dir: Path, weekday: int, hour: int) -> str:
    log_path = state_dir / "cron.log"
    return (
        "# Confirm the server timezone before installing.\n"
        "# Keep notification recipients in private hook configuration.\n"
        f"0 {hour} * * {weekday} {shell_value(wrapper)} >> {shell_value(log_path)} 2>&1\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Private directory for checker code and wrapper")
    parser.add_argument("--scan-root", type=Path, required=True,
                        help="Approved data root to inspect")
    parser.add_argument("--state-dir", type=Path, required=True,
                        help="Private runtime state/report directory")
    parser.add_argument("--python-command", default="python3")
    parser.add_argument("--weekday", type=int, choices=range(0, 7), default=0,
                        help="Cron weekday: 0=Sunday")
    parser.add_argument("--hour", type=int, choices=range(0, 24), default=4)
    parser.add_argument("--span-warn-days", type=int, default=40)
    parser.add_argument("--retention-days", type=int, default=365 * 3)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite generated files after reviewing/backing them up")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = args.output_dir.expanduser().resolve()
    scan_root = args.scan_root.expanduser().resolve()
    state_dir = args.state_dir.expanduser().resolve()
    if not scan_root.is_dir():
        print(f"[scaffold] scan root does not exist: {scan_root}", file=sys.stderr)
        return 2
    if paths_overlap(scan_root, output_dir) or paths_overlap(scan_root, state_dir):
        print("[scaffold] checker/state directories must be outside the scan root", file=sys.stderr)
        return 2
    if paths_overlap(output_dir, state_dir):
        print("[scaffold] keep checker code and runtime state in separate directories", file=sys.stderr)
        return 2

    source_checker = Path(__file__).resolve().with_name(CHECKER_NAME)
    if not source_checker.is_file():
        print(f"[scaffold] missing bundled checker: {source_checker}", file=sys.stderr)
        return 2

    checker = output_dir / CHECKER_NAME
    wrapper = output_dir / WRAPPER_NAME
    cron = output_dir / CRON_NAME
    outputs = [checker, wrapper, cron]
    existing = [path for path in outputs if path.exists()]
    if args.write and existing and not args.force:
        print(f"[scaffold] refusing to overwrite: {existing[0]}", file=sys.stderr)
        return 2

    print(f"[scaffold] scan root : {scan_root}")
    print(f"[scaffold] code dir  : {output_dir}")
    print(f"[scaffold] state dir : {state_dir}")
    for path in outputs:
        action = "overwrite" if path.exists() else "create"
        print(f"[scaffold] {action:9s}: {path}")
    print("[scaffold] cron line:")
    print(cron_text(wrapper, state_dir, args.weekday, args.hour).splitlines()[-1])

    if not args.write:
        print("[scaffold] dry-run only; pass --write after reviewing these paths")
        return 0

    checker_content = source_checker.read_text(encoding="utf-8")
    atomic_write(checker, checker_content, 0o700)
    atomic_write(
        wrapper,
        wrapper_text(
            checker,
            scan_root,
            state_dir,
            args.python_command,
            max(0, args.span_warn_days),
            max(1, args.retention_days),
        ),
        0o700,
    )
    atomic_write(cron, cron_text(wrapper, state_dir, args.weekday, args.hour), 0o600)
    output_dir.chmod(0o700)
    print("[scaffold] generated files; cron was not installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
