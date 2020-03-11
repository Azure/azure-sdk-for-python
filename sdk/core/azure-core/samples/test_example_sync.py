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

from azure.core.pipeline import Pipeline
from azure.core import PipelineClient
from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    RedirectPolicy,
    RetryPolicy
)


def test_example_requests():
    request = HttpRequest("GET", "https://bing.com")
    policies = [
        UserAgentPolicy("myuseragent"),
        RedirectPolicy(),
        RetryPolicy()
    ]
    # [START requests]
    from azure.core.pipeline.transport import RequestsTransport

    with Pipeline(transport=RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)
    # [END requests]
    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)


def test_example_pipeline():
    # [START build_pipeline]
    from azure.core.pipeline import Pipeline
    from azure.core.pipeline.policies import RedirectPolicy, UserAgentPolicy
    from azure.core.pipeline.transport import RequestsTransport, HttpRequest

    # example: create request and policies
    request = HttpRequest("GET", "https://bing.com")
    policies = [
        UserAgentPolicy("myuseragent"),
        RedirectPolicy()
    ]

    # run the pipeline
    with Pipeline(transport=RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)
    # [END build_pipeline]
    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)


def test_example_pipeline_client():
    url = "https://bing.com"
    # [START build_pipeline_client]
    from azure.core import PipelineClient
    from azure.core.pipeline.policies import RedirectPolicy, UserAgentPolicy

    # example configuration with some policies
    policies = [
        UserAgentPolicy("myuseragent"),
        RedirectPolicy()
    ]

    client = PipelineClient(base_url=url, policies=policies)
    request = client.get("https://bing.com")

    pipeline_response = client._pipeline.run(request)
    # [END build_pipeline_client]

    response = pipeline_response.http_response
    assert isinstance(response.status_code, int)

def test_example_redirect_policy():

    url = "https://bing.com"

    # [START redirect_policy]
    from azure.core.pipeline.policies import RedirectPolicy

    redirect_policy = RedirectPolicy()

    # Client allows redirects. Defaults to True.
    redirect_policy.allow = True

    # The maximum allowed redirects. The default value is 30
    redirect_policy.max_redirects = 10

    # Alternatively you can disable redirects entirely
    redirect_policy = RedirectPolicy.no_redirects()

    # It can also be overridden per operation.
    client = PipelineClient(base_url=url, policies=[redirect_policy])
    request = client.get(url)
    pipeline_response = client._pipeline.run(request, permit_redirects=True, redirect_max=5)
    # [END redirect_policy]

    response = pipeline_response.http_response
    assert isinstance(response.status_code, int)


def test_example_no_redirects():
    url = "https://bing.com"

    redirect_policy = RedirectPolicy.no_redirects()

    client = PipelineClient(base_url=url, policies=[redirect_policy])
    request = client.get(url)
    pipeline_response = client._pipeline.run(request)

    response = pipeline_response.http_response
    # bing returns 301 if not redirected
    assert response.status_code == 301


def test_example_retry_policy():

    url = "https://bing.com"

    policies = [
        UserAgentPolicy("myuseragent"),
        RedirectPolicy()
    ]

    # [START retry_policy]
    from azure.core.pipeline.policies import RetryPolicy

    retry_policy = RetryPolicy()

    # Total number of retries to allow. Takes precedence over other counts.
    # Default value is 10.
    retry_policy.total_retries = 5

    # How many connection-related errors to retry on.
    # These are errors raised before the request is sent to the remote server,
    # which we assume has not triggered the server to process the request. Default value is 3
    retry_policy.connect_retries = 2

    # How many times to retry on read errors.
    # These errors are raised after the request was sent to the server, so the
    # request may have side-effects. Default value is 3.
    retry_policy.read_retries = 4

    # How many times to retry on bad status codes. Default value is 3.
    retry_policy.status_retries = 3

    # A backoff factor to apply between attempts after the second try
    # (most errors are resolved immediately by a second try without a delay).
    # Retry policy will sleep for:
    #    {backoff factor} * (2 ** ({number of total retries} - 1))
    # seconds. If the backoff_factor is 0.1, then the retry will sleep
    # for [0.0s, 0.2s, 0.4s, ...] between retries.
    # The default value is 0.8.
    retry_policy.backoff_factor = 0.5

    # The maximum back off time. Default value is 120 seconds (2 minutes).
    retry_policy.backoff_max = 120

    # Alternatively you can disable redirects entirely
    retry_policy = RetryPolicy.no_retries()

    # All of these settings can also be configured per operation.
    policies.append(retry_policy)
    client = PipelineClient(base_url=url, policies=policies)
    request = client.get(url)
    pipeline_response = client._pipeline.run(
        request,
        retry_total=10,
        retry_connect=1,
        retry_read=1,
        retry_status=5,
        retry_backoff_factor=0.5,
        retry_backoff_max=120,
        retry_on_methods=['GET']
    )
    # [END retry_policy]

    response = pipeline_response.http_response
    assert isinstance(response.status_code, int)

def test_example_no_retries():
    url = "https://bing.com"

    retry_policy = RetryPolicy.no_retries()

    client = PipelineClient(base_url=url, policies=[retry_policy])
    request = client.get(url)
    pipeline_response = client._pipeline.run(request)

    response = pipeline_response.http_response
    # bing returns 301 if not retried
    assert response.status_code == 301
