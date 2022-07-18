# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from inspect import iscoroutinefunction
import logging
import requests
import six
from typing import TYPE_CHECKING
import urllib.parse as url_parse

import pytest

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy

# the functions we patch
from azure.core.pipeline.transport import RequestsTransport

# the trimming function to clean up incoming arguments to the test function we are wrapping
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from .config import PROXY_URL
from .helpers import get_test_id, is_live, is_live_and_not_recording, set_recording_id
from .proxy_startup import test_proxy

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Optional, Tuple
    from pytest import FixtureRequest
    from azure.core.pipeline.transport import HttpRequest

# To learn about how to migrate SDK tests to the test proxy, please refer to the migration guide at
# https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md


# defaults
RECORDING_START_URL = "{}/record/start".format(PROXY_URL)
RECORDING_STOP_URL = "{}/record/stop".format(PROXY_URL)
PLAYBACK_START_URL = "{}/playback/start".format(PROXY_URL)
PLAYBACK_STOP_URL = "{}/playback/stop".format(PROXY_URL)


def start_record_or_playback(test_id: str) -> "Tuple[str, Dict[str, str]]":
    """Sends a request to begin recording or playing back the provided test.

    This returns a tuple, (a, b), where a is the recording ID of the test and b is the `variables` dictionary that maps
    test variables to values. If no variable dictionary was stored when the test was recorded, b is an empty dictionary.
    """
    variables = {}  # this stores a dictionary of test variable values that could have been stored with a recording

    if is_live():
        result = requests.post(
            RECORDING_START_URL,
            json={"x-recording-file": test_id},
        )
        if result.status_code != 200:
            message = six.ensure_str(result._content)
            raise HttpResponseError(message=message)
        recording_id = result.headers["x-recording-id"]

    else:
        result = requests.post(
            PLAYBACK_START_URL,
            json={"x-recording-file": test_id},
        )
        if result.status_code != 200:
            message = six.ensure_str(result._content)
            raise HttpResponseError(message=message)

        try:
            recording_id = result.headers["x-recording-id"]
        except KeyError as ex:
            six.raise_from(ValueError("No recording file found for {}".format(test_id)), ex)
        if result.text:
            try:
                variables = result.json()
            except ValueError as ex:  # would be a JSONDecodeError on Python 3, which subclasses ValueError
                six.raise_from(
                    ValueError("The response body returned from starting playback did not contain valid JSON"), ex
                )

    # set recording ID in a module-level variable so that sanitizers can access it
    set_recording_id(test_id, recording_id)
    return (recording_id, variables)


def stop_record_or_playback(test_id: str, recording_id: str, test_variables: "Dict[str, str]") -> None:
    if is_live():
        response = requests.post(
            RECORDING_STOP_URL,
            headers={
                "x-recording-file": test_id,
                "x-recording-id": recording_id,
                "x-recording-save": "true",
                "Content-Type": "application/json",
            },
            json=test_variables or {},  # tests don't record successfully unless test_variables is a dictionary
        )
    else:
        response = requests.post(
            PLAYBACK_STOP_URL,
            headers={"x-recording-id": recording_id},
        )
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        raise HttpResponseError(
            "The test proxy ran into an error while ending the session. Make sure any test variables you record have "
            "string values."
        ) from e


def get_proxy_netloc() -> "Dict[str, str]":
    parsed_result = url_parse.urlparse(PROXY_URL)
    return {"scheme": parsed_result.scheme, "netloc": parsed_result.netloc}


def transform_request(request: "HttpRequest", recording_id: str) -> None:
    """Redirect the request to the test proxy, and store the original request URI in a header"""
    headers = request.headers

    parsed_result = url_parse.urlparse(request.url)
    updated_target = parsed_result._replace(**get_proxy_netloc()).geturl()
    if headers.get("x-recording-upstream-base-uri", None) is None:
        headers["x-recording-upstream-base-uri"] = "{}://{}".format(parsed_result.scheme, parsed_result.netloc)
    headers["x-recording-id"] = recording_id
    headers["x-recording-mode"] = "record" if is_live() else "playback"
    request.url = updated_target


def recorded_by_proxy(test_func: "Callable") -> None:
    """Decorator that redirects network requests to target the azure-sdk-tools test proxy. Use with recorded tests.

    For more details and usage examples, refer to
    https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md
    """

    def record_wrap(*args, **kwargs):
        def transform_args(*args, **kwargs):
            copied_positional_args = list(args)
            request = copied_positional_args[1]

            transform_request(request, recording_id)

            return tuple(copied_positional_args), kwargs

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(test_func, trimmed_kwargs)

        if is_live_and_not_recording():
            return test_func(*args, **trimmed_kwargs)

        test_id = get_test_id()
        recording_id, variables = start_record_or_playback(test_id)
        original_transport_func = RequestsTransport.send

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

        # call the modified function
        # we define test_variables before invoking the test so the variable is defined in case of an exception
        test_variables = None
        try:
            try:
                test_variables = test_func(*args, variables=variables, **trimmed_kwargs)
            except TypeError:
                logger = logging.getLogger()
                logger.info(
                    "This test can't accept variables as input. The test method should accept `**kwargs` and/or a "
                    "`variables` parameter to make use of recorded test variables."
                )
                test_variables = test_func(*args, **trimmed_kwargs)
        except ResourceNotFoundError as error:
            error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
            message = error_body.get("message") or error_body.get("Message")
            error_with_message = ResourceNotFoundError(message=message, response=error.response)
            six.raise_from(error_with_message, error)
        finally:
            RequestsTransport.send = original_transport_func
            stop_record_or_playback(test_id, recording_id, test_variables)

        return test_variables

    return record_wrap


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
    return recorded_test["variables"]
