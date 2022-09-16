# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import os
import sys
import uuid

import pytest
from devtools_testutils import test_proxy
from devtools_testutils.sanitizers import add_remove_header_sanitizer, add_general_regex_sanitizer, set_custom_default_matcher


collect_ignore = []
collect_ignore.append("test_connection_string_parser*")
collect_ignore.append("test_message*")
collect_ignore.append("test_queues*")
collect_ignore.append("test_sb_client*")
collect_ignore.append("test_session*")
collect_ignore.append("test_topic*")
collect_ignore.append("test_subscriptions*")
collect_ignore.append("test_errors*")

@pytest.fixture(scope="session", autouse=True)
def add_aeg_sanitizer(test_proxy):
    set_custom_default_matcher(
        compare_bodies=False, excluded_headers="ServiceBusSupplementaryAuthorization,ServiceBusDlqSupplementaryAuthorization"
    )
    add_remove_header_sanitizer(headers="aeg-sas-key, aeg-sas-token")
    add_general_regex_sanitizer(
        value="fakeresource",
        regex="(?<=\\/\\/)[a-z-]+(?=\\.servicebus\\.windows\\.net)"
    )


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
