"""Tests for lib.history."""
import json
import pytest
from pathlib import Path

import sys
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from lib.history import (
    append_from_result_file,
    read_history,
    summarize,
    get_history_path,
    get_results_dir,
)


def test_append_from_result_file(tmp_repo, fixture_criteria, fixture_history_line):
    """Append creates eval_history.jsonl with one line."""
    result_file = tmp_repo / "results" / "APP001_result.json"
    result_data = {
        "timestamp": "2026-01-01T12:00:00",
        "score": {"total_score": 85, "grade": "B", "percentage": 85.0},
        "validation": {"success": True},
    }
    result_file.write_text(json.dumps(result_data))
    append_from_result_file("APP001", result_file=result_file, repo_root=tmp_repo)
    history_path = get_history_path(tmp_repo)
    assert history_path.exists()
    lines = history_path.read_text().strip().split("\n")
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["app_id"] == "APP001"
    assert record["score"] == 85
    assert record["grade"] == "B"
    assert record["validation_success"] is True


def test_read_history_empty(tmp_repo):
    assert read_history(repo_root=tmp_repo) == []


def test_read_history_with_data(tmp_repo, fixture_history_line):
    history_path = get_history_path(tmp_repo)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(fixture_history_line) + "\n")
    records = read_history(repo_root=tmp_repo)
    assert len(records) == 1
    assert records[0]["app_id"] == "APP001"


def test_summarize_empty(tmp_repo):
    out = summarize(repo_root=tmp_repo)
    assert "No evaluation history" in out


def test_summarize_with_fixture(tmp_repo, fixture_history_line):
    history_path = get_history_path(tmp_repo)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(fixture_history_line) + "\n")
    out = summarize(repo_root=tmp_repo)
    assert "APP001" in out
    assert "B" in out


def test_summarize_json(tmp_repo, fixture_history_line):
    history_path = get_history_path(tmp_repo)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(fixture_history_line) + "\n")
    out = summarize(as_json=True, repo_root=tmp_repo)
    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["app_id"] == "APP001"
