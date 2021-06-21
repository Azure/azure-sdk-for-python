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
from attr import has
import requests
import datetime
from enum import Enum
import unittest
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO

try:
    from unittest import mock
except ImportError:
    import mock
import xml.etree.ElementTree as ET
import sys

import requests
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
from azure.core.pipeline.transport._base import SupportedFormat
from azure.core.pipeline.transport._base import PipelineClientBase
from azure.core.pipeline.transport import (
    HttpRequest as PipelineTransportHttpRequest,
    HttpTransport,
    RequestsTransport,
)
from azure.core.rest import HttpRequest as RestHttpRequest

from azure.core.exceptions import AzureError

def test_default_http_logging_policy():
    config = Configuration()
    pipeline_client = PipelineClient(base_url="test")
    pipeline = pipeline_client._build_pipeline(config)
    http_logging_policy = pipeline._impl_policies[-1]._policy
    assert http_logging_policy.allowed_header_names == HttpLoggingPolicy.DEFAULT_HEADERS_WHITELIST

def test_pass_in_http_logging_policy():
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


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_sans_io_exception(request_type):
    class BrokenSender(HttpTransport):
        def send(self, request, **config):
            raise ValueError("Broken")

        def open(self):
            self.session = requests.Session()

        def close(self):
            self.session.close()

        @property
        def supported_formats(self):
            return [SupportedFormat.PIPELINE_TRANSPORT, SupportedFormat.REST]

        def __exit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return self.close()

    pipeline = Pipeline(BrokenSender(), [SansIOHTTPPolicy()])

    req = request_type("GET", "/")
    with pytest.raises(ValueError):
        pipeline.run(req)

    class SwapExec(SansIOHTTPPolicy):
        def on_exception(self, requests, **kwargs):
            exc_type, exc_value, exc_traceback = sys.exc_info()
            raise NotImplementedError(exc_value)

    pipeline = Pipeline(BrokenSender(), [SwapExec()])
    with pytest.raises(NotImplementedError):
        pipeline.run(req)

class TestRequestsTransport(object):

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_basic_requests(self, request_type):

        conf = Configuration()
        request = request_type("GET", "https://bing.com")
        policies = [
            UserAgentPolicy("myusergant"),
            RedirectPolicy()
        ]
        with Pipeline(RequestsTransport(), policies=policies) as pipeline:
            response = pipeline.run(request)

        assert pipeline._transport.session is None
        assert isinstance(response.http_response.status_code, int)

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_basic_options_requests(self, request_type):

        request = request_type("OPTIONS", "https://httpbin.org")
        policies = [
            UserAgentPolicy("myusergant"),
            RedirectPolicy()
        ]
        with Pipeline(RequestsTransport(), policies=policies) as pipeline:
            response = pipeline.run(request)

        assert pipeline._transport.session is None
        assert isinstance(response.http_response.status_code, int)

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_requests_socket_timeout(self, request_type):
        conf = Configuration()
        request = request_type("GET", "https://bing.com")
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

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_basic_requests_separate_session(self, request_type):

        session = requests.Session()
        request = request_type("GET", "https://bing.com")
        policies = [
            UserAgentPolicy("myusergant"),
            RedirectPolicy()
        ]
        transport = RequestsTransport(session=session, session_owner=False)
        with Pipeline(transport, policies=policies) as pipeline:
            response = pipeline.run(request)

        assert transport.session
        assert isinstance(response.http_response.status_code, int)
        transport.close()
        assert transport.session
        transport.session.close()

class TestClientPipelineURLFormatting(object):

    def test_format_url_basic(self):
        client = PipelineClientBase("https://bing.com")
        formatted = client.format_url("/{foo}", foo="bar")
        assert formatted == "https://bing.com/bar"

    def test_format_url_with_query(self):
        client = PipelineClientBase("https://bing.com/path?query=testvalue&x=2ndvalue")
        formatted = client.format_url("/{foo}", foo="bar")
        assert formatted == "https://bing.com/path/bar?query=testvalue&x=2ndvalue"

    def test_format_url_missing_param_values(self):
        client = PipelineClientBase("https://bing.com/path")
        formatted = client.format_url("/{foo}")
        assert formatted == "https://bing.com/path"

    def test_format_url_missing_param_values_with_query(self):
        client = PipelineClientBase("https://bing.com/path?query=testvalue&x=2ndvalue")
        formatted = client.format_url("/{foo}")
        assert formatted == "https://bing.com/path?query=testvalue&x=2ndvalue"

    def test_format_url_extra_path(self):
        client = PipelineClientBase("https://bing.com/path")
        formatted = client.format_url("/subpath/{foo}", foo="bar")
        assert formatted == "https://bing.com/path/subpath/bar"

    def test_format_url_complex_params(self):
        client = PipelineClientBase("https://bing.com/path")
        formatted = client.format_url("/subpath/{a}/{b}/foo/{c}/bar", a="X", c="Y")
        assert formatted == "https://bing.com/path/subpath/X/foo/Y/bar"

    def test_format_url_extra_path_missing_values(self):
        client = PipelineClientBase("https://bing.com/path")
        formatted = client.format_url("/subpath/{foo}")
        assert formatted == "https://bing.com/path/subpath"

    def test_format_url_extra_path_missing_values_with_query(self):
        client = PipelineClientBase("https://bing.com/path?query=testvalue&x=2ndvalue")
        formatted = client.format_url("/subpath/{foo}")
        assert formatted == "https://bing.com/path/subpath?query=testvalue&x=2ndvalue"

    def test_format_url_full_url(self):
        client = PipelineClientBase("https://bing.com/path")
        formatted = client.format_url("https://google.com/subpath/{foo}", foo="bar")
        assert formatted == "https://google.com/subpath/bar"

    def test_format_url_no_base_url(self):
        client = PipelineClientBase(None)
        formatted = client.format_url("https://google.com/subpath/{foo}", foo="bar")
        assert formatted == "https://google.com/subpath/bar"

    def test_format_incorrect_endpoint(self):
        # https://github.com/Azure/azure-sdk-for-python/pull/12106
        client = PipelineClientBase('{Endpoint}/text/analytics/v3.0')
        with pytest.raises(ValueError) as exp:
            client.format_url("foo/bar")
        assert str(exp.value) == "The value provided for the url part Endpoint was incorrect, and resulted in an invalid url"

