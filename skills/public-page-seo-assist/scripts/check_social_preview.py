#!/usr/bin/env python3
"""Validate essential social-preview metadata in local or live HTML."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import random
import sys
import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen


CRAWLER_USER_AGENTS = (
    ("discord", "Discordbot/2.0"),
    ("telegram", "TelegramBot (like TwitterBot)"),
)


REQUIRED_META = (
    ("name", "description"),
    ("property", "og:type"),
    ("property", "og:url"),
    ("property", "og:title"),
    ("property", "og:description"),
    ("property", "og:locale"),
    ("property", "og:site_name"),
    ("name", "twitter:card"),
    ("name", "twitter:title"),
    ("name", "twitter:description"),
)


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.title = ""
        self.meta: dict[tuple[str, str], list[str]] = {}
        self.canonical: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        if tag.lower() == "title":
            self.in_title = True
        elif tag.lower() == "meta":
            for key in ("name", "property"):
                label = values.get(key, "").lower()
                if label:
                    self.meta.setdefault((key, label), []).append(values.get("content", "").strip())
        elif tag.lower() == "link" and values.get("rel", "").lower() == "canonical":
            self.canonical.append(values.get("href", "").strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data


def read_target(target: str, user_agent: str | None = None) -> tuple[str, str]:
    parsed = urlparse(target)
    if parsed.scheme in {"http", "https"}:
        request = Request(target, headers={"User-Agent": user_agent or CRAWLER_USER_AGENTS[0][1]})
        with urlopen(request, timeout=20) as response:
            content_type = response.headers.get_content_type()
            if content_type != "text/html":
                raise ValueError(f"expected text/html, got {content_type}")
            return response.geturl(), response.read().decode("utf-8", errors="replace")
    path = Path(target)
    return str(path), path.read_text(encoding="utf-8")


def validate(label: str, html: str) -> list[str]:
    errors: list[str] = []
    head = html.lower().split("</head>", 1)[0]
    charset_index = head.find("charset=")
    if charset_index < 0 or charset_index > 1024:
        errors.append("UTF-8 charset is missing from the first 1024 head bytes")

    parser = HeadParser()
    parser.feed(html)
    if not parser.title.strip():
        errors.append("missing non-empty title")
    if len(parser.canonical) != 1 or not parser.canonical[0]:
        errors.append(f"expected one non-empty canonical, found {len(parser.canonical)}")
    for key in REQUIRED_META:
        values = parser.meta.get(key, [])
        if len(values) != 1 or not values[0]:
            errors.append(f"expected one non-empty {key[1]}, found {len(values)}")

    og_url = parser.meta.get(("property", "og:url"), [""])[0]
    if parser.canonical and og_url and parser.canonical[0] != og_url:
        errors.append("canonical and og:url differ")
    return [f"{label}: {message}" for message in errors]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("targets", nargs="+")
    args = parser.parse_args()
    failures: list[str] = []
    host_requests: dict[str, int] = {}
    for target in args.targets:
        try:
            parsed = urlparse(target)
            if parsed.scheme in {"http", "https"}:
                for crawler, user_agent in CRAWLER_USER_AGENTS:
                    host = parsed.netloc.lower()
                    request_count = host_requests.get(host, 0)
                    if request_count >= 3:
                        time.sleep(random.uniform(3, 10))
                    label, html = read_target(target, user_agent)
                    host_requests[host] = request_count + 1
                    failures.extend(validate(f"{label} [{crawler}]", html))
            else:
                label, html = read_target(target)
                failures.extend(validate(label, html))
        except Exception as exc:  # noqa: BLE001 - CLI should report each failed target.
            failures.append(f"{target}: {exc}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Social preview checks passed for {len(args.targets)} target(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
