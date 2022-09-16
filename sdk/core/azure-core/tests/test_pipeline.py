# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------

import json
import requests
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO
import xml.etree.ElementTree as ET
import sys

import pytest

from azure.core.configuration import Configuration
from azure.core.pipeline import Pipeline
from azure.core import PipelineClient
from azure.core.pipeline.policies import (
    SansIOHTTPPolicy,
    UserAgentPolicy,
    DistributedTracingPolicy,
    RedirectPolicy,
    RetryPolicy,
    HttpLoggingPolicy,
    HTTPPolicy,
    SansIOHTTPPolicy
)
from azure.core.pipeline.transport._base import PipelineClientBase
from azure.core.pipeline.transport import (
    HttpTransport,
    RequestsTransport,
)
from utils import HTTP_REQUESTS, is_rest

from azure.core.exceptions import AzureError

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_default_http_logging_policy(http_request):
    config = Configuration()
    pipeline_client = PipelineClient(base_url="test")
    pipeline = pipeline_client._build_pipeline(config)
    http_logging_policy = pipeline._impl_policies[-1]._policy
    assert http_logging_policy.allowed_header_names == HttpLoggingPolicy.DEFAULT_HEADERS_WHITELIST
    assert "WWW-Authenticate" in http_logging_policy.allowed_header_names

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_pass_in_http_logging_policy(http_request):
    config = Configuration()
    http_logging_policy = HttpLoggingPolicy()
    http_logging_policy.allowed_header_names.update(
        {"x-ms-added-header"}
    )
    config.http_logging_policy = http_logging_policy

    pipeline_client = PipelineClient(base_url="test")
    pipeline = pipeline_client._build_pipeline(config)
    http_logging_policy = pipeline._impl_policies[-1]._policy
    assert http_logging_policy.allowed_header_names == HttpLoggingPolicy.DEFAULT_HEADERS_WHITELIST.union({"x-ms-added-header"})


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_sans_io_exception(http_request):
    class BrokenSender(HttpTransport):
        def send(self, request, **config):
            raise ValueError("Broken")

        def open(self):
            self.session = requests.Session()

        def close(self):
            self.session.close()

        def __exit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return self.close()

    pipeline = Pipeline(BrokenSender(), [SansIOHTTPPolicy()])

    req = http_request("GET", "/")
    with pytest.raises(ValueError):
        pipeline.run(req)

    class SwapExec(SansIOHTTPPolicy):
        def on_exception(self, requests, **kwargs):
            exc_type, exc_value, exc_traceback = sys.exc_info()
            raise NotImplementedError(exc_value)

    pipeline = Pipeline(BrokenSender(), [SwapExec()])
    with pytest.raises(NotImplementedError):
        pipeline.run(req)

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_requests_socket_timeout(http_request):
    conf = Configuration()
    request = http_request("GET", "https://bing.com")
    policies = [
        UserAgentPolicy("myusergant"),
        RedirectPolicy()
    ]
    # Sometimes this will raise a read timeout, sometimes a socket timeout depending on timing.
    # Either way, the error should always be wrapped as an AzureError to ensure it's caught
    # by the retry policy.
    with pytest.raises(AzureError):
        with Pipeline(RequestsTransport(), policies=policies) as pipeline:
            response = pipeline.run(request, connection_timeout=0.000001, read_timeout=0.000001)

def test_format_url_basic():
    client = PipelineClientBase("https://bing.com")
    formatted = client.format_url("/{foo}", foo="bar")
    assert formatted == "https://bing.com/bar"

def test_format_url_with_query():
    client = PipelineClientBase("https://bing.com/path?query=testvalue&x=2ndvalue")
    formatted = client.format_url("/{foo}", foo="bar")
    assert formatted == "https://bing.com/path/bar?query=testvalue&x=2ndvalue"

def test_format_url_missing_param_values():
    client = PipelineClientBase("https://bing.com/path")
    formatted = client.format_url("/{foo}")
    assert formatted == "https://bing.com/path"

def test_format_url_missing_param_values_with_query():
    client = PipelineClientBase("https://bing.com/path?query=testvalue&x=2ndvalue")
    formatted = client.format_url("/{foo}")
    assert formatted == "https://bing.com/path?query=testvalue&x=2ndvalue"

def test_format_url_extra_path():
    client = PipelineClientBase("https://bing.com/path")
    formatted = client.format_url("/subpath/{foo}", foo="bar")
    assert formatted == "https://bing.com/path/subpath/bar"

