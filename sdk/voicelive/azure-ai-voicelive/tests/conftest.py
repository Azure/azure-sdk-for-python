"""
Pytest configuration for Azure AI Voice Live SDK tests.
"""

import pytest
import os
import base64
from devtools_testutils import test_proxy, is_live

from devtools_testutils.helpers import locate_assets
from pathlib import Path


def pytest_runtest_setup(item):
    is_live_only_test_marked = bool([mark for mark in item.iter_markers(name="live_test_only")])
    if is_live_only_test_marked:
        if not is_live():
            pytest.skip("live test only")

    is_playback_test_marked = bool([mark for mark in item.iter_markers(name="playback_test_only")])
    if is_playback_test_marked:
        if is_live():
            pytest.skip("playback test only")


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parent / "asset"


@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return
