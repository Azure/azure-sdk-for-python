# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import requests

from azure_devtools.scenario_tests.config import TestConfig
from .config import PROXY_URL


def is_live():
    """A module version of is_live, that could be used in pytest marker."""
    if not hasattr(is_live, "_cache"):
        is_live._cache = TestConfig().record_mode
    return is_live._cache


def send_proxy_matcher_request(matcher, headers):
    # type: (str, Dict) -> None
    """Send a POST request to the test proxy endpoint to register the specified matcher.

    :param str matcher: The name of the matcher to set.
    :param dict headers: Headers for the matcher setting request, as a dictionary.
    """

    headers_to_send = {"x-abstraction-identifier": matcher}
    headers_to_send.update(headers)
    response = requests.post(
        "{}/Admin/SetMatcher".format(PROXY_URL),
        headers=headers_to_send,
    )


def send_proxy_sanitizer_request(sanitizer, parameters):
    # type: (str, Dict) -> None
    """Send a POST request to the test proxy endpoint to register the specified sanitizer.

    :param str sanitizer: The name of the sanitizer to add.
    :param dict parameters: The sanitizer constructor parameters, as a dictionary.
    """

    response = requests.post(
        "{}/Admin/AddSanitizer".format(PROXY_URL),
        headers={"x-abstraction-identifier": sanitizer, "Content-Type": "application/json"},
        json=parameters
    )


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
