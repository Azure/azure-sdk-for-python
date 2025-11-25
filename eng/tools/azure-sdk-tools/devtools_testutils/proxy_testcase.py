# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import os
from typing import TYPE_CHECKING, Optional
from contextlib import ExitStack
from functools import wraps
import urllib.parse as url_parse

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy

# the functions we patch
try:
    from azure.core.pipeline.transport import RequestsTransport
except:
    pass

from .config import PROXY_URL
from .helpers import (
    get_http_client,
    get_test_id,
    is_live,
    is_live_and_not_recording,
    set_recording_id,
    trim_kwargs_from_test_function,  # to clean up incoming arguments to the test function we are wrapping
)
from .proxy_startup import discovered_roots
from urllib3.exceptions import HTTPError
import json

if TYPE_CHECKING:
    from typing import Callable, Dict, Tuple
    from azure.core.pipeline.transport import HttpRequest


# defaults
RECORDING_START_URL = "{}/record/start".format(PROXY_URL)
RECORDING_STOP_URL = "{}/record/stop".format(PROXY_URL)
PLAYBACK_START_URL = "{}/playback/start".format(PROXY_URL)
PLAYBACK_STOP_URL = "{}/playback/stop".format(PROXY_URL)


def get_recording_assets(test_id: str) -> Optional[str]:
    """Used to retrieve the assets.json given a PYTEST_CURRENT_TEST test id."""
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
    http_client = get_http_client()

    if is_live():
        result = http_client.request(
            method="POST",
            url=RECORDING_START_URL,
            body=encoded_payload,
        )
        if result.status != 200:
            raise HttpResponseError(message=result.data)
        recording_id = result.headers["x-recording-id"]

    else:
        result = http_client.request(
            method="POST",
            url=PLAYBACK_START_URL,
            body=encoded_payload,
        )
        if result.status != 200:
            raise HttpResponseError(message=result.data)

        try:
            recording_id = result.headers["x-recording-id"]
        except KeyError as ex:
            raise ValueError(f"No recording file found for {test_id}") from ex
        if result.data:
            try:
                variables = json.loads(result.data.decode("utf-8"))
            except ValueError as ex:  # would be a JSONDecodeError, which subclasses ValueError
                raise ValueError("The response body returned from starting playback did not contain valid JSON") from ex

    # set recording ID in a module-level variable so that sanitizers can access it
    set_recording_id(test_id, recording_id)
    return (recording_id, variables)


def stop_record_or_playback(test_id: str, recording_id: str, test_variables: "Dict[str, str]") -> None:
    http_client = get_http_client()
    if is_live():
        response = http_client.request(
            method="POST",
            url=RECORDING_STOP_URL,
            headers={
                "x-recording-file": test_id,
                "x-recording-id": recording_id,
                "x-recording-save": "true",
                "Content-Type": "application/json",
            },
            # tests don't record successfully unless test_variables is a dictionary
            body=json.dumps(test_variables or {}).encode("utf-8"),
        )
    else:
        response = http_client.request(
            method="POST",
            url=PLAYBACK_STOP_URL,
            headers={"x-recording-id": recording_id},
        )
    if response.status >= 400:
        raise HttpResponseError(
            "The test proxy ran into an error while ending the session. Make sure any test variables you record have "
            f"string values. Full error details: {response.data}"
        )


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


# helper: turn decorator args into a normalized list of (owner, attr_name)
def _normalize_transport_specs(specs):
    norm = []
    for spec in specs:
        if isinstance(spec, tuple) and len(spec) == 2:
            owner, attr = spec
            norm.append((owner, attr))
        else:
            # If a class was provided, assume attribute name "send"
            # (Safer than accepting a bare function object like RequestsTransport.send,
            # because assignment requires knowing the owner and attribute name.)
            norm.append((spec, "send"))
    return norm


def recorded_by_proxy(*maybe_specs):
    """
    Usages:
      @recorded_by_proxy
      def test(...): ...

      @recorded_by_proxy((RequestsTransport, "send"), (HttpxTransport, "send"))
      def test(...): ...
    """

    # Bare decorator usage: @recorded_by_proxy
    if len(maybe_specs) == 1 and callable(maybe_specs[0]):
        test_func = maybe_specs[0]
        transports = _normalize_transport_specs([(RequestsTransport, "send")])
        return _make_proxy_decorator(transports)(test_func)

    # Parameterized decorator usage: @recorded_by_proxy(...)
    transports = _normalize_transport_specs(maybe_specs or [(RequestsTransport, "send")])
    return _make_proxy_decorator(transports)


def _make_proxy_decorator(transports):
    def _decorator(test_func: "Callable"):
        @wraps(test_func)
        def record_wrap(*args, **kwargs):
            # ---- your existing trimming/early-exit logic ----
            trimmed_kwargs = {k: v for k, v in kwargs.items()}
            trim_kwargs_from_test_function(test_func, trimmed_kwargs)

            if is_live_and_not_recording():
                return test_func(*args, **trimmed_kwargs)

            test_id = get_test_id()
            recording_id, variables = start_record_or_playback(test_id)

            def transform_args_inner(*call_args, **call_kwargs):
                copied_positional_args = list(call_args)
                request = copied_positional_args[1]
                transform_request(request, recording_id)
                return tuple(copied_positional_args), call_kwargs

            # Build a wrapper factory so each patched method closes over its own original
            def make_combined_call(original_transport_func):
                def combined_call(*call_args, **call_kwargs):
                    adjusted_args, adjusted_kwargs = transform_args_inner(*call_args, **call_kwargs)
                    result = original_transport_func(*adjusted_args, **adjusted_kwargs)

                    # rewrite request.url to the original upstream for LROs, etc.
                    parsed_result = url_parse.urlparse(result.request.url)
                    upstream_uri = url_parse.urlparse(result.request.headers["x-recording-upstream-base-uri"])
                    upstream_uri_dict = {"scheme": upstream_uri.scheme, "netloc": upstream_uri.netloc}
                    original_target = parsed_result._replace(**upstream_uri_dict).geturl()
                    result.request.url = original_target
                    return result
                return combined_call

            # Patch multiple transports and ensure restoration
            test_variables = None
            test_run = False
            with ExitStack() as stack:
                originals = []
                # monkeypatch all requested transports
                for owner, name in transports:
                    original = getattr(owner, name)
                    setattr(owner, name, make_combined_call(original))
                    originals.append((owner, name, original))

                try:
                    try:
                        test_variables = test_func(*args, variables=variables, **trimmed_kwargs)
                        test_run = True
                    except TypeError as error:
                        if "unexpected keyword argument" in str(error) and "variables" in str(error):
                            logger = logging.getLogger()
                            logger.info(
                                "This test can't accept variables as input. "
                                "Accept `**kwargs` and/or a `variables` parameter to use recorded variables."
                            )
                        else:
                            raise

                    if not test_run:
                        test_variables = test_func(*args, **trimmed_kwargs)

                except ResourceNotFoundError as error:
                    error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
                    troubleshoot = (
                        "Playback failure -- for help resolving, see https://aka.ms/azsdk/python/test-proxy/troubleshoot."
                    )
                    message = error_body.get("message") or error_body.get("Message")
                    error_with_message = ResourceNotFoundError(
                        message=f"{troubleshoot} Error details:\n{message}",
                        response=error.response,
                    )
                    raise error_with_message from error

                finally:
                    # restore in reverse order
                    for owner, name, original in reversed(originals):
                        setattr(owner, name, original)
                    stop_record_or_playback(test_id, recording_id, test_variables)

            return test_variables
        return record_wrap
    return _decorator
