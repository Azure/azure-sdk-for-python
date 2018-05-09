"""Configuration of fixtures for pytest"""
import os
import sys

from github import Github

import pytest

collect_ignore = []
if sys.version_info < (3, 6):
    # Might do something more generic later
    collect_ignore.append("test_bot_framework.py")
    collect_ignore.append("test_git_tools.py")
    collect_ignore.append("test_github_tools.py")

@pytest.fixture
def github_token():
    """Return the Github token to use for real tests."""
    if not 'GH_TOKEN' in os.environ:
        raise RuntimeError('GH_TOKEN must be defined for this test')
    return os.environ['GH_TOKEN']

@pytest.fixture
def github_client(github_token):
    """Return a Github client with configured token."""
    return Github(github_token)
