import os
import pytest
import shutil
from tempfile import mkdtemp

from ci_tools.snippet_update.python_snippet_updater import (
    get_snippet,
    update_snippet,
    check_snippets,
    check_not_up_to_date,
)

scenario = os.path.join(os.path.dirname(__file__), "integration", "scenarios", "snippet-updater")


def create_temp_directory_from_template(input_directory: str) -> str:
    """
    Create a temporary directory from a template directory.
    Args:
        input_directory (str): The path to the input directory to copy.
    Returns:
        str: The path to the newly created temporary directory.
    """
    temp_dir = mkdtemp()
    shutil.copytree(input_directory, temp_dir, dirs_exist_ok=True)
    return temp_dir


def test_get_snippet():
    folder = scenario
    file = os.path.join(folder, "example_async.py")
    get_snippet(file)
    snippets = check_snippets().keys()
    assert len(snippets) == 7
    assert "example_async.trio" in snippets
    assert "example_async.async_retry_policy" in snippets


def test_update_snippet():
    folder = create_temp_directory_from_template(scenario)
    file = os.path.join(folder, "example_async.py")
    get_snippet(file)
    file_1 = os.path.join(folder, "README.md")
    update_snippet(file_1)


def test_missing_snippet():
    folder = create_temp_directory_from_template(scenario)
    file = os.path.join(folder, "example_async.py")
    get_snippet(file)
    file_1 = os.path.join(folder, "README_missing_snippet.md")
    with pytest.raises(SystemExit):
        update_snippet(file_1)


def test_out_of_sync():
    folder = create_temp_directory_from_template(scenario)
    file = os.path.join(folder, "example_async.py")
    get_snippet(file)
    file_1 = os.path.join(folder, "README_out_of_sync.md")
    update_snippet(file_1)
    not_up_to_date = check_not_up_to_date()
    assert not_up_to_date