class TestClientRequest(object):

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_request_json(self, request_type):

        data = "Lots of dataaaa"
        if hasattr(request_type, "content"):
            request = request_type("GET", "/", json=data)
        else:
            request = request_type("GET", "/")
            request.set_json_body(data)
            assert request.data == json.dumps(data)

        assert request.headers.get("Content-Length") == "17"

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_request_data(self, request_type):

        data = "Lots of dataaaa"

        if hasattr(request_type, "content"):
            request = request_type("GET", "/", content=data)
            assert request.content == data
        else:
            request = request_type("GET", "/")
            request.set_bytes_body(data)
            assert request.data == data
        assert request.headers.get("Content-Length") == "15"

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_request_stream(self, request_type):

        data = b"Lots of dataaaa"

        if hasattr(request_type, "content"):
            request = request_type("GET", "/", content=data)
            assert request.content == data
        else:
            request = request_type("GET", "/")
            request.set_streamed_data_body(data)
            assert request.data == data

        def data_gen():
            for i in range(10):
                yield i
        data = data_gen()

        if hasattr(request_type, "content"):
            request = request_type("GET", "/", content=data)
            assert request.content == data
        else:
            request.set_streamed_data_body(data)
            assert request.data == data

        data = BytesIO(b"Lots of dataaaa")
        if hasattr(request_type, "content"):
            request = request_type("GET", "/", content=data)
            assert request.content == data
        else:
            request.set_streamed_data_body(data)
            assert request.data == data


    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_request_xml(self, request_type):
        data = ET.Element("root")

        if hasattr(request_type, "content"):
            request = request_type("GET", "/", content=data)
            assert request.content == b"<?xml version='1.0' encoding='utf-8'?>\n<root />"
        else:
            request = request_type("GET", "/")
            request.set_xml_body(data)

            assert request.data == b"<?xml version='1.0' encoding='utf-8'?>\n<root />"

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_request_url_with_params(self, request_type):

        if hasattr(request_type, "content"):
            request = request_type("GET", "a/b/c?t=y", params={"g": "h"})
        else:
            request = request_type("GET", "/")
            request.url = "a/b/c?t=y"
            request.format_parameters({"g": "h"})

        assert request.url in ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"]

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_request_url_with_params_as_list(self, request_type):

        if hasattr(request_type, "content"):
            request = request_type("GET", "a/b/c?t=y", params={"g": ["h","i"]})
        else:
            request = request_type("GET", "/")
            request.url = "a/b/c?t=y"
            request.format_parameters({"g": ["h","i"]})

        assert request.url in ["a/b/c?g=h&g=i&t=y", "a/b/c?t=y&g=h&g=i"]

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_request_url_with_params_with_none_in_list(self, request_type):

        if hasattr(request_type, "content"):
            with pytest.raises(ValueError):
                request_type("GET", "a/b/c?t=y", params={"g": ["h",None]})
        else:
            request = request_type("GET", "/")
            request.url = "a/b/c?t=y"
            with pytest.raises(ValueError):
                request.format_parameters({"g": ["h",None]})

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_request_url_with_params_with_none(self, request_type):

        if hasattr(request_type, "content"):
            with pytest.raises(ValueError):
                request_type("GET", "a/b/c?t=y", params={"g": None})
        else:
            request = request_type("GET", "/")
            request.url = "a/b/c?t=y"
            with pytest.raises(ValueError):
                request.format_parameters({"g": None})


    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_request_text(self, request_type):
        client = PipelineClientBase('http://example.org')
        if hasattr(request_type, "content"):
            # we don't assume that everything is JSON bc we have a specific JSON kwarg
            request = request_type("GET", "/", content="foo")
            assert request.content == "foo"
        else:
            request = client.get(
                "/",
                content="foo"
            )

            # In absence of information, everything is JSON (double quote added)
            assert request.data == json.dumps("foo")

        if hasattr(request_type, "content"):
            request = request_type("POST", "/", headers={'content-type': 'text/whatever'}, content="foo")
            assert request.content == "foo"
        else:
            request = client.post(
                "/",
                headers={'content-type': 'text/whatever'},
                content="foo"
            )

            # We want a direct string
            assert request.data == "foo"

    @pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
    def test_repr(self, request_type):
        request = request_type("GET", "hello.com")
        assert repr(request) == "<HttpRequest [GET], url: 'hello.com'>"

    def test_add_custom_policy(self):
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
