#!/usr/bin/env python3
"""Generate a conservative cron wrapper for crawler jobs."""

from __future__ import annotations

import argparse
from pathlib import Path
import shlex


TEMPLATE = """#!/bin/sh
set -u

JOB_NAME={job_name_q}
APP_DIR={app_dir_q}
LOG_DIR={log_dir_q}
LOCK_DIR={lock_dir_q}
ALERT_TO=${{CRON_FAILURE_EMAIL:-}}
TIMEOUT_SECONDS={timeout_seconds}

PATH=/usr/local/bin:/usr/bin:/bin
export PATH

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$JOB_NAME.log"

log() {{
  printf '%s [%s] %s\\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$JOB_NAME" "$*" >> "$LOG_FILE"
}}

send_failure_mail() {{
  code="$1"
  if [ -z "$ALERT_TO" ]; then
    return 0
  fi
  {{
    printf 'To: %s\\n' "$ALERT_TO"
    printf 'Subject: [cron failed] %s\\n' "$JOB_NAME"
    printf 'Content-Type: text/plain; charset=UTF-8\\n'
    printf '\\n'
    printf 'Job: %s\\n' "$JOB_NAME"
    printf 'Host: %s\\n' "$(hostname 2>/dev/null || printf unknown)"
    printf 'Cwd: %s\\n' "$APP_DIR"
    printf 'Exit code: %s\\n' "$code"
    printf 'Time: %s\\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')"
    printf 'Log: %s\\n\\n' "$LOG_FILE"
    printf 'Recent log tail:\\n'
    tail -n 80 "$LOG_FILE" 2>/dev/null | sed -E 's/(password|token|secret|api[_-]?key|cookie|authorization)([=: ]+)[^ ]+/\\1\\2[redacted]/Ig'
  }} | /usr/sbin/sendmail -t
}}

cleanup() {{
  [ -d "$LOCK_DIR" ] && rmdir "$LOCK_DIR" 2>/dev/null || true
}}

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  log "skip: lock already held at $LOCK_DIR"
  exit 0
fi
trap cleanup EXIT INT TERM

cd "$APP_DIR" || {{
  log "failed: cannot cd to $APP_DIR"
  send_failure_mail 2
  exit 2
}}

log "start"

if command -v timeout >/dev/null 2>&1; then
  timeout "$TIMEOUT_SECONDS" sh -c {command_q} >> "$LOG_FILE" 2>&1
  code=$?
else
  sh -c {command_q} >> "$LOG_FILE" 2>&1
  code=$?
fi

if [ "$code" -ne 0 ]; then
  log "failed: exit=$code"
  send_failure_mail "$code"
  exit "$code"
fi

log "success"
exit 0
"""


def shell_quote(value: str) -> str:
    return shlex.quote(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a safe cron wrapper shell script.")
    parser.add_argument("--output", required=True, help="Wrapper path to create.")
    parser.add_argument("--job-name", required=True, help="Short job name for logs and alerts.")
    parser.add_argument("--app-dir", required=True, help="Working directory for the command.")
    parser.add_argument("--log-dir", required=True, help="Private log directory.")
    parser.add_argument("--lock-dir", required=True, help="Lock directory path.")
    parser.add_argument("--timeout-seconds", type=int, default=900, help="Whole command timeout when timeout(1) is available.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --.")
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("provide command after --")
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")

    script = TEMPLATE.format(
        job_name_q=shell_quote(args.job_name),
        app_dir_q=shell_quote(args.app_dir),
        log_dir_q=shell_quote(args.log_dir),
        lock_dir_q=shell_quote(args.lock_dir),
        timeout_seconds=args.timeout_seconds,
        command_q=shell_quote(" ".join(shlex.quote(part) for part in command)),
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(script, encoding="utf-8")
    output.chmod(0o755)
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
