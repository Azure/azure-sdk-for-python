# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from inspect import iscoroutinefunction
import logging
import os
from typing import TYPE_CHECKING
import urllib.parse as url_parse

import pytest

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy

# the functions we patch
from azure.core.pipeline.transport import RequestsTransport

from .helpers import get_test_id, is_live, is_live_and_not_recording
from .proxy_testcase import start_record_or_playback, stop_record_or_playback, transform_request
from .proxy_startup import test_proxy
from .sanitizers import add_general_regex_sanitizer

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Optional, Tuple
    from pytest import FixtureRequest


_LOGGER = logging.getLogger()


class EnvironmentVariableSanitizer:
    def __init__(self) -> None:
        self._fake_values = {}

    def sanitize(self, variable: str, value: str) -> str:
        """Registers a sanitizer that replaces the value of the specified environment variable with the provided value.

        :param str variable: Name of the environment variable to sanitize.
        :param str value: Value to sanitize the environment variable's value with.

        :returns: The real value of `variable` in live mode, or the sanitized value in playback.
        """
        self._fake_values[variable] = value
        real_value = os.getenv(variable)
        if real_value:
            add_general_regex_sanitizer(regex=real_value, value=value)
        else:
            _LOGGER.info(f"No value for {variable} was found, so a sanitizer could not be registered for the variable.")

        return real_value if is_live() else value

    def sanitize_batch(self, variables: "Dict[str, str]") -> "Dict[str, str]":
        """Registers sanitizers that replace the values of multiple environment variables with the provided values.

        :param variables: A dictionary mapping environment variable names to values they should be sanitized with.
            For example: {"SERICE_CLIENT_ID": "fake_client_id", "SERVICE_ENDPOINT": "https://fake-endpoint.azure.net"}

        :returns: A dictionary mapping environment variables to their real values in live mode, or their sanitized
            values in playback.
        """
        current_values = {variable: self.sanitize(variable, variables[variable]) for variable in variables}
        return current_values


    def get(self, variable: str) -> str:
        """Returns the value of the specified environment variable in live mode, or the sanitized value in playback.

        :param str variable: Name of the environment variable to fetch the value of.

        :returns: The real value of `variable` in live mode, or the sanitized value in playback.
        """
        return os.getenv(variable) if is_live() else self._fake_values.get(variable)


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


@pytest.fixture
def environment_variables(test_proxy: None) -> EnvironmentVariableSanitizer:
    """Fixture that returns an EnvironmentVariableSanitizer for convenient environment variable fetching and sanitizing.

    :param test_proxy: The fixture responsible for starting up the test proxy server.
    :type test_proxy: None

    :returns: An EnvironmentVariableSanitizer object. Calling:
        - `sanitize(a, b)` will sanitize the value of environment variable `a` with value `b`
        - `sanitize_batch(dict)` will sanitize the values of all variables in dictionary `dict`
        - `get(a)` will return the value of environment variable `a` in the current context (live or playback mode)
        See the definition of EnvironmentVariableSanitizer in
        https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/proxy_fixtures.py
        for more details.
    """
    return EnvironmentVariableSanitizer()


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
def variable_recorder(recorded_test: "Dict[str, Any]") -> VariableRecorder:
    """Fixture that invokes the `recorded_test` fixture and returns a dictionary of recorded test variables.

    :param recorded_test: The fixture responsible for redirecting network traffic to target the test proxy.
        This should return a dictionary containing information about the current test -- in particular, the variables
        that were recorded with the test.
    :type recorded_test: Dict[str, Any]

    :returns: A VariableRecorder object. Calling `get_or_record(a, b)` on this object will return the recorded value of
        `a` in playback mode, or record the value `b` in recording mode. See the definition of VariableRecorder in
        https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/proxy_fixtures.py
        for more details.
    """
    return VariableRecorder(recorded_test["variables"])


# ----------HELPERS----------


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
            _LOGGER.error(f"\n\n-----Test proxy playback error:-----\n\n{message}")


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
            _LOGGER.error(f"\n\n-----Test proxy playback error:-----\n\n{message}")
