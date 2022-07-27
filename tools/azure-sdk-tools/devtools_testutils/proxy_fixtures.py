# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from inspect import iscoroutinefunction
import logging
from typing import TYPE_CHECKING
import urllib.parse as url_parse

import pytest

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy

# the functions we patch
from azure.core.pipeline.transport import RequestsTransport

from .helpers import get_test_id, is_live_and_not_recording
from .proxy_testcase import start_record_or_playback, stop_record_or_playback, transform_request
from .proxy_startup import test_proxy

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Optional, Tuple
    from pytest import FixtureRequest


@pytest.fixture
async def recorded_test(test_proxy: None, request: "FixtureRequest") -> "Dict[str, Any]":
    """Fixture that redirects network requests to target the azure-sdk-tools test proxy.

    Use with recorded tests. For more details and usage examples, refer to
    https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md.

    :param test_proxy: The fixture responsible for starting up the test proxy server.
    :type test_proxy: None
    :param request: The built-in `request` fixture.
    :type request: ~pytest.FixtureRequest

    :yields: A dictionary containing information relevant to the currently executing test.
    """

    test_id, recording_id, variables = start_proxy_session()

    # True if the function requesting the fixture is an async test
    if iscoroutinefunction(request._pyfuncitem.function):
        original_transport_func = await redirect_async_traffic(recording_id)
        yield {"variables": variables}  # yield relevant test info and allow tests to run
        restore_async_traffic(original_transport_func, request)
    else:
        original_transport_func = redirect_traffic(recording_id)
        yield {"variables": variables}  # yield relevant test info and allow tests to run
        restore_traffic(original_transport_func, request)

    stop_record_or_playback(test_id, recording_id, variables)


@pytest.fixture
def variable_recorder(recorded_test: "Dict[str, Any]") -> "Dict[str, str]":
    """Fixture that invokes the `recorded_test` fixture and returns a dictionary of recorded test variables.

    :param recorded_test: The fixture responsible for redirecting network traffic to target the test proxy.
        This should return a dictionary containing information about the current test -- in particular, the variables
        that were recorded with the test.
    :type recorded_test: Dict[str, Any]

    :returns: A dictionary that maps test variables to string values. If no variable dictionary was stored when the test
        was recorded, this returns an empty dictionary.
    """
    return VariableRecorder(recorded_test["variables"])


# ----------HELPERS----------


class VariableRecorder:
    def __init__(self, variables: "Dict[str, str]") -> None:
        self.variables = variables

    def get_or_record(self, variable: str, default: str) -> str:
        """Returns the recorded value of `variable`, or records and returns `default` as the value for `variable`.

        In recording mode, `get_or_record("a", "b")` will record "b" for the value of the variable `a` and return "b".
        In playback, it will return the recorded value of `a`. This is an analogue of a Python dictionary's `setdefault`
        method: https://docs.python.org/library/stdtypes.html#dict.setdefault.

        :param str variable: The name of the variable to search the value of, or record a value for.
        :param str default: The variable value to record.

        :returns: str
        """
        if not isinstance(default, str):
            raise ValueError('"default" must be a string. The test proxy cannot record non-string variable values.')
        return self.variables.setdefault(variable, default)


def start_proxy_session() -> "Optional[Tuple[str, str, Dict[str, str]]]":
    """Begins a playback or recording session and returns the current test ID, recording ID, and recorded variables.

    :returns: A tuple, (a, b, c), where a is the test ID, b is the recording ID, and c is the `variables` dictionary
        that maps test variables to string values. If no variable dictionary was stored when the test was recorded, c is
        an empty dictionary. If the current test session is live but recording is disabled, this returns None.
    """
    if is_live_and_not_recording():
        return

    test_id = get_test_id()
    recording_id, variables = start_record_or_playback(test_id)
    return (test_id, recording_id, variables)


async def redirect_async_traffic(recording_id: str) -> "Callable":
    """Redirects asynchronous network requests to target the test proxy.

    :param str recording_id: Recording ID of the currently executing test.

    :returns: The original transport function used by the currently executing test.
    """
    from azure.core.pipeline.transport import AioHttpTransport

    original_transport_func = AioHttpTransport.send

    def transform_args(*args, **kwargs):
        copied_positional_args = list(args)
        request = copied_positional_args[1]

        transform_request(request, recording_id)

        return tuple(copied_positional_args), kwargs

    async def combined_call(*args, **kwargs):
        adjusted_args, adjusted_kwargs = transform_args(*args, **kwargs)
        result = await original_transport_func(*adjusted_args, **adjusted_kwargs)

        # make the x-recording-upstream-base-uri the URL of the request
        # this makes the request look like it was made to the original endpoint instead of to the proxy
        # without this, things like LROPollers can get broken by polling the wrong endpoint
        parsed_result = url_parse.urlparse(result.request.url)
        upstream_uri = url_parse.urlparse(result.request.headers["x-recording-upstream-base-uri"])
        upstream_uri_dict = {"scheme": upstream_uri.scheme, "netloc": upstream_uri.netloc}
        original_target = parsed_result._replace(**upstream_uri_dict).geturl()

        result.request.url = original_target
        return result

    AioHttpTransport.send = combined_call
    return original_transport_func


def redirect_traffic(recording_id: str) -> "Callable":
    """Redirects network requests to target the test proxy.

    :param str recording_id: Recording ID of the currently executing test.

    :returns: The original transport function used by the currently executing test.
    """
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
    return original_transport_func


def restore_async_traffic(original_transport_func: "Callable", request: "FixtureRequest") -> None:
    """Resets asynchronous network traffic to no longer target the test proxy.

    :param original_transport_func: The original transport function used by the currently executing test.
    :type original_transport_func: Callable
    :param request: The built-in `request` pytest fixture.
    :type request: ~pytest.FixtureRequest
    """
    from azure.core.pipeline.transport import AioHttpTransport

    AioHttpTransport.send = original_transport_func  # test finished running -- tear down

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


def restore_traffic(original_transport_func: "Callable", request: "FixtureRequest") -> None:
    """Resets network traffic to no longer target the test proxy.

    :param original_transport_func: The original transport function used by the currently executing test.
    :type original_transport_func: Callable
    :param request: The built-in `request` pytest fixture.
    :type request: ~pytest.FixtureRequest
    """
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
