"""Tests for bin scripts: --help exits 0, invalid args exit 2."""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "bin"


def run_bin(script: str, args: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BIN / script)] + args,
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("script", ["eval.py", "eval-results.py", "eval-history.py", "eval-status.py", "setup.py", "convert-criteria.py", "learn-stats.py", "learn-suggest.py"])
def test_bin_help(script):
    if script == "eval.py":
        r = run_bin(script, ["--help"])
    elif script == "setup.py":
        r = run_bin(script, ["--help"])
    elif script == "convert-criteria.py":
        r = run_bin(script, ["--help"])
    else:
        r = run_bin(script, ["--help"])
    assert r.returncode == 0, (r.stderr or r.stdout)


def test_eval_run_missing_arg():
    """eval run with no app_id_or_path should exit 2."""
    r = run_bin("eval.py", ["run"])
    assert r.returncode == 2


def test_eval_results_help():
    r = run_bin("eval-results.py", ["--help"])
    assert r.returncode == 0


def test_eval_history_help():
    r = run_bin("eval-history.py", ["--help"])
    assert r.returncode == 0


def test_setup_missing_criteria_file():
    """setup requires --criteria-file."""
    r = run_bin("setup.py", ["APP001"])
    assert r.returncode == 2


def test_convert_criteria_missing_output():
    """convert-criteria requires --output."""
    r = run_bin("convert-criteria.py", ["--file", "/nonexistent"])
    assert r.returncode == 2
