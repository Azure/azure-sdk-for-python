# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import sys

from azure_devtools.scenario_tests.config import TestConfig


# we store recording IDs in a module-level variable so that sanitizers can access them
# we map test IDs to recording IDs, rather than storing only the current test's recording ID, for parallelization
this = sys.modules[__name__]
this.recording_ids = {}


def get_recording_id():
    """Fetches the recording ID for the currently executing test"""
    test_id = get_test_id()
    return this.recording_ids.get(test_id)


def set_recording_id(test_id, recording_id):
    """Used to update a persistent dictionary, mapping test IDs to recording IDs, from outside this module"""
    this.recording_ids[test_id] = recording_id


def get_test_id():
    # type: () -> str
    # pytest sets the current running test in an environment variable
    # the path to the test can depend on the environment, so we can't assume this is the path from the repo root
    setting_value = os.getenv("PYTEST_CURRENT_TEST")
    path_to_test = os.path.normpath(setting_value.split(" ")[0])
    full_path_to_test = os.path.abspath(path_to_test)

    # walk up to the repo root by looking for "sdk" directory or root of file system
    path_components = []
    head, tail = os.path.split(full_path_to_test)
    while tail != "sdk" and tail != "":
        path_components.append(tail)
        head, tail = os.path.split(head)

    # reverse path_components to construct components of path from repo root: [sdk, ..., tests, {test}]
    path_components.append("sdk")
    path_components.reverse()
    for idx, val in enumerate(path_components):
        if val.startswith("test"):
            path_components.insert(idx + 1, "recordings")
            break

    return os.sep.join(path_components).replace("::", "").replace("\\", "/")


def is_live():
    """A module version of is_live, that could be used in pytest marker."""
    if not hasattr(is_live, "_cache"):
        is_live._cache = TestConfig().record_mode
    return is_live._cache


def is_live_and_not_recording():
    return is_live() and os.environ.get("AZURE_SKIP_LIVE_RECORDING", "").lower() == "true"


class RetryCounter(object):
    def __init__(self):
        self.count = 0

    def simple_count(self, retry_context):
        self.count += 1


class ResponseCallback(object):
    def __init__(self, status=None, new_status=None):
        self.status = status
        self.new_status = new_status
        self.first = True
        self.count = 0

    def override_first_status(self, response):
        if self.first and response.http_response.status_code == self.status:
            response.http_response.status_code = self.new_status
            self.first = False
        self.count += 1

    def override_status(self, response):
        if response.http_response.status_code == self.status:
            response.http_response.status_code = self.new_status
        self.count += 1
