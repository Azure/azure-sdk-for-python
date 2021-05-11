# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
import pdb
import os
import requests
from contextlib import contextmanager

import subprocess


# the functions we patch
from azure.core.pipeline.transport import RequestsTransport, AsyncioRequestsTransport

# the trimming function to clean up incoming arguments to the test function we are wrapping
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

# defaults
PROXY_URL = "http://localhost:5001"
RECORDING_START_URL = "{}/record/start".format(PROXY_URL)
RECORDING_STOP_URL = "{}/record/stop".format(PROXY_URL)
PLAYBACK_START_URL = "{}/playback/start".format(PROXY_URL)
PLAYBACK_STOP_URL = "{}/playback/stop".format(PROXY_URL)

# TODO, create a pytest scope="session" implementation that can be added to a fixture such that that can
# unit tests can startup/shutdown the local test proxy
# this should also fire the admin mapping updates, and start/end the session for commiting recording updates

@contextmanager
def patch_requests_func(request_transform):
    original_func = RequestsTransport.send

    def combined_call(*args, **kwargs):
        adjusted_args, adjusted_kwargs = request_transform(*args,**kwargs)
        return original_func(*adjusted_args, **adjusted_kwargs)

    RequestsTransport.send = combined_call
    yield None

    RequestsTransport.send = original_func

@contextmanager
def patch_requests_func_async(request_transform):
    original_func = AsyncioRequestsTransport.send

    async def combined_call(*args, **kwargs):
        adjusted_args, adjusted_kwargs = request_transform(*args,**kwargs)
        return await original_func(*adjusted_args, **adjusted_kwargs)

    AsyncioRequestsTransport.send = combined_call
    yield None

    AsyncioRequestsTransport.send = original_func

def get_test_id():
    # pytest sets the current running test in an environment variable
    return os.getenv('PYTEST_CURRENT_TEST').split(" ")[0].replace("::",".")

def get_current_sha():
    result = subprocess.check_output(["git", "rev-parse", "HEAD"])

    #TODO: is this compatible with py27?
    return result.decode('utf-8').strip()

def start_record_or_playback(test_id):
    if os.getenv("AZURE_RECORD_MODE") == "record":
        result = requests.post(
            RECORDING_START_URL, headers={"x-recording-file": test_id, "x-recording-sha": get_current_sha() }, verify=False
        )
        recording_id = result.headers["x-recording-id"]
    elif os.getenv("AZURE_RECORD_MODE") == "playback":
        result = requests.post(
            PLAYBACK_START_URL,
            headers={"x-recording-file": test_id, "x-recording-id": recording_id},
            verify=False,
        )
        recording_id = result.headers["x-recording-id"]
    return recording_id

def stop_record_or_playback(test_id, recording_id):
    if os.getenv("AZURE_RECORD_MODE") == "record":
        result = requests.post(
            RECORDING_STOP_URL,
            headers={"x-recording-file": test_id, "x-recording-id": recording_id, "x-recording-save": "true"},
            verify=False,
        )
    elif os.getenv("AZURE_RECORD_MODE") == "playback":
        result = requests.post(
            PLAYBACK_STOP_URL,
            headers={"x-recording-file": test_id, "x-recording-id": recording_id},
            verify=False,
        )

def transform_request(request, recording_id):
    upstream_url = request.url.replace("//text", "/text")
    headers = request.headers

    # quiet passthrough if neither are set
    if os.getenv("AZURE_RECORD_MODE") == "record" or os.getenv("AZURE_RECORD_MODE") == "playback":
        headers["x-recording-upstream-base-uri"] = upstream_url
        headers["x-recording-id"] = recording_id
        headers["x-recording-mode"] = os.getenv("AZURE_RECORD_MODE")
        request.url = PROXY_URL

def RecordedByProxyAsync(func):
    @functools.wraps(func)
    async def record_wrap(*args, **kwargs):
        test_id = get_test_id()
        recording_id = get_recording_id(test_id)

        def transform_args(*args, **kwargs):
            copied_positional_args = list(args)
            request = copied_positional_args[1]

            # TODO, get the test-proxy server a real SSL certificate. The issue here is that SSL Certificates are
            # normally associated with a domain name. Need to talk to the //SSLAdmin folks (or someone else) and get
            # a recommendation for how to get a valid SSL Cert for localhost
            kwargs["connection_verify"] = False

            transform_request(request, recording_id)

            return tuple(copied_positional_args), kwargs

        trimmed_kwargs = {k:v for k,v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        # this ensures that within this scope, we've monkeypatched the send functionality
        with patch_requests_func_async(transform_args):
            # call the modified function.
            value = await func(*args, **trimmed_kwargs)

        stop_record_or_playback(test_id, recording_id)
        return value

    return record_wrap

def RecordedByProxy(func):
    @functools.wraps(func)
    def record_wrap(*args, **kwargs):
        test_id = get_test_id()
        recording_id = start_record_or_playback(test_id)

        def transform_args(*args, **kwargs):
            copied_positional_args = list(args)
            request = copied_positional_args[1]

            # TODO, get the test-proxy server a real SSL certificate. The issue here is that SSL Certificates are
            # normally associated with a domain name. Need to talk to the //SSLAdmin folks (or someone else) and get
            # a recommendation for how to get a valid SSL Cert for localhost
            kwargs["connection_verify"] = False

            transform_request(request, recording_id)

            return tuple(copied_positional_args), kwargs

        trimmed_kwargs = {k:v for k,v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        # this ensures that within this scope, we've monkeypatched the send functionality
        with patch_requests_func(transform_args):
            # call the modified function.
            try:
                value = func(*args, **trimmed_kwargs)
            finally:
                stop_record_or_playback(test_id, recording_id)

        return value

    return record_wrap