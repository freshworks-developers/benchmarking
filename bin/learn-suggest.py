#!/usr/bin/env python3
"""Generate skill update suggestions from recorded errors. Exit 0 success."""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTOMATE = REPO_ROOT / "automate_test.py"


def main() -> int:
    r = subprocess.run(
        [sys.executable, str(AUTOMATE), "--generate-skill-updates"],
        cwd=str(REPO_ROOT),
    )
    return 0 if r.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
