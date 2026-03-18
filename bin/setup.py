#!/usr/bin/env python3
"""Setup app slot: create test-criteria and test-apps dir. Requires --criteria-file (non-interactive). Exit 0 success, 1 failure, 2 invalid args."""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    p = argparse.ArgumentParser(description="Setup test criteria and app directory (non-interactive)")
    p.add_argument("app_id", help="App ID (e.g. APP001)")
    p.add_argument("--criteria-file", required=True, help="Path to criteria JSON file")
    p.add_argument("--app-path", help="Path to existing app to copy into test-apps/")
    args = p.parse_args()
    criteria_path = Path(args.criteria_file)
    if not criteria_path.exists():
        print(f"Criteria file not found: {criteria_path}", file=sys.stderr)
        return 2
    automate = REPO_ROOT / "setup_test.py"
    cmd = [sys.executable, str(automate), args.app_id, "--criteria-file", str(criteria_path)]
    if args.app_path:
        cmd.extend(["--app-path", args.app_path])
    r = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return 0 if r.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
