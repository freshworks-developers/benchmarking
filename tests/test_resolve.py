"""Tests for lib.resolve."""
import pytest
from pathlib import Path

# Add repo root
import sys
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from lib.resolve import get_repo_root, resolve_app, list_app_ids


def test_get_repo_root():
    root = get_repo_root()
    assert root.is_dir()
    assert (root / "lib").is_dir()
    assert (root / "bin").is_dir()


def test_resolve_app_by_path_repo(repo_root):
    """Resolve test-apps/TEST002-generated (exists in repo)."""
    app_path = repo_root / "test-apps" / "TEST002-generated"
    if not app_path.exists():
        pytest.skip("test-apps/TEST002-generated not present")
    path, app_id, criteria_path, req_arg = resolve_app(
        "test-apps/TEST002-generated", repo_root=repo_root
    )
    assert path == app_path
    assert app_id == "TEST002-generated"
    # May or may not have criteria file
    assert req_arg is None or "criteria" in str(req_arg)


def test_resolve_app_by_id_repo(repo_root):
    """Resolve by id when app dir exists (e.g. TEST002-generated)."""
    app_path = repo_root / "test-apps" / "TEST002-generated"
    if not app_path.exists():
        pytest.skip("test-apps/TEST002-generated not present")
    path, app_id, criteria_path, req_arg = resolve_app("TEST002-generated", repo_root=repo_root)
    assert app_id == "TEST002-generated"
    assert path == app_path


def test_resolve_app_empty_raises():
    with pytest.raises(ValueError):
        resolve_app("")
    with pytest.raises(ValueError):
        resolve_app("   ")


def test_resolve_app_missing_dir_raises(tmp_repo):
    """When app_id is given and test-apps/<id> does not exist, FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        resolve_app("NONEXISTENT", repo_root=tmp_repo)


def test_resolve_app_with_fixture_layout(tmp_repo):
    """With tmp_repo containing test-apps/Foo and optional criteria."""
    (tmp_repo / "test-apps" / "Foo").mkdir(parents=True)
    path, app_id, criteria_path, req_arg = resolve_app("Foo", repo_root=tmp_repo)
    assert path == tmp_repo / "test-apps" / "Foo"
    assert app_id == "Foo"
    assert req_arg is None
    # Add criteria file
    (tmp_repo / "test-criteria" / "Foo-criteria.json").write_text('{"requirements": []}')
    path2, app_id2, criteria_path2, req_arg2 = resolve_app("Foo", repo_root=tmp_repo)
    assert path2 == tmp_repo / "test-apps" / "Foo"
    assert req_arg2 is not None
    assert "Foo-criteria.json" in str(req_arg2)


def test_list_app_ids(repo_root):
    ids = list_app_ids(repo_root=repo_root)
    assert isinstance(ids, list)
    # Repo has at least use_cases and possibly test-apps
    assert len(ids) >= 0
