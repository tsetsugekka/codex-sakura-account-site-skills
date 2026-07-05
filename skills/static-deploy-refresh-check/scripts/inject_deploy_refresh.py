#!/usr/bin/env python3
"""Inject a one-time deploy refresh check into static HTML files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


DEFAULT_MARKER = "DEPLOY_REFRESH_CHECK_V1"
REVALIDATION_META = (
    '<meta http-equiv="Cache-Control" content="no-cache, must-revalidate">',
    '<meta http-equiv="Pragma" content="no-cache">',
    '<meta http-equiv="Expires" content="0">',
)


def build_snippet(marker: str, check_param: str, version_param: str, storage_prefix: str) -> str:
    marker_comment = f"<!-- {marker} -->"
    check_param_js = json.dumps(check_param)
    version_param_js = json.dumps(version_param)
    storage_prefix_js = json.dumps(storage_prefix)
    return f"""{marker_comment}
    <script>
    (function () {{
      var storageKey = {storage_prefix_js} + location.pathname;

      function pageUrl() {{
        var pathname = location.pathname || '/';
        if (pathname.charAt(pathname.length - 1) === '/') {{
          pathname += 'index.html';
        }}
        var url = new URL(pathname, location.origin);
        url.searchParams.set({check_param_js}, String(Date.now()));
        return url.toString();
      }}

      function normalizedLocalAsset(rawUrl) {{
        if (!rawUrl) return '';
        try {{
          var url = new URL(rawUrl, location.href);
          if (url.origin !== location.origin) return '';
          var value = url.pathname + url.search;
          if (!/\\.(js|css)(\\?|$)/.test(value)) return '';
          return value;
        }} catch (_error) {{
          return '';
        }}
      }}

      function signatureFromDocument(doc) {{
        var values = [];
        doc.querySelectorAll('script[src],link[rel~="stylesheet"][href]').forEach(function (node) {{
          var value = normalizedLocalAsset(node.getAttribute('src') || node.getAttribute('href'));
          if (value) values.push(value);
        }});
        values.sort();
        return values.join('|');
      }}

      function shortHash(value) {{
        var hash = 2166136261;
        for (var index = 0; index < value.length; index += 1) {{
          hash ^= value.charCodeAt(index);
          hash = Math.imul(hash, 16777619);
        }}
        return (hash >>> 0).toString(36);
      }}

      function refreshOnce(version) {{
        try {{
          if (sessionStorage.getItem(storageKey) === version) return;
          sessionStorage.setItem(storageKey, version);
        }} catch (_error) {{
          // sessionStorage can be unavailable in private or restricted contexts.
        }}
        var url = new URL(location.href);
        url.searchParams.set({version_param_js}, version);
        location.replace(url.toString());
      }}

      function checkForDeployUpdate() {{
        var currentSignature = signatureFromDocument(document);
        if (!currentSignature) return;
        fetch(pageUrl(), {{ cache: 'no-store', credentials: 'same-origin' }})
          .then(function (response) {{
            if (!response.ok) throw new Error('deploy check failed');
            return response.text();
          }})
          .then(function (html) {{
            var latestDocument = new DOMParser().parseFromString(html, 'text/html');
            var latestSignature = signatureFromDocument(latestDocument);
            if (!latestSignature || latestSignature === currentSignature) return;
            refreshOnce(shortHash(latestSignature));
          }})
          .catch(function () {{}});
      }}

      function start() {{
        setTimeout(checkForDeployUpdate, 1200);
      }}

      if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', start, {{ once: true }});
      }} else {{
        start();
      }}
    }}());
    </script>"""


def looks_like_html(path: Path) -> bool:
    try:
        prefix = path.read_text(encoding="utf-8", errors="ignore")[:4096].lower()
    except OSError:
        return False
    return "<html" in prefix or "<!doctype html" in prefix or "</head>" in prefix


def iter_targets(paths: list[Path], include_extensionless: bool) -> list[Path]:
    targets: list[Path] = []
    for path in paths:
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if not child.is_file():
                    continue
                if child.suffix.lower() in {".html", ".htm"}:
                    targets.append(child)
                elif include_extensionless and child.suffix == "" and looks_like_html(child):
                    targets.append(child)
        elif path.is_file():
            if path.suffix.lower() in {".html", ".htm"}:
                targets.append(path)
            elif include_extensionless and path.suffix == "" and looks_like_html(path):
                targets.append(path)
        else:
            print(f"[missing] {path}", file=sys.stderr)
    return sorted(set(targets))


def has_http_equiv(html: str, name: str) -> bool:
    pattern = r"<meta\s+[^>]*http-equiv\s*=\s*['\"]?" + re.escape(name) + r"['\"]?[^>]*>"
    return re.search(pattern, html, flags=re.IGNORECASE) is not None


def missing_revalidation_meta(html: str) -> list[str]:
    missing: list[str] = []
    for name, tag in (
        ("Cache-Control", REVALIDATION_META[0]),
        ("Pragma", REVALIDATION_META[1]),
        ("Expires", REVALIDATION_META[2]),
    ):
        if not has_http_equiv(html, name):
            missing.append(tag)
    return missing


def inject_html(html: str, snippet: str, marker: str) -> tuple[str, str]:
    insertions = missing_revalidation_meta(html)
    if marker not in html:
        insertions.append(snippet)

    if not insertions:
        return html, "unchanged"
    if not re.search(r"</head>", html, flags=re.IGNORECASE):
        return html, "no-head"

    block = "\n".join(insertions)
    updated = re.sub(r"</head>", block + "\n</head>", html, count=1, flags=re.IGNORECASE)
    return updated, "updated"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="HTML files or directories to scan")
    parser.add_argument("--write", action="store_true", help="write changes instead of dry-running")
    parser.add_argument("--include-extensionless", action="store_true", help="also scan extensionless HTML alias files")
    parser.add_argument("--marker", default=DEFAULT_MARKER, help="marker name used in the HTML comment")
    parser.add_argument("--check-param", default="__deploy_check", help="query parameter used for no-store HTML checks")
    parser.add_argument("--version-param", default="__deploy_v", help="query parameter used for the one-time refresh")
    parser.add_argument("--storage-prefix", default="deploy-refresh:", help="sessionStorage key prefix")
    args = parser.parse_args()

    marker_text = f"<!-- {args.marker} -->"
    snippet = build_snippet(args.marker, args.check_param, args.version_param, args.storage_prefix)
    targets = iter_targets(args.paths, args.include_extensionless)
    if not targets:
        print("No HTML targets found.", file=sys.stderr)
        return 1

    changed = 0
    skipped = 0
    for target in targets:
        html = target.read_text(encoding="utf-8", errors="ignore")
        updated, status = inject_html(html, snippet, marker_text)
        if status == "updated":
            changed += 1
            if args.write:
                target.write_text(updated, encoding="utf-8")
                print(f"[updated] {target}")
            else:
                print(f"[would-update] {target}")
        elif status == "unchanged":
            skipped += 1
            print(f"[unchanged] {target}")
        else:
            skipped += 1
            print(f"[no-head] {target}", file=sys.stderr)

    mode = "updated" if args.write else "would update"
    print(f"Summary: {mode} {changed}, skipped {skipped}, scanned {len(targets)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
