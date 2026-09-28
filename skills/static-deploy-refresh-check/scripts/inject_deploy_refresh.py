#!/usr/bin/env python3
"""Inject a one-time deploy refresh check into static HTML files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


DEFAULT_MARKER = "DEPLOY_REFRESH_CHECK_V1"


def build_snippet(marker: str, version_param: str, storage_prefix: str) -> str:
    marker_comment = f"<!-- {marker} -->"
    version_param_js = json.dumps(version_param)
    storage_prefix_js = json.dumps(storage_prefix)
    return f"""{marker_comment}
    <script>
    (function () {{
      // Navigation Timing retains the loaded URL even if the app later calls pushState.
      var navigations = typeof performance !== 'undefined' && performance.getEntriesByType
        ? performance.getEntriesByType('navigation') : [];
      var loadedUrl = navigations.length && navigations[0].name || location.href;
      var entryUrl;
      try {{
        entryUrl = new URL(loadedUrl, location.href);
        if (entryUrl.origin !== location.origin) return;
        entryUrl.hash = '';
        entryUrl.searchParams.delete({version_param_js});
      }} catch (_error) {{
        return;
      }}
      var routeKey = {storage_prefix_js} + shortHash(entryUrl.pathname + entryUrl.search) + ':';
      var interacted = false;
      ['pointerdown', 'mousedown', 'click', 'keydown', 'compositionstart', 'input', 'change', 'submit',
        'wheel', 'touchstart', 'focusin', 'scroll']
        .forEach(function (name) {{
          document.addEventListener(name, function () {{ interacted = true; }}, {{ capture: true, passive: true }});
        }});

      function stillOnLoadedEntry() {{
        try {{
          var currentUrl = new URL(location.href);
          currentUrl.hash = '';
          currentUrl.searchParams.delete({version_param_js});
          return currentUrl.toString() === entryUrl.toString();
        }} catch (_error) {{
          return false;
        }}
      }}

      function shouldSkipRefresh() {{
        var active = document.activeElement;
        return !stillOnLoadedEntry() || interacted ||
          (document.visibilityState && document.visibilityState !== 'visible') ||
          (active && (active.isContentEditable || /^(INPUT|TEXTAREA|SELECT|IFRAME)$/i.test(active.tagName)));
      }}

      function normalizedLocalAsset(rawUrl, baseUrl) {{
        if (!rawUrl) return '';
        try {{
          var url = new URL(rawUrl, baseUrl);
          if (url.origin !== location.origin) return '';
          if (!/\\.(js|css)$/i.test(url.pathname)) return '';
          return url.pathname + url.search;
        }} catch (_error) {{
          return '';
        }}
      }}

      function signatureFromDocument(doc) {{
        var baseUrl = entryUrl;
        var baseNode = doc.querySelector('base[href]');
        if (baseNode) {{
          try {{ baseUrl = new URL(baseNode.getAttribute('href'), entryUrl); }} catch (_error) {{}}
        }}
        var values = [];
        doc.querySelectorAll('script[src],link[rel~="stylesheet"][href]').forEach(function (node) {{
          var value = normalizedLocalAsset(node.getAttribute('src') || node.getAttribute('href'), baseUrl);
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

      function cleanDeployVersionParam() {{
        try {{
          var url = new URL(location.href);
          if (!url.searchParams.has({version_param_js})) return;
          url.searchParams.delete({version_param_js});
          if (history && history.replaceState) {{
            history.replaceState(history.state, document.title, url.toString());
          }}
        }} catch (_error) {{}}
      }}

      function refreshOnce(version) {{
        if (shouldSkipRefresh()) return;
        var storageKey = routeKey + version;
        try {{
          if (sessionStorage.getItem(storageKey)) return;
          sessionStorage.setItem(storageKey, '1');
        }} catch (_error) {{
          return; // Without a persistent guard, automatic reload could loop.
        }}
        var url = new URL(entryUrl);
        url.searchParams.set({version_param_js}, version);
        location.replace(url.toString());
      }}

      function checkForDeployUpdate() {{
        if (shouldSkipRefresh()) return;
        var currentSignature = signatureFromDocument(document);
        if (!currentSignature) return;
        fetch(entryUrl.toString(), {{ cache: 'no-cache', credentials: 'same-origin' }})
          .then(function (response) {{
            if (!response.ok) throw new Error('deploy check failed');
            var finalUrl = new URL(response.url || entryUrl.toString(), entryUrl);
            if (finalUrl.origin !== entryUrl.origin || finalUrl.pathname !== entryUrl.pathname) {{
              throw new Error('deploy check redirected');
            }}
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
        cleanDeployVersionParam();
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


def inject_html(html: str, snippet: str, marker: str) -> tuple[str, str]:
    if marker in html:
        return html, "unchanged"
    if not re.search(r"</head>", html, flags=re.IGNORECASE):
        return html, "no-head"

    updated = re.sub(r"</head>", lambda match: snippet + "\n" + match.group(0), html, count=1, flags=re.IGNORECASE)
    return updated, "updated"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="HTML files or directories to scan")
    parser.add_argument("--write", action="store_true", help="write changes instead of dry-running")
    parser.add_argument("--include-extensionless", action="store_true", help="also scan extensionless HTML alias files")
    parser.add_argument("--marker", default=DEFAULT_MARKER, help="marker name used in the HTML comment")
    parser.add_argument("--version-param", default="__deploy_v", help="query parameter used for the one-time refresh")
    parser.add_argument("--storage-prefix", default="deploy-refresh:", help="sessionStorage key prefix")
    args = parser.parse_args()

    marker_text = f"<!-- {args.marker} -->"
    snippet = build_snippet(args.marker, args.version_param, args.storage_prefix)
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
