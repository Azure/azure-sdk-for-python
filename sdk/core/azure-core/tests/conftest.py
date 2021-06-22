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
import os
import signal
import functools
import subprocess
import pytest
import sys
from azure.core.pipeline import policies
from azure.core.configuration import Configuration
from azure.core import PipelineClient
from azure.core.pipeline.transport._base import SupportedFormat
from azure.core.pipeline._tools import prepare_request_helper, update_response_based_on_format_helper

def start_testserver():
    os.environ["FLASK_APP"] = "coretestserver"
    cmd = "flask run"
    if os.name == 'nt': #On windows, subprocess creation works without being in the shell
        return subprocess.Popen(cmd.format("set"))

    return subprocess.Popen(cmd.format("export"), shell=True, preexec_fn=os.setsid) #On linux, have to set shell=True

def terminate_testserver(process):
    os.environ["FLASK_APP"] = ""
    if os.name == 'nt':
        process.kill()
    else:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Send the signal to all the process groups

@pytest.fixture(scope="session")
def testserver():
    """Start the Autorest testserver."""
    server = start_testserver()
    yield
    terminate_testserver(server)


class TestRestClientConfiguration(Configuration):
    def __init__(
        self, **kwargs
    ):
        # type: (...) -> None
        super(TestRestClientConfiguration, self).__init__(**kwargs)

        kwargs.setdefault("sdk_moniker", "autorestswaggerbatfileservice/1.0.0b1")
        self._configure(**kwargs)

    def _configure(
        self, **kwargs
    ):
        # type: (...) -> None
        self.user_agent_policy = kwargs.get("user_agent_policy") or policies.UserAgentPolicy(**kwargs)
        self.headers_policy = kwargs.get("headers_policy") or policies.HeadersPolicy(**kwargs)
        self.proxy_policy = kwargs.get("proxy_policy") or policies.ProxyPolicy(**kwargs)
        self.logging_policy = kwargs.get("logging_policy") or policies.NetworkTraceLoggingPolicy(**kwargs)
        self.http_logging_policy = kwargs.get("http_logging_policy") or policies.HttpLoggingPolicy(**kwargs)
        self.retry_policy = kwargs.get("retry_policy") or policies.RetryPolicy(**kwargs)
        self.custom_hook_policy = kwargs.get("custom_hook_policy") or policies.CustomHookPolicy(**kwargs)
        self.redirect_policy = kwargs.get("redirect_policy") or policies.RedirectPolicy(**kwargs)
        self.authentication_policy = kwargs.get("authentication_policy")

class TestRestClient(object):

    def __init__(self, **kwargs):
        self._config = TestRestClientConfiguration(**kwargs)
        self._client = PipelineClient(
            base_url="http://localhost:5000/",
            config=self._config,
            **kwargs
        )

    def send_request(self, request, **kwargs):
        """Runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "http://localhost:3000/helloWorld")
        <HttpRequest [GET], url: 'http://localhost:3000/helloWorld'>
        >>> response = client.send_request(request)
        <HttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/python/protocol/quickstart

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.HttpResponse
        """
        return self._client.send_request(request, **kwargs)

@pytest.fixture
def client():
    return TestRestClient()

@pytest.fixture
def add_properties_to_transport():
    def _callback(transport_mock):
        # need to add some stuff to transport to mock the new properties we've added
        transport_mock.supported_formats = [SupportedFormat.REST, SupportedFormat.PIPELINE_TRANSPORT]
        transport_mock.prepare_request = functools.partial(prepare_request_helper, transport_mock)
        transport_mock.update_response_based_on_format = update_response_based_on_format_helper
    return _callback

# Ignore collection of async tests for Python 2
collect_ignore = []
if sys.version_info < (3, 5):
    collect_ignore.append("async_tests")


# If opencensus is loadable while doing these tests, register an empty tracer to avoid this:
# https://github.com/census-instrumentation/opencensus-python/issues/442
try:
    from azure.core.tracing.ext.opencensus_span import OpenCensusSpan
    from opencensus.trace.tracer import Tracer
    Tracer()
except ImportError:
    pass
