import os
import sys
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from eng.scripts.cleanup_isolate_dirs import cleanup_isolate_dirs, find_isolate_dirs


def test_find_isolate_dirs_returns_only_azpysdk_environments(tmp_path):
    isolate_root = tmp_path / ".venv"
    whl_dir = isolate_root / "azure-core" / ".venv_whl"
    versioned_dir = isolate_root / "azure-core" / ".venv_whl_py311"
    unrelated_dir = isolate_root / "azure-core" / "shared"
    root_environment = isolate_root / "repository-environment"
    for directory in (whl_dir, versioned_dir, unrelated_dir, root_environment):
        directory.mkdir(parents=True)

    assert find_isolate_dirs(os.fspath(tmp_path)) == sorted(
        [os.fspath(whl_dir), os.fspath(versioned_dir)]
    )


def test_cleanup_isolate_dirs_removes_isolates_and_preserves_other_directories(
    tmp_path,
):
    isolate_dir = tmp_path / ".venv" / "azure-core" / ".venv_whl"
    unrelated_dir = tmp_path / ".venv" / "azure-core" / "shared"
    isolate_dir.mkdir(parents=True)
    unrelated_dir.mkdir()

    assert cleanup_isolate_dirs(os.fspath(tmp_path)) == 0
    assert not isolate_dir.exists()
    assert unrelated_dir.exists()


def test_cleanup_isolate_dirs_succeeds_when_root_does_not_exist(tmp_path):
    assert cleanup_isolate_dirs(os.fspath(tmp_path)) == 0


def test_cleanup_isolate_dirs_reports_failures_and_continues(tmp_path):
    first_dir = tmp_path / ".venv" / "azure-core" / ".venv_whl"
    second_dir = tmp_path / ".venv" / "azure-core" / ".venv_sdist"
    first_dir.mkdir(parents=True)
    second_dir.mkdir()

    def remove_with_failure(path):
        if path == os.fspath(first_dir):
            raise OSError("directory is in use")
        os.rmdir(path)

    with patch(
        "eng.scripts.cleanup_isolate_dirs.shutil.rmtree",
        side_effect=remove_with_failure,
    ):
        assert cleanup_isolate_dirs(os.fspath(tmp_path)) == 1

    assert first_dir.exists()
    assert not second_dir.exists()
