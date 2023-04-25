# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import six
import os
from typing import TYPE_CHECKING
import urllib.parse as url_parse

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy

# the functions we patch
from azure.core.pipeline.transport import RequestsTransport

# the trimming function to clean up incoming arguments to the test function we are wrapping
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

from .config import PROXY_URL
from .helpers import get_test_id, is_live, is_live_and_not_recording, set_recording_id
from .proxy_startup import discovered_roots
from urllib3 import PoolManager, Retry
from urllib3.exceptions import HTTPError
import json

if TYPE_CHECKING:
    from typing import Callable, Dict, Tuple
    from azure.core.pipeline.transport import HttpRequest

# To learn about how to migrate SDK tests to the test proxy, please refer to the migration guide at
# https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md

if os.getenv("REQUESTS_CA_BUNDLE"):
    http_client = PoolManager(
        retries=Retry(total=3, raise_on_status=False),
        cert_reqs="CERT_REQUIRED",
        ca_certs=os.getenv("REQUESTS_CA_BUNDLE"),
    )
else:
    http_client = PoolManager(retries=Retry(total=3, raise_on_status=False))

# defaults
RECORDING_START_URL = "{}/record/start".format(PROXY_URL)
RECORDING_STOP_URL = "{}/record/stop".format(PROXY_URL)
PLAYBACK_START_URL = "{}/playback/start".format(PROXY_URL)
PLAYBACK_STOP_URL = "{}/playback/stop".format(PROXY_URL)


def get_recording_assets(test_id: str) -> str:
    """
    Used to retrieve the assets.json given a PYTEST_CURRENT_TEST test id.
    """
    for root in discovered_roots:
        current_dir = os.path.dirname(test_id)
        while current_dir is not None and not (os.path.dirname(current_dir) == current_dir):
            possible_assets = os.path.join(current_dir, "assets.json")
            possible_root = os.path.join(current_dir, ".git")

            # we need to check for assets.json first!
            if os.path.exists(os.path.join(root, possible_assets)):
                complete_path = os.path.abspath(os.path.join(root, possible_assets))
                return os.path.relpath(complete_path, root).replace("\\", "/")
            # we need the git check to prevent ascending out of the repo
            elif os.path.exists(os.path.join(root, possible_root)):
                return None
            else:
                current_dir = os.path.dirname(current_dir)

    return None


def start_record_or_playback(test_id: str) -> "Tuple[str, Dict[str, str]]":
    """Sends a request to begin recording or playing back the provided test.

    This returns a tuple, (a, b), where a is the recording ID of the test and b is the `variables` dictionary that maps
    test variables to values. If no variable dictionary was stored when the test was recorded, b is an empty dictionary.
    """
    variables = {}  # this stores a dictionary of test variable values that could have been stored with a recording

    json_payload = {"x-recording-file": test_id}
    assets_json = get_recording_assets(test_id)
    if assets_json:
        json_payload["x-recording-assets-file"] = assets_json

    encoded_payload = json.dumps(json_payload).encode("utf-8")

    if is_live():
        result = http_client.request(
            method="POST",
            url=RECORDING_START_URL,
            body=encoded_payload,
        )
        if result.status != 200:
            message = six.ensure_str(result.data)
            raise HttpResponseError(message=message)
        recording_id = result.headers["x-recording-id"]

    else:
        result = http_client.request(
            method="POST",
            url=PLAYBACK_START_URL,
            body=encoded_payload,
        )
        if result.status != 200:
            message = six.ensure_str(result.data)
            raise HttpResponseError(message=message)

        try:
            recording_id = result.headers["x-recording-id"]
        except KeyError as ex:
            six.raise_from(ValueError("No recording file found for {}".format(test_id)), ex)
        if result.data:
            try:
                variables = json.loads(result.data.decode("utf-8"))
            except ValueError as ex:  # would be a JSONDecodeError on Python 3, which subclasses ValueError
                six.raise_from(
                    ValueError("The response body returned from starting playback did not contain valid JSON"),
                    ex,
                )

    # set recording ID in a module-level variable so that sanitizers can access it
    set_recording_id(test_id, recording_id)
    return (recording_id, variables)


def stop_record_or_playback(test_id: str, recording_id: str, test_variables: "Dict[str, str]") -> None:
    try:
        if is_live():
            http_client.request(
                method="POST",
                url=RECORDING_STOP_URL,
                headers={
                    "x-recording-file": test_id,
                    "x-recording-id": recording_id,
                    "x-recording-save": "true",
                    "Content-Type": "application/json",
                },
                # tests don't record successfully unless test_variables is a dictionary
                body=json.dumps(test_variables).encode("utf-8") if test_variables else "{}",
            )
        else:
            http_client.request(
                method="POST",
                url=PLAYBACK_STOP_URL,
                headers={"x-recording-id": recording_id},
            )
    except HTTPError as e:
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
            upstream_uri_dict = {
                "scheme": upstream_uri.scheme,
                "netloc": upstream_uri.netloc,
            }
            original_target = parsed_result._replace(**upstream_uri_dict).geturl()

            result.request.url = original_target
            return result

        RequestsTransport.send = combined_call

        # call the modified function
        # we define test_variables before invoking the test so the variable is defined in case of an exception
        test_variables = None
        # this tracks whether the test has been run yet; used when calling the test function with/without `variables`
        # running without `variables` in the `except` block leads to unnecessary exceptions in test execution output
        test_run = False
        try:
            try:
                test_variables = test_func(*args, variables=variables, **trimmed_kwargs)
                test_run = True
            except TypeError as error:
                if "unexpected keyword argument" in str(error) and "variables" in str(error):
                    logger = logging.getLogger()
                    logger.info(
                        "This test can't accept variables as input. The test method should accept `**kwargs` and/or a "
                        "`variables` parameter to make use of recorded test variables."
                    )
                else:
                    raise error
            # if the test couldn't accept `variables`, run the test without passing them
            if not test_run:
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
