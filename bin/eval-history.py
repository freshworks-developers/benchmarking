#!/usr/bin/env python3
"""Show evaluation history. Exit 0 success, 2 invalid args."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "history"] + sys.argv[1:]
    from bin.eval import main
    sys.exit(main())
