# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import json
import requests

try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO
import xml.etree.ElementTree as ET
import sys

import pytest

from corehttp.runtime.pipeline import Pipeline
from corehttp.runtime import PipelineClient
from corehttp.runtime.policies import (
    SansIOHTTPPolicy,
    UserAgentPolicy,
    RetryPolicy,
    HTTPPolicy,
)
from corehttp.runtime._base import PipelineClientBase, _format_url_section
from corehttp.transport import HttpTransport
from corehttp.transport.requests import RequestsTransport
from utils import HTTP_REQUESTS

from corehttp.exceptions import BaseError


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


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_requests_socket_timeout(http_request):
    request = http_request("GET", "https://bing.com")
    policies = [UserAgentPolicy("myusergant")]
    # Sometimes this will raise a read timeout, sometimes a socket timeout depending on timing.
    # Either way, the error should always be wrapped as an BaseError to ensure it's caught
    # by the retry policy.
    with pytest.raises(BaseError):
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


def test_format_url_no_endpoint():
    client = PipelineClientBase(None)
    formatted = client.format_url("https://google.com/subpath/{foo}", foo="bar")
    assert formatted == "https://google.com/subpath/bar"


def test_format_url_double_query():
    client = PipelineClientBase("https://bing.com/path?query=testvalue&x=2ndvalue")
    formatted = client.format_url("/subpath?a=X&c=Y")
    assert formatted == "https://bing.com/path/subpath?query=testvalue&x=2ndvalue&a=X&c=Y"


def test_format_url_braces_with_dot():
    endpoint = "https://bing.com/{aaa.bbb}"
    with pytest.raises(ValueError):
        url = _format_url_section(endpoint)


def test_format_url_single_brace():
    endpoint = "https://bing.com/{aaa.bbb"
    with pytest.raises(ValueError):
        url = _format_url_section(endpoint)


def test_format_incorrect_endpoint():
    # https://github.com/Azure/azure-sdk-for-python/pull/12106
    client = PipelineClientBase("{Endpoint}/text/analytics/v3.0")
    with pytest.raises(ValueError) as exp:
        client.format_url("foo/bar")
    assert (
        str(exp.value) == "The value provided for the url part Endpoint was incorrect, and resulted in an invalid url"
    )


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_json(http_request):

    data = "Lots of dataaaa"
    request = http_request("GET", "/", json=data)

    assert request.content == json.dumps(data)
    assert request.headers.get("Content-Length") == "17"


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_data(http_request):

    data = "Lots of dataaaa"
    request = http_request("GET", "/", content=data)

    assert request.content == data
    assert request.headers.get("Content-Length") == "15"


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_stream(http_request):
    data = b"Lots of dataaaa"
    request = http_request("GET", "/", content=data)
    assert request.content == data

    def data_gen():
        for i in range(10):
            yield i

    data = data_gen()
    request = http_request("GET", "/", content=data)
    assert request.content == data

    data = BytesIO(b"Lots of dataaaa")
    request = http_request("GET", "/", content=data)
    assert request.content == data


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_xml(http_request):
    data = ET.Element("root")
    request = http_request("GET", "/", content=data)
    assert request.content == b"<?xml version='1.0' encoding='utf-8'?>\n<root />"


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_url_with_params(http_request):
    request = http_request("GET", "a/b/c?t=y", params={"g": "h"})
    assert request.url in ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"]


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_url_with_params_as_list(http_request):
    request = http_request("GET", "a/b/c?t=y", params={"g": ["h", "i"]})
    assert request.url in ["a/b/c?g=h&g=i&t=y", "a/b/c?t=y&g=h&g=i"]


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_url_with_params_with_none_in_list(http_request):
    with pytest.raises(ValueError):
        http_request("GET", "a/b/c?t=y", params={"g": ["h", None]})


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_url_with_params_with_none(http_request):
    with pytest.raises(ValueError):
        http_request("GET", "a/b/c?t=y", params={"g": None})


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_repr(http_request):
    request = http_request("GET", "hello.com")
    assert repr(request) == "<HttpRequest [GET], url: 'hello.com'>"


