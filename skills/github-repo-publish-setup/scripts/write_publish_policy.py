#!/usr/bin/env python3
import argparse
from pathlib import Path

BLOCK = """<!-- codex-github-publish-policy:start -->
## GitHub Publish Discipline

- Do not create or switch branches unless the user explicitly asks for a branch or PR.
- For "commit", "push", or "publish" requests, default to the repository's intended target branch, usually `main`.
- Before staging or committing, run `git branch --show-current` and `git status --short`.
- Stage only files related to the current task.
- Never commit secrets, local deploy credentials, `.env` files, cookies, mailbox passwords, or production-only private data.
- If unrelated changes exist, ask before staging them.
<!-- codex-github-publish-policy:end -->
"""

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    path = root / "AGENTS.md"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    start = "<!-- codex-github-publish-policy:start -->"
    end = "<!-- codex-github-publish-policy:end -->"
    if start in current and end in current:
        before = current.split(start)[0]
        after = current.split(end, 1)[1]
        path.write_text(before + BLOCK + after.lstrip("\n"), encoding="utf-8")
    else:
        suffix = "" if current.endswith("\n") or current == "" else "\n"
        path.write_text(current + suffix + BLOCK, encoding="utf-8")
    print(f"updated {path}")

if __name__ == "__main__":
    main()

