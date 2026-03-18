#!/usr/bin/env python3
"""Print error learner statistics. Exit 0 success."""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTOMATE = REPO_ROOT / "automate_test.py"


def main() -> int:
    r = subprocess.run([sys.executable, str(AUTOMATE), "--show-stats"], cwd=str(REPO_ROOT))
    return 0 if r.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
