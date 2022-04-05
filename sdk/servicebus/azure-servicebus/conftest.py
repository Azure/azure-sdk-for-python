# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import os
import sys
import uuid

import pytest

collect_ignore = []

# Only run stress tests on request.
if not any([arg.startswith('test_stress') or arg.endswith('StressTest') for arg in sys.argv]):
    collect_ignore.append("stress/scripts")

# Allow us to pass stress_test_duration from the command line.
def pytest_addoption(parser):
    parser.addoption('--stress_test_duration_seconds', action="store", default=None)

# Note: This is duplicated between here and the basic conftest, so that it does not throw warnings if you're
# running locally to this SDK. (Everything works properly, pytest just makes a bit of noise.)
def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "markers", "liveTest: mark test to be a live test only"
    )
    config.addinivalue_line(
        "markers", "live_test_only: mark test to be a live test only"
    )
    config.addinivalue_line(
        "markers", "playback_test_only: mark test to be a playback test only"
    )
