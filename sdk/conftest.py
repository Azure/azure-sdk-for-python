# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import logging
import os
import pytest
import sys
from typing import TYPE_CHECKING
import urllib.parse as url_parse

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.transport import RequestsTransport
from devtools_testutils import test_proxy
from devtools_testutils.helpers import get_test_id, is_live, is_live_and_not_recording
from devtools_testutils.proxy_testcase import start_record_or_playback, stop_record_or_playback, transform_request

if TYPE_CHECKING:
    from typing import Any, Optional


def pytest_configure(config):
    # register an additional marker
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

try:
    from azure_devtools.scenario_tests import AbstractPreparer
    @pytest.fixture(scope='session', autouse=True)
    def clean_cached_resources():
        yield
        AbstractPreparer._perform_pending_deletes()
except ImportError:
    pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call) -> None:
    """Captures test exception info and makes it available to other fixtures."""
    # execute all other hooks to obtain the report object
    outcome = yield
    result = outcome.get_result()
    if result.outcome == "failed":
        error = call.excinfo.value
        # set a test_error attribute on the item (available to other fixtures from request.node)
        setattr(item, "test_error", error)


@pytest.fixture
def start_proxy_session() -> "Optional[tuple[str, str, dict[str, Any]]]":
    """Begins a playback or recording session and returns the current test ID, recording ID, and recorded variables.

    This returns a tuple, (a, b, c), where a is the test ID, b is the recording ID, and c is the `variables` dictionary
    that maps test variables to values. If no variable dictionary was stored when the test was recorded, c is an empty
    dictionary.
    """
    if sys.version_info.major == 2 and not is_live():
        pytest.skip("Playback testing is incompatible with the azure-sdk-tools test proxy on Python 2")

    if is_live_and_not_recording():
        return

    test_id = get_test_id()
    recording_id, variables = start_record_or_playback(test_id)
    return (test_id, recording_id, variables)


@pytest.fixture
def recorded_test(test_proxy, start_proxy_session, request) -> "dict[str, Any]":
    """Fixture that redirects network requests to target the azure-sdk-tools test proxy. Use with recorded tests.

    For more details and usage examples, refer to
    https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md.
    """
    test_id, recording_id, variables = start_proxy_session
    original_transport_func = RequestsTransport.send

    def transform_args(*args, **kwargs):
        copied_positional_args = list(args)
        http_request = copied_positional_args[1]

        transform_request(http_request, recording_id)

        return tuple(copied_positional_args), kwargs

    def combined_call(*args, **kwargs):
        adjusted_args, adjusted_kwargs = transform_args(*args, **kwargs)
        result = original_transport_func(*adjusted_args, **adjusted_kwargs)

        # make the x-recording-upstream-base-uri the URL of the request
        # this makes the request look like it was made to the original endpoint instead of to the proxy
        # without this, things like LROPollers can get broken by polling the wrong endpoint
        parsed_result = url_parse.urlparse(result.request.url)
        upstream_uri = url_parse.urlparse(result.request.headers["x-recording-upstream-base-uri"])
        upstream_uri_dict = {"scheme": upstream_uri.scheme, "netloc": upstream_uri.netloc}
        original_target = parsed_result._replace(**upstream_uri_dict).geturl()

        result.request.url = original_target
        return result

    RequestsTransport.send = combined_call

    # store info pertinent to the test in a dictionary that other fixtures can access
    variable_recorder = VariableRecorder(variables)
    test_info = {"test_id": test_id, "variables": variable_recorder}
    yield test_info  # yield and allow test to run

    RequestsTransport.send = original_transport_func  # test finished running -- tear down

    if hasattr(request.node, "test_error"):
        # Exceptions are logged here instead of being raised because of how pytest handles error raising from inside
        # fixtures and hooks. Raising from a fixture raises an error in addition to the test failure report, and the
        # test proxy error is logged before the test failure output (making it difficult to find in pytest output).
        # Raising from a hook isn't allowed, and produces an internal error that disrupts test execution.
        # ResourceNotFoundErrors during playback indicate a recording mismatch
        error = request.node.test_error
        if isinstance(error, ResourceNotFoundError):
            error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
            message = error_body.get("message") or error_body.get("Message")
            logger = logging.getLogger()
            logger.error(f"\n\n-----Test proxy playback error:-----\n\n{message}")

    stop_record_or_playback(test_id, recording_id, variables)


@pytest.fixture
def variable_recorder(recorded_test) -> "dict[str, Any]":
    """Fixture that invokes the `recorded_test` fixture and returns a dictionary of recorded test variables.

    The dictionary returned by this fixture maps test variables to values. If no variable dictionary was stored when the
    test was recorded, this returns an empty dictionary.
    """
    yield recorded_test["variables"]


class VariableRecorder():
    """Interface for fetching recorded test variables and recording new variables."""

    def __init__(self, variables: "dict[str, Any]") -> None:
        self.variables = variables

    def get(self, name: str) -> "Any":
        """Returns the value of the recorded variable with the provided name.

        :param str name: The name of the recorded variable. For example, "vault_name".
        """
        return self.variables.get(name)

    def record(self, variables: "dict[str, Any]") -> None:
        """Records the provided variables in the test recording, making them available for future playback.

        :param variables: A dictionary mapping variable names to their values.
        :type variables: dict[str, Any]
        """
        self.variables = variables
