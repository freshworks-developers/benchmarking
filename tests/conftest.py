"""Pytest fixtures for benchmarking tests."""
import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def repo_root():
    """Benchmarking repo root (parent of tests/)."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def tmp_repo(tmp_path):
    """A temporary directory with test-apps and test-criteria layout."""
    (tmp_path / "test-apps").mkdir()
    (tmp_path / "test-criteria").mkdir()
    (tmp_path / "results").mkdir()
    (tmp_path / "use-cases").mkdir()
    return tmp_path


@pytest.fixture
def fixture_criteria():
    """Minimal criteria JSON."""
    return {
        "requirements": ["OAuth 2.0", "Webhooks", "Platform 3.0"],
        "expected_files": ["manifest.json", "server/server.js", "config/requests.json"],
        "description": "Test app",
    }


@pytest.fixture
def fixture_history_line():
    """One line of eval_history.jsonl."""
    return {
        "app_id": "APP001",
        "timestamp": "2026-01-01T12:00:00",
        "score": 85,
        "grade": "B",
        "validation_success": True,
        "result_file": "results/APP001_result.json",
    }
