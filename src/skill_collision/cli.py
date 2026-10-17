#!/usr/bin/env python3
"""CLI for skill-collision."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .detector import detect_collisions


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect name/description collisions among skills")
    parser.add_argument("--local", type=Path, required=True, help="Directory containing skill folders")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = detect_collisions(args.local)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Skills scanned: {report['scanned']}")
        if report["collisions"]:
            for c in report["collisions"]:
                print(f"COLLISION [{c['type']}] {c['a']} <-> {c['b']}: {c['detail']}")
        else:
            print("No collisions found.")
    return 0 if not report["collisions"] else 1


if __name__ == "__main__":
    sys.exit(main())
