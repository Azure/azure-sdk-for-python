# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from itertools import product
import pytest

from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import UserAgentPolicy
from azure.core.exceptions import AzureError

from utils import (
    SYNC_TRANSPORTS,
    HTTP_REQUESTS,
    create_http_request,
    create_transport_from_connection,
    assert_transport_connection,
)


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_transport_socket_timeout(transport, requesttype):
    request = create_http_request(requesttype, "GET", "https://bing.com")
    policies = [UserAgentPolicy("my-user-agent")]
    # Sometimes this will raise a read timeout, sometimes a socket timeout depending on timing.
    # Either way, the error should always be wrapped as an BaseError to ensure it's caught
    # by the retry policy.
    with pytest.raises(AzureError):
        with Pipeline(transport(), policies=policies) as pipeline:
            response = pipeline.run(request, connection_timeout=0.000001, read_timeout=0.000001)


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_basic_transport(port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("my-user-agent")]
    with Pipeline(transport(), policies=policies) as pipeline:
        response = pipeline.run(request)

    assert_transport_connection(pipeline._transport, is_closed=True)
    assert isinstance(response.http_response.status_code, int)


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_basic_options_request(port, transport, requesttype):
    request = create_http_request(requesttype, "OPTIONS", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("my-user-agent")]
    with Pipeline(transport(), policies=policies) as pipeline:
        response = pipeline.run(request)

    assert_transport_connection(pipeline._transport, is_closed=True)
    assert isinstance(response.http_response.status_code, int)


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_basic_transport_separate_connection(port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("my-user-agent")]
    transport = create_transport_from_connection(transport)
    with Pipeline(transport, policies=policies) as pipeline:
        response = pipeline.run(request)

    assert_transport_connection(transport, is_closed=False)
    assert isinstance(response.http_response.status_code, int)
    transport.close()
    assert_transport_connection(transport, is_closed=False)