def test_format_url_complex_params():
    client = PipelineClientBase("https://bing.com/path")
    formatted = client.format_url("/subpath/{a}/{b}/foo/{c}/bar", a="X", c="Y")
    assert formatted == "https://bing.com/path/subpath/X/foo/Y/bar"

def test_format_url_extra_path_missing_values():
    client = PipelineClientBase("https://bing.com/path")
    formatted = client.format_url("/subpath/{foo}")
    assert formatted == "https://bing.com/path/subpath"

def test_format_url_extra_path_missing_values_with_query():
    client = PipelineClientBase("https://bing.com/path?query=testvalue&x=2ndvalue")
    formatted = client.format_url("/subpath/{foo}")
    assert formatted == "https://bing.com/path/subpath?query=testvalue&x=2ndvalue"

def test_format_url_full_url():
    client = PipelineClientBase("https://bing.com/path")
    formatted = client.format_url("https://google.com/subpath/{foo}", foo="bar")
    assert formatted == "https://google.com/subpath/bar"

def test_format_url_no_base_url():
    client = PipelineClientBase(None)
    formatted = client.format_url("https://google.com/subpath/{foo}", foo="bar")
    assert formatted == "https://google.com/subpath/bar"

def test_format_incorrect_endpoint():
    # https://github.com/Azure/azure-sdk-for-python/pull/12106
    client = PipelineClientBase('{Endpoint}/text/analytics/v3.0')
    with pytest.raises(ValueError) as exp:
        client.format_url("foo/bar")
    assert str(exp.value) == "The value provided for the url part Endpoint was incorrect, and resulted in an invalid url"

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_json(http_request):

    request = http_request("GET", "/")
    data = "Lots of dataaaa"
    request.set_json_body(data)

    assert request.data == json.dumps(data)
    assert request.headers.get("Content-Length") == "17"

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_data(http_request):

    request = http_request("GET", "/")
    data = "Lots of dataaaa"
    request.set_bytes_body(data)

    assert request.data == data
    assert request.headers.get("Content-Length") == "15"

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_stream(http_request):
    request = http_request("GET", "/")

    data = b"Lots of dataaaa"
    request.set_streamed_data_body(data)
    assert request.data == data

    def data_gen():
        for i in range(10):
            yield i
    data = data_gen()
    request.set_streamed_data_body(data)
    assert request.data == data

    data = BytesIO(b"Lots of dataaaa")
    request.set_streamed_data_body(data)
    assert request.data == data


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_xml(http_request):
    request = http_request("GET", "/")
    data = ET.Element("root")
    request.set_xml_body(data)

    assert request.data == b"<?xml version='1.0' encoding='utf-8'?>\n<root />"

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_url_with_params(http_request):

    request = http_request("GET", "/")
    request.url = "a/b/c?t=y"
    request.format_parameters({"g": "h"})

    assert request.url in ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"]

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_url_with_params_as_list(http_request):

    request = http_request("GET", "/")
    request.url = "a/b/c?t=y"
    request.format_parameters({"g": ["h","i"]})

    assert request.url in ["a/b/c?g=h&g=i&t=y", "a/b/c?t=y&g=h&g=i"]

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_url_with_params_with_none_in_list(http_request):

    request = http_request("GET", "/")
    request.url = "a/b/c?t=y"
    with pytest.raises(ValueError):
        request.format_parameters({"g": ["h",None]})

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_url_with_params_with_none(http_request):

    request = http_request("GET", "/")
    request.url = "a/b/c?t=y"
    with pytest.raises(ValueError):
        request.format_parameters({"g": None})

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_repr(http_request):
    request = http_request("GET", "hello.com")
    assert repr(request) == "<HttpRequest [GET], url: 'hello.com'>"

