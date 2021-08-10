# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import requests

try:
    # py3
    import urllib.parse as url_parse
except:
    # py2
    import urlparse as url_parse

import subprocess

# the functions we patch
from azure.core.pipeline.transport import RequestsTransport

# the trimming function to clean up incoming arguments to the test function we are wrapping
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from devtools_testutils.azure_recorded_testcase import is_live


# defaults
PROXY_URL = "http://localhost:5000"
RECORDING_START_URL = "{}/record/start".format(PROXY_URL)
RECORDING_STOP_URL = "{}/record/stop".format(PROXY_URL)
PLAYBACK_START_URL = "{}/playback/start".format(PROXY_URL)
PLAYBACK_STOP_URL = "{}/playback/stop".format(PROXY_URL)

# TODO, create a pytest scope="session" implementation that can be added to a fixture such that unit tests can
# startup/shutdown the local test proxy
# this should also fire the admin mapping updates, and start/end the session for commiting recording updates


def get_test_id():
    # pytest sets the current running test in an environment variable
    return os.getenv("PYTEST_CURRENT_TEST").split(" ")[0].replace("::", ".")


def get_current_sha():
    result = subprocess.check_output(["git", "rev-parse", "HEAD"])

    # TODO: is this compatible with py27?
    return result.decode("utf-8").strip()


def start_record_or_playback(test_id):
    if is_live:
        result = requests.post(
            RECORDING_START_URL,
            headers={"x-recording-file": test_id, "x-recording-sha": get_current_sha()},
            verify=False,
        )
        recording_id = result.headers["x-recording-id"]
    else:
        result = requests.post(
            PLAYBACK_START_URL,
            # headers={"x-recording-file": test_id, "x-recording-id": recording_id},
            headers={"x-recording-file": test_id, "x-recording-sha": get_current_sha()},
            verify=False,
        )
        recording_id = result.headers["x-recording-id"]
    return recording_id


def stop_record_or_playback(test_id, recording_id):
    if is_live:
        requests.post(
            RECORDING_STOP_URL,
            headers={"x-recording-file": test_id, "x-recording-id": recording_id, "x-recording-save": "true"},
            verify=False,
        )
    else:
        requests.post(
            PLAYBACK_STOP_URL,
            headers={"x-recording-file": test_id, "x-recording-id": recording_id},
            verify=False,
        )


def get_proxy_netloc():
    parsed_result = url_parse.urlparse(PROXY_URL)
    return {"scheme": parsed_result.scheme, "netloc": parsed_result.netloc}


def transform_request(request, recording_id):
    """Redirect the request to the test proxy, and store the original request URI in a header"""
    headers = request.headers

    parsed_result = url_parse.urlparse(request.url)
    updated_target = parsed_result._replace(**get_proxy_netloc()).geturl()
    if headers.get("x-recording-upstream-base-uri", None) is None:
        headers["x-recording-upstream-base-uri"] = "{}://{}".format(parsed_result.scheme, parsed_result.netloc)
    headers["x-recording-id"] = recording_id
    headers["x-recording-mode"] = "record" if is_live else "playback"
    request.url = updated_target


def RecordedByProxy(func):
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

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        original_transport_func = RequestsTransport.send

        def combined_call(*args, **kwargs):
            adjusted_args, adjusted_kwargs = transform_args(*args, **kwargs)
            req = adjusted_args[1]
            return original_transport_func(*adjusted_args, **adjusted_kwargs)

        RequestsTransport.send = combined_call

        # call the modified function.
        try:
            value = func(*args, **trimmed_kwargs)
        finally:
            RequestsTransport.send = original_transport_func
            # print("Exiting patch context. RequestsTransport.send is at {}".format(id(RequestsTransport.send)))
            stop_record_or_playback(test_id, recording_id)

        return value

    return record_wrap
