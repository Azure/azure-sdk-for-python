# --------------------------------------------------------------------------
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
import time
from unittest import mock
import pytest
import httpretty

from azure.core.configuration import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import (
    HttpRequest,
    RequestsTransport,
)

from azure.mgmt.core import ARMPipelineClient
from azure.mgmt.core.policies import (
    ARMAutoResourceProviderRegistrationPolicy,
    ARMHttpLoggingPolicy,
)


@pytest.fixture
def sleepless(monkeypatch):
    def sleep(_):
        pass

    monkeypatch.setattr(time, "sleep", sleep)


@httpretty.activate
@pytest.mark.usefixtures("sleepless")
def test_register_rp_policy():
    """Protocol:
    - We call the provider and get a 409 provider error
    - Now we POST register provider and get "Registering"
    - Now we GET register provider and get "Registered"
    - We call again the first endpoint and this time this succeed
    """

    provider_url = (
        "https://management.azure.com/"
        "subscriptions/12345678-9abc-def0-0000-000000000000/"
        "resourceGroups/clitest.rg000001/"
        "providers/Microsoft.Sql/servers/ygserver123?api-version=2014-04-01"
    )

    provider_error = (
        '{"error":{"code":"MissingSubscriptionRegistration", '
        '"message":"The subscription registration is in \'Unregistered\' state. '
        "The subscription must be registered to use namespace 'Microsoft.Sql'. "
        'See https://aka.ms/rps-not-found for how to register subscriptions."}}'
    )

    provider_success = '{"success": true}'

    httpretty.register_uri(
        httpretty.PUT,
        provider_url,
        responses=[
            httpretty.Response(body=provider_error, status=409),
            httpretty.Response(body=provider_success),
        ],
        content_type="application/json",
    )

    register_post_url = (
        "https://management.azure.com/"
        "subscriptions/12345678-9abc-def0-0000-000000000000/"
        "providers/Microsoft.Sql/register?api-version=2016-02-01"
    )

    register_post_result = {"registrationState": "Registering"}

    register_get_url = (
        "https://management.azure.com/"
        "subscriptions/12345678-9abc-def0-0000-000000000000/"
        "providers/Microsoft.Sql?api-version=2016-02-01"
    )

    register_get_result = {"registrationState": "Registered"}

    httpretty.register_uri(
        httpretty.POST,
        register_post_url,
        body=json.dumps(register_post_result),
        content_type="application/json",
    )

    httpretty.register_uri(
        httpretty.GET,
        register_get_url,
        body=json.dumps(register_get_result),
        content_type="application/json",
    )

    request = HttpRequest("PUT", provider_url)
    policies = [
        ARMAutoResourceProviderRegistrationPolicy(),
    ]
    with Pipeline(RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)

    assert json.loads(response.http_response.text())["success"]


@httpretty.activate
@pytest.mark.usefixtures("sleepless")
def test_register_failed_policy():
    """Protocol:
    - We call the provider and get a 409 provider error
    - Now we POST register provider and get "Registering"
    - This POST failed
    """

    provider_url = (
        "https://management.azure.com/"
        "subscriptions/12345678-9abc-def0-0000-000000000000/"
        "resourceGroups/clitest.rg000001/"
        "providers/Microsoft.Sql/servers/ygserver123?api-version=2014-04-01"
    )

    provider_error = (
        '{"error":{"code":"MissingSubscriptionRegistration", '
        '"message":"The subscription registration is in \'Unregistered\' state. '
        "The subscription must be registered to use namespace 'Microsoft.Sql'. "
        'See https://aka.ms/rps-not-found for how to register subscriptions."}}'
    )

    provider_success = '{"success": true}'

    httpretty.register_uri(
        httpretty.PUT,
        provider_url,
        responses=[
            httpretty.Response(body=provider_error, status=409),
            httpretty.Response(body=provider_success),
        ],
        content_type="application/json",
    )

    register_post_url = (
        "https://management.azure.com/"
        "subscriptions/12345678-9abc-def0-0000-000000000000/"
        "providers/Microsoft.Sql/register?api-version=2016-02-01"
    )

    httpretty.register_uri(
        httpretty.POST, register_post_url, status=409, content_type="application/json"
    )

    request = HttpRequest("PUT", provider_url)
    policies = [
        ARMAutoResourceProviderRegistrationPolicy(),
    ]
    with Pipeline(RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)

    assert response.http_response.status_code == 409


def test_default_http_logging_policy():
    config = Configuration()
    pipeline_client = ARMPipelineClient(base_url="test", config=config)
    http_logging_policy = pipeline_client._pipeline._impl_policies[-1]._policy
    assert (
        http_logging_policy.allowed_header_names
        == ARMHttpLoggingPolicy.DEFAULT_HEADERS_WHITELIST
    )
    assert (
        http_logging_policy.allowed_header_names
        == ARMHttpLoggingPolicy.DEFAULT_HEADERS_ALLOWLIST
    )


def test_pass_in_http_logging_policy():
    config = Configuration()
    http_logging_policy = ARMHttpLoggingPolicy()
    http_logging_policy.allowed_header_names.update({"x-ms-added-header"})
    config.http_logging_policy = http_logging_policy

    pipeline_client = ARMPipelineClient(base_url="test", config=config)
    http_logging_policy = pipeline_client._pipeline._impl_policies[-1]._policy
    assert (
        http_logging_policy.allowed_header_names
        == ARMHttpLoggingPolicy.DEFAULT_HEADERS_ALLOWLIST.union({"x-ms-added-header"})
    )
    assert (
        http_logging_policy.allowed_header_names
        == ARMHttpLoggingPolicy.DEFAULT_HEADERS_WHITELIST.union({"x-ms-added-header"})
    )
