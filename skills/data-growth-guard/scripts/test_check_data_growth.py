#!/usr/bin/env python3
"""Synthetic regressions; no server access or production records."""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

import check_data_growth as guard
import scaffold_data_growth_guard as scaffold


class GrowthTests(unittest.TestCase):
    def item(self, oldest="2026-01-01", newest="2026-09-01", fields=("recorded_at",), size=2097152):
        return dict(path="synthetic-cache.json", oldest=oldest, newest=newest,
                    span_days=guard.days_between(oldest, newest), size=size,
                    mib=size / 1048576, date_basis=list(fields))

    def verdict(self, item, prior=None):
        prior = prior or [dict(at="2026-09-01", size=1048576, oldest="2026-01-01")]
        return guard.judge(item, prior + [dict(at="2026-10-01", size=item["size"], oldest=item["oldest"])],
                           span_warn_days=40, min_observe_days=14,
                           min_growth_mib_per_month=0.25, retention_days=1095)["verdict"]

    def test_quotes_are_not_record_dates(self):
        payload = json.dumps([dict(recorded_at="2026-09-30T01:00:00Z",
                                  text='quoted 2020-12-23 and 2031-09-09; "recorded_at": "2020-01-01"') for _ in range(8)]).encode()
        self.assertEqual(set(guard.dates_in(payload, ("recorded_at",))), {date(2026, 9, 30)})
        self.assertIn(date(2020, 12, 23), guard.dates_in(payload))

    def test_invalid_or_epoch_values_are_not_dates(self):
        payload = b'{"recorded_at":"2026-99-99","next":{"recorded_at":"2026-02-31"},"other":{"recorded_at":1788220800}}'
        self.assertEqual(guard.dates_in(payload, ("recorded_at",)), [])

    def test_head_tail_sampling_and_small_date_count(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cache.json"
            path.write_bytes(b'[' + b'{"recorded_at":"2026-01-01"},' * 4 + b'{"text":"'
                             + b'x' * (guard.SAMPLE_BYTES * 2 + 100) + b'"},'
                             + b','.join([b'{"recorded_at":"2026-09-01"}'] * 4) + b']')
            self.assertEqual(guard.sample_dates(path, path.stat().st_size, ("recorded_at",)),
                             (date(2026, 1, 1), date(2026, 9, 1)))
            path.write_text('{"recorded_at":"2026-09-01"}')
            self.assertIsNone(guard.sample_dates(path, path.stat().st_size, ("recorded_at",)))

    def test_verdicts(self):
        for item, expected in [(self.item(), "accumulating"),
                               (self.item(oldest="2026-02-01"), "sliding"),
                               (self.item(oldest="2020-01-01"), "changed"),
                               (self.item(fields=()), "unverified"),
                               (self.item(newest="2031-09-09"), "unverified"),
                               (self.item(size=524288), "steady"),
                               (self.item(oldest="2026-09-20", newest="2026-09-30"), "short")]:
            with self.subTest(expected=expected):
                self.assertEqual(self.verdict(item), expected)
        self.assertEqual(self.verdict(self.item(), [dict(at="2026-09-30", size=1048576, oldest="2026-01-01")]), "watching")

    def test_mixed_oldest_dates_not_pinned(self):
        prior = [dict(at="2026-09-01", size=1048576, oldest="2026-01-01"),
                 dict(at="2026-09-15", size=3145728, oldest="2026-02-01")]
        self.assertEqual(self.verdict(self.item(), prior), "changed")

    def test_date_basis_resets_state(self):
        state = {}
        guard.observe(state, self.item(fields=()), date(2026, 9, 1))
        self.assertEqual(len(guard.observe(state, self.item(), date(2026, 10, 1))), 1)
        legacy = {"files": {"synthetic-cache.json": {"observations": [dict(at="2026-09-01", size=1048576, oldest="2020-01-01")]}}}
        self.assertEqual(len(guard.observe(legacy, self.item(), date(2026, 10, 1))), 1)

    def test_cli_alert_and_discovery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "data"
            root.mkdir()
            cache = root / "cache.json"
            state = Path(directory) / "private" / "state.json"
            def run(day, fields):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    status = guard.main(["--root", str(root), "--state", str(state), "--min-mib", "0",
                                         "--format", "json", "--as-of", day] + fields)
                return status, json.loads(output.getvalue())
            def write(padding):
                cache.write_text(json.dumps([dict(recorded_at="2026-01-01" if index == 0 else "2026-09-01", text="2031-09-09 " + "x" * padding) for index in range(8)]))
            write(10)
            self.assertEqual(run("2026-09-01", ["--date-field", "recorded_at"])[0], 0)
            write(150000)
            self.assertEqual(run("2026-10-01", ["--date-field", "recorded_at"])[0], 10)
            self.assertEqual(state.stat().st_mode & 0o777, 0o600)
            status, report = run("2026-10-02", [])
            self.assertEqual(status, 0)
            self.assertEqual(report["records"][0]["verdict"], "unverified")
            (root / "2026-09.json").write_text(cache.read_text())
            self.assertEqual(run("2026-10-03", [])[1]["scanCounts"]["period_shard"], 1)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(guard.main(["--root", str(root), "--state", str(root / "state.json")]), 2)

    def test_scaffold_forwards_fields_and_quotes(self):
        wrapper = scaffold.wrapper_text(Path("/code/check.py"), Path("/data"), Path("/state"), "python3", 40, 1095,
                                        ["recorded_at", "event date"])
        self.assertIn("--date-field recorded_at --date-field 'event date'", wrapper)

    def test_generated_wrapper_runs_and_lock_skips(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root, code, state = (base / name for name in ("data", "code", "state"))
            root.mkdir()
            (root / "cache.json").write_text(json.dumps([dict(recorded_at="2026-01-01") for _ in range(8)]))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(scaffold.main(["--scan-root", str(root), "--output-dir", str(code), "--state-dir", str(state),
                                               "--date-field", "recorded_at", "--python-command", sys.executable, "--write"]), 0)
            wrapper = code / scaffold.WRAPPER_NAME
            self.assertEqual(subprocess.run(["sh", "-n", str(wrapper)]).returncode, 0)
            self.assertEqual(subprocess.run(["sh", str(wrapper)]).returncode, 0)
            self.assertTrue((state / "latest-report.md").exists())
            (state / "run.lock").mkdir()
            self.assertEqual(subprocess.run(["sh", str(wrapper)]).returncode, 0)
            self.assertEqual(state.stat().st_mode & 0o777, 0o700)

    def test_broken_state_warns_and_rebaselines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text("{broken")
            state, warnings = guard.load_state(path)
            self.assertEqual(state["files"], {})
            self.assertEqual(len(warnings), 1)


if __name__ == "__main__":
    unittest.main()
