#!/usr/bin/env python3
"""Convert plain text criteria to JSON. Reads from --file or stdin, writes to --output. Exit 0 success, 2 invalid args."""
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from lib.criteria_convert import plain_text_to_criteria


def main() -> int:
    p = argparse.ArgumentParser(description="Convert plain text criteria to JSON")
    p.add_argument("--file", "-f", help="Input plain text file (default: stdin)")
    p.add_argument("--stdin", action="store_true", help="Read from stdin")
    p.add_argument("--output", "-o", required=True, help="Output JSON file path")
    args = p.parse_args()
    if args.file:
        with open(args.file) as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()
    if not lines:
        print("No input", file=sys.stderr)
        return 2
    criteria = plain_text_to_criteria(lines)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(criteria, f, indent=2)
    if not getattr(args, "quiet", False):
        print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
