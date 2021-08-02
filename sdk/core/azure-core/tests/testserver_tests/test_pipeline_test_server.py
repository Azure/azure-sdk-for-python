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

from azure.core.configuration import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    RedirectPolicy,
)
from azure.core.pipeline.transport._base import PipelineClientBase
from azure.core.pipeline.transport import (
    HttpRequest,
    RequestsTransport,
)


def test_basic_requests(port):

    conf = Configuration()
    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))
    policies = [
        UserAgentPolicy("myusergant"),
        RedirectPolicy()
    ]
    with Pipeline(RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)

    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)

def test_basic_options_requests(port):

    request = HttpRequest("OPTIONS", "http://localhost:{}/basic/string".format(port))
    policies = [
        UserAgentPolicy("myusergant"),
        RedirectPolicy()
    ]
    with Pipeline(RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)

    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)

def test_basic_requests_separate_session(port):

    session = requests.Session()
    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))
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

def test_request_text(port):
    client = PipelineClientBase("http://localhost:{}".format(port))
    request = client.get(
        "/",
        content="foo"
    )

    # In absence of information, everything is JSON (double quote added)
    assert request.data == json.dumps("foo")

    request = client.post(
        "/",
        headers={'content-type': 'text/whatever'},
        content="foo"
    )

    # We want a direct string
    assert request.data == "foo"
