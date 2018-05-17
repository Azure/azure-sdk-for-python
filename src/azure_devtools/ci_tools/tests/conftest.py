"""Configuration of fixtures for pytest"""
import logging
import os
import sys
import types

from github import Github

import pytest

_LOGGER = logging.getLogger(__name__)

collect_ignore = []
if sys.version_info < (3, 6):
    # Might do something more generic later
    collect_ignore.append("test_bot_framework.py")
    collect_ignore.append("test_git_tools.py")
    collect_ignore.append("test_github_tools.py")

_context = { 
    'login': "login",
    'password': "password",
    'oauth_token': os.environ.get('GH_TOKEN', 'oauth_token')
}
_test_context_module = types.ModuleType(
    'GithubCredentials',
    'Module created to provide a context for tests'
)
_test_context_module.__dict__.update(_context)
sys.modules['GithubCredentials'] = _test_context_module


@pytest.fixture
def github_token():
    """Return the Github token to use for real tests."""
    if not 'GH_TOKEN' in os.environ:
        _LOGGER.warning('GH_TOKEN must be defined for this test')
        return "faketoken"
    return os.environ['GH_TOKEN']

@pytest.fixture
def github_client(github_token):
    """Return a Github client with configured token."""
    return Github(github_token)
