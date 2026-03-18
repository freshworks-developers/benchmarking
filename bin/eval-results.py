#!/usr/bin/env python3
"""Show result file path or list results. Exit 0 success, 1 not found, 2 invalid args."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

if __name__ == "__main__":
    # Invoke dispatcher with "results" subcommand
    sys.argv = [sys.argv[0], "results"] + sys.argv[1:]
    from bin.eval import main
    sys.exit(main())
