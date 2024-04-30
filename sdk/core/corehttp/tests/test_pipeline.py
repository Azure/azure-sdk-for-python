# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from unittest.mock import Mock
import json
from io import BytesIO
import xml.etree.ElementTree as ET

import pytest
import httpx
import requests

from corehttp.rest import HttpRequest
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
from corehttp.transport.httpx import HttpXTransport
from corehttp.exceptions import BaseError

from utils import SYNC_TRANSPORTS


def test_sans_io_exception():
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

    req = HttpRequest("GET", "/")
    with pytest.raises(ValueError):
        pipeline.run(req)


def test_invalid_policy_error():
    # non-HTTPPolicy/non-SansIOHTTPPolicy should raise an error
    class FooPolicy:
        pass

    # only on_request should raise an error
    class OnlyOnRequestPolicy:
        def on_request(self, request):
            pass

    # only on_response should raise an error
    class OnlyOnResponsePolicy:
        def on_response(self, request, response):
            pass

    with pytest.raises(AttributeError):
        pipeline = Pipeline(transport=Mock(), policies=[FooPolicy()])

    with pytest.raises(AttributeError):
        pipeline = Pipeline(transport=Mock(), policies=[OnlyOnRequestPolicy()])

    with pytest.raises(AttributeError):
        pipeline = Pipeline(transport=Mock(), policies=[OnlyOnResponsePolicy()])


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_transport_socket_timeout(transport):
    request = HttpRequest("GET", "https://bing.com")
    policies = [UserAgentPolicy("myusergant")]
    # Sometimes this will raise a read timeout, sometimes a socket timeout depending on timing.
    # Either way, the error should always be wrapped as an BaseError to ensure it's caught
    # by the retry policy.
    with pytest.raises(BaseError):
        with Pipeline(transport(), policies=policies) as pipeline:
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
    client = PipelineClientBase("{Endpoint}/text/analytics/v3.0")
    with pytest.raises(ValueError) as exp:
        client.format_url("foo/bar")
    assert (
        str(exp.value) == "The value provided for the url part Endpoint was incorrect, and resulted in an invalid url"
    )


def test_request_json():

    data = "Lots of dataaaa"
    request = HttpRequest("GET", "/", json=data)

    assert request.content == json.dumps(data)
    assert request.headers.get("Content-Length") == "17"


def test_request_data():

    data = "Lots of dataaaa"
    request = HttpRequest("GET", "/", content=data)

    assert request.content == data
    assert request.headers.get("Content-Length") == "15"


def test_request_stream():
    data = b"Lots of dataaaa"
    request = HttpRequest("GET", "/", content=data)
    assert request.content == data

    def data_gen():
        for i in range(10):
            yield i

    data = data_gen()
    request = HttpRequest("GET", "/", content=data)
    assert request.content == data

    data = BytesIO(b"Lots of dataaaa")
    request = HttpRequest("GET", "/", content=data)
    assert request.content == data


def test_request_xml():
    data = ET.Element("root")
    request = HttpRequest("GET", "/", content=data)
    assert request.content == b"<?xml version='1.0' encoding='utf-8'?>\n<root />"


def test_request_url_with_params():
    request = HttpRequest("GET", "a/b/c?t=y", params={"g": "h"})
    assert request.url in ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"]


def test_request_url_with_params_as_list():
    request = HttpRequest("GET", "a/b/c?t=y", params={"g": ["h", "i"]})
    assert request.url in ["a/b/c?g=h&g=i&t=y", "a/b/c?t=y&g=h&g=i"]


def test_request_url_with_params_with_none_in_list():
    with pytest.raises(ValueError):
        HttpRequest("GET", "a/b/c?t=y", params={"g": ["h", None]})


def test_request_url_with_params_with_none():
    with pytest.raises(ValueError):
        HttpRequest("GET", "a/b/c?t=y", params={"g": None})


def test_repr():
    request = HttpRequest("GET", "hello.com")
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


def test_basic_requests(port):
    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant")]
    with Pipeline(RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)

    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)


def test_basic_options_requests(port):

    request = HttpRequest("OPTIONS", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant")]
    with Pipeline(RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)

    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)


def test_basic_requests_separate_session(port):

    session = requests.Session()
    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant")]
    transport = RequestsTransport(session=session, session_owner=False)
    with Pipeline(transport, policies=policies) as pipeline:
        response = pipeline.run(request)

    assert transport.session
    assert isinstance(response.http_response.status_code, int)
    transport.close()
    assert transport.session
    transport.session.close()


def test_request_text(port):
    request = HttpRequest("GET", "/", json="foo")

    # In absence of information, everything is JSON (double quote added)
    assert request.content == json.dumps("foo")

    request = HttpRequest("POST", "/", headers={"content-type": "text/whatever"}, content="foo")

    # We want a direct string
    assert request.content == "foo"


def test_httpx_transport_get(port):
    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant")]
    with Pipeline(HttpXTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)

    assert pipeline._transport.client is None
    assert isinstance(response.http_response.status_code, int)


def test_httpx_transport_options(port):

    request = HttpRequest("OPTIONS", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant")]
    transport = HttpXTransport()
    with Pipeline(transport, policies=policies) as pipeline:
        response = pipeline.run(request)

    assert pipeline._transport.client is None
    assert isinstance(response.http_response.status_code, int)


def test_httpx_separate_session(port):

    client = httpx.Client()
    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant")]
    transport = HttpXTransport(client=client, client_owner=False)
    with Pipeline(transport, policies=policies) as pipeline:
        response = pipeline.run(request)

    assert transport.client
    assert isinstance(response.http_response.status_code, int)
    transport.close()
    assert transport.client
    transport.client.close()
