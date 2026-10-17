#!/usr/bin/env python3
"""CLI entry for skill-lint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .linter import lint_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Security + frontmatter linter for Agent Skills")
    parser.add_argument("path", type=Path, help="Path to SKILL.md or skill directory")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    args = parser.parse_args()

    results = lint_path(args.path)
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            status = "PASS" if r["ok"] else "FAIL"
            print(f"[{status}] {r['check']}: {r['message']}")
        fails = sum(1 for r in results if not r["ok"])
        print(f"\n{len(results)} checks, {fails} failures")
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
