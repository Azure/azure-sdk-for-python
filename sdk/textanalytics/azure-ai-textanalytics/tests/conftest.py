
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
import sys

# fixture needs to be visible from conftest
from testcase import text_analytics_account

# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("*_async.py")

def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "usefixtures", "text_analytics_account"
    )
    config.addinivalue_line(
        "markers", "live_test_only: mark test to be a live test only"
    )
    config.addinivalue_line(
        "markers", "playback_test_only: mark test to be a playback test only"
    )

def pytest_runtest_setup(item):
    is_live_only_test_marked = bool([mark for mark in item.iter_markers(name="live_test_only")])
    if is_live_only_test_marked:
        from devtools_testutils import is_live
        if not is_live():
            pytest.skip("live test only")

    is_playback_test_marked = bool([mark for mark in item.iter_markers(name="playback_test_only")])
    if is_playback_test_marked:
        from devtools_testutils import is_live
        if is_live() and os.environ.get('AZURE_SKIP_LIVE_RECORDING', '').lower() == 'true':
            pytest.skip("playback test only")
