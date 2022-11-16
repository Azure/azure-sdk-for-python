import os
import sys
import pytest
from ci_tools.snippet_update.python_snippet_updater import get_snippet, update_snippet, check_snippets, check_not_up_to_date


def test_get_snippet():
    folder = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(folder, "example_async.py")
    get_snippet(file)
    snippets = check_snippets().keys()
    assert len(snippets) == 7
    assert 'example_async.trio' in snippets
    assert 'example_async.async_retry_policy' in snippets

def test_update_snippet():
    folder = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(folder, "example_async.py")
    get_snippet(file)
    file_1 = os.path.join(folder, "README.md")
    update_snippet(file_1)

def test_missing_snippet():
    folder = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(folder, "example_async.py")
    get_snippet(file)
    file_1 = os.path.join(folder, "README_missing_snippet.md")
    with pytest.raises(SystemExit):
        update_snippet(file_1)

def test_out_of_sync():
    folder = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(folder, "example_async.py")
    get_snippet(file)
    file_1 = os.path.join(folder, "README_out_of_sync.md")
    update_snippet(file_1)
    not_up_to_date = check_not_up_to_date()
    assert not_up_to_date
