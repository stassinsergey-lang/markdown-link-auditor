#!/usr/bin/env python3
"""Report missing local file links referenced by Markdown files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def broken_links(markdown_file: Path) -> list[tuple[str, Path]]:
    broken: list[tuple[str, Path]] = []
    text = markdown_file.read_text(encoding="utf-8")
    for raw_target in LINK_RE.findall(text):
        target = raw_target.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith(("mailto:", "#")):
            continue
        resolved = (markdown_file.parent / unquote(target)).resolve()
        if not resolved.exists():
            broken.append((raw_target, resolved))
    return broken


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()

    failures = 0
    for markdown_file in sorted(args.root.rglob("*.md")):
        for target, resolved in broken_links(markdown_file):
            failures += 1
            print(f"{markdown_file}: broken link {target!r} -> {resolved}")

    print(f"checked={len(list(args.root.rglob('*.md')))} broken={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