def test_add_custom_policy():
    class BooPolicy(HTTPPolicy):
        def send(*args):
            raise BaseError("boo")

    class FooPolicy(HTTPPolicy):
        def send(*args):
            raise BaseError("boo")

    retry_policy = RetryPolicy()
    boo_policy = BooPolicy()
    foo_policy = FooPolicy()
    client = PipelineClient(endpoint="test", policies=[retry_policy], per_call_policies=boo_policy)
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry

    client = PipelineClient(endpoint="test", policies=[retry_policy], per_call_policies=[boo_policy])
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry

    client = PipelineClient(endpoint="test", policies=[retry_policy], per_retry_policies=boo_policy)
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo > pos_retry

    client = PipelineClient(endpoint="test", policies=[retry_policy], per_retry_policies=[boo_policy])
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo > pos_retry

    client = PipelineClient(
        endpoint="test", policies=[retry_policy], per_call_policies=boo_policy, per_retry_policies=foo_policy
    )
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    assert foo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_foo = policies.index(foo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry
    assert pos_foo > pos_retry

    client = PipelineClient(
        endpoint="test", policies=[retry_policy], per_call_policies=[boo_policy], per_retry_policies=[foo_policy]
    )
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    assert foo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_foo = policies.index(foo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry
    assert pos_foo > pos_retry

    policies = [UserAgentPolicy(), RetryPolicy()]
    client = PipelineClient(endpoint="test", policies=policies, per_call_policies=boo_policy)
    actual_policies = client.pipeline._impl_policies
    assert boo_policy == actual_policies[0]
    client = PipelineClient(endpoint="test", policies=policies, per_call_policies=[boo_policy])
    actual_policies = client.pipeline._impl_policies
    assert boo_policy == actual_policies[0]

    client = PipelineClient(endpoint="test", policies=policies, per_retry_policies=foo_policy)
    actual_policies = client.pipeline._impl_policies
    assert foo_policy == actual_policies[2]
    client = PipelineClient(endpoint="test", policies=policies, per_retry_policies=[foo_policy])
    actual_policies = client.pipeline._impl_policies
    assert foo_policy == actual_policies[2]

    client = PipelineClient(
        endpoint="test", policies=policies, per_call_policies=boo_policy, per_retry_policies=foo_policy
    )
    actual_policies = client.pipeline._impl_policies
    assert boo_policy == actual_policies[0]
    assert foo_policy == actual_policies[3]
    client = PipelineClient(
        endpoint="test", policies=policies, per_call_policies=[boo_policy], per_retry_policies=[foo_policy]
    )
    actual_policies = client.pipeline._impl_policies
    assert boo_policy == actual_policies[0]
    assert foo_policy == actual_policies[3]

    policies = [UserAgentPolicy()]
    with pytest.raises(ValueError):
        client = PipelineClient(endpoint="test", policies=policies, per_retry_policies=foo_policy)
    with pytest.raises(ValueError):
        client = PipelineClient(endpoint="test", policies=policies, per_retry_policies=[foo_policy])


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_basic_requests(port, http_request):
    request = http_request("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant")]
    with Pipeline(RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)

    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_basic_options_requests(port, http_request):

    request = http_request("OPTIONS", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant")]
    with Pipeline(RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)

    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_basic_requests_separate_session(port, http_request):

    session = requests.Session()
    request = http_request("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant")]
    transport = RequestsTransport(session=session, session_owner=False)
    with Pipeline(transport, policies=policies) as pipeline:
        response = pipeline.run(request)

    assert transport.session
    assert isinstance(response.http_response.status_code, int)
    transport.close()
    assert transport.session
    transport.session.close()


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_text(port, http_request):
    client = PipelineClientBase("http://localhost:{}".format(port))
    request = http_request("GET", "/", json="foo")

    # In absence of information, everything is JSON (double quote added)
    assert request.content == json.dumps("foo")

    request = http_request("POST", "/", headers={"content-type": "text/whatever"}, content="foo")

    # We want a direct string
    assert request.content == "foo"
