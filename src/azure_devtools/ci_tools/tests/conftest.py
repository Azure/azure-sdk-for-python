"""Configuration of fixtures for pytest"""
import os

from github import Github

import pytest


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