def test_add_custom_policy():
    class BooPolicy(HTTPPolicy):
        def send(*args):
            raise AzureError('boo')

    class FooPolicy(HTTPPolicy):
        def send(*args):
            raise AzureError('boo')

    config = Configuration()
    retry_policy = RetryPolicy()
    config.retry_policy = retry_policy
    boo_policy = BooPolicy()
    foo_policy = FooPolicy()
    client = PipelineClient(base_url="test", config=config, per_call_policies=boo_policy)
    policies = client._pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry

    client = PipelineClient(base_url="test", config=config, per_call_policies=[boo_policy])
    policies = client._pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry

    client = PipelineClient(base_url="test", config=config, per_retry_policies=boo_policy)
    policies = client._pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo > pos_retry

    client = PipelineClient(base_url="test", config=config, per_retry_policies=[boo_policy])
    policies = client._pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo > pos_retry

    client = PipelineClient(base_url="test", config=config, per_call_policies=boo_policy, per_retry_policies=foo_policy)
    policies = client._pipeline._impl_policies
    assert boo_policy in policies
    assert foo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_foo = policies.index(foo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry
    assert pos_foo > pos_retry

    client = PipelineClient(base_url="test", config=config, per_call_policies=[boo_policy],
                            per_retry_policies=[foo_policy])
    policies = client._pipeline._impl_policies
    assert boo_policy in policies
    assert foo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_foo = policies.index(foo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry
    assert pos_foo > pos_retry

    policies = [UserAgentPolicy(),
                RetryPolicy(),
                DistributedTracingPolicy()]
    client = PipelineClient(base_url="test", policies=policies, per_call_policies=boo_policy)
    actual_policies = client._pipeline._impl_policies
    assert boo_policy == actual_policies[0]
    client = PipelineClient(base_url="test", policies=policies, per_call_policies=[boo_policy])
    actual_policies = client._pipeline._impl_policies
    assert boo_policy == actual_policies[0]

    client = PipelineClient(base_url="test", policies=policies, per_retry_policies=foo_policy)
    actual_policies = client._pipeline._impl_policies
    assert foo_policy == actual_policies[2]
    client = PipelineClient(base_url="test", policies=policies, per_retry_policies=[foo_policy])
    actual_policies = client._pipeline._impl_policies
    assert foo_policy == actual_policies[2]

    client = PipelineClient(base_url="test", policies=policies, per_call_policies=boo_policy,
                            per_retry_policies=foo_policy)
    actual_policies = client._pipeline._impl_policies
    assert boo_policy == actual_policies[0]
    assert foo_policy == actual_policies[3]
    client = PipelineClient(base_url="test", policies=policies, per_call_policies=[boo_policy],
                            per_retry_policies=[foo_policy])
    actual_policies = client._pipeline._impl_policies
    assert boo_policy == actual_policies[0]
    assert foo_policy == actual_policies[3]

    policies = [UserAgentPolicy(),
                DistributedTracingPolicy()]
    with pytest.raises(ValueError):
        client = PipelineClient(base_url="test", policies=policies, per_retry_policies=foo_policy)
    with pytest.raises(ValueError):
        client = PipelineClient(base_url="test", policies=policies, per_retry_policies=[foo_policy])

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_basic_requests(port, http_request):

    conf = Configuration()
    request = http_request("GET", "http://localhost:{}/basic/string".format(port))
    policies = [
        UserAgentPolicy("myusergant"),
        RedirectPolicy()
    ]
    with Pipeline(RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)
        if is_rest(request):
            assert is_rest(response.http_response)

    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_basic_options_requests(port, http_request):

    request = http_request("OPTIONS", "http://localhost:{}/basic/string".format(port))
    policies = [
        UserAgentPolicy("myusergant"),
        RedirectPolicy()
    ]
    with Pipeline(RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)
        if is_rest(request):
            assert is_rest(response.http_response)

    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_basic_requests_separate_session(port, http_request):

    session = requests.Session()
    request = http_request("GET", "http://localhost:{}/basic/string".format(port))
    policies = [
        UserAgentPolicy("myusergant"),
        RedirectPolicy()
    ]
    transport = RequestsTransport(session=session, session_owner=False)
    with Pipeline(transport, policies=policies) as pipeline:
        response = pipeline.run(request)
        if is_rest(request):
            assert is_rest(response.http_response)

    assert transport.session
    assert isinstance(response.http_response.status_code, int)
    transport.close()
    assert transport.session
    transport.session.close()

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_text(port, http_request):
    client = PipelineClientBase("http://localhost:{}".format(port))
    if is_rest(http_request):
        request = http_request("GET", "/", json="foo")
    else:
        request = client.get(
            "/",
            content="foo"
        )

    # In absence of information, everything is JSON (double quote added)
    assert request.data == json.dumps("foo")

    if is_rest(http_request):
        request = http_request("POST", "/", headers={'content-type': 'text/whatever'}, content="foo")
    else:
        request = client.post(
            "/",
            headers={'content-type': 'text/whatever'},
            content="foo"
        )

    # We want a direct string
    assert request.data == "foo"
