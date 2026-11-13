# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Sync unit tests for the throttle response headers that Execute() sets on the client.
"""

from unittest.mock import MagicMock

import pytest

from azure.cosmos import _retry_utility, exceptions
from azure.cosmos._request_object import RequestObject
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import HttpHeaders, ResourceType, StatusCodes


class _ImmutableHeaders(dict):
    """Headers another thread is iterating: any change to them would raise RuntimeError there."""

    def __setitem__(self, key, value):
        raise AssertionError(f"headers were mutated: {key}")


def _mock_client(last_response_headers):
    client = MagicMock()
    client.connection_policy = MagicMock()
    client.connection_policy.RetryOptions = MagicMock(
        MaxRetryAttemptCount=0,
        FixedRetryIntervalInMilliseconds=0,
        MaxWaitTimeInSeconds=0,
    )
    client.connection_policy.EnableEndpointDiscovery = False
    client.last_response_headers = last_response_headers
    client._container_properties_cache = {}
    client._enable_diagnostics_logging = False
    return client


def _mock_global_endpoint_manager():
    global_endpoint_manager = MagicMock()
    global_endpoint_manager.is_per_partition_automatic_failover_applicable.return_value = False
    global_endpoint_manager.is_circuit_breaker_applicable.return_value = False
    return global_endpoint_manager


def _request(resource_type):
    return RequestObject(resource_type, _OperationType.Read, {})


def _succeed(global_endpoint_manager, request, **kwargs):
    return {}, {}


def _fail(global_endpoint_manager, request, **kwargs):
    raise exceptions.CosmosHttpResponseError(status_code=StatusCodes.BAD_REQUEST, message="bad request")


class TestRetryUtilityThrottleHeaders:

    def test_database_account_request_leaves_last_response_headers_untouched(self):
        """A database account read must not change client.last_response_headers.

        The background endpoint refresh issues these reads on its own thread, while
        last_response_headers can be the headers a query on another thread is iterating.
        """
        headers = _ImmutableHeaders({"x-ms-request-charge": "1"})
        client = _mock_client(headers)

        _retry_utility.Execute(
            client, _mock_global_endpoint_manager(), _succeed, _request(ResourceType.DatabaseAccount))

        assert client.last_response_headers is headers
        assert client.last_response_headers == {"x-ms-request-charge": "1"}

    def test_failed_database_account_request_leaves_last_response_headers_untouched(self):
        """A failing database account read must not change client.last_response_headers either."""
        headers = _ImmutableHeaders({"x-ms-request-charge": "1"})
        client = _mock_client(headers)

        with pytest.raises(exceptions.CosmosHttpResponseError):
            _retry_utility.Execute(
                client, _mock_global_endpoint_manager(), _fail, _request(ResourceType.DatabaseAccount))

        assert client.last_response_headers is headers
        assert client.last_response_headers == {"x-ms-request-charge": "1"}

    def test_document_request_sets_throttle_headers(self):
        """Other requests still report their throttle retry statistics on the client."""
        client = _mock_client({})

        _retry_utility.Execute(client, _mock_global_endpoint_manager(), _succeed, _request(ResourceType.Document))

        assert client.last_response_headers[HttpHeaders.ThrottleRetryCount] == 0
        assert client.last_response_headers[HttpHeaders.ThrottleRetryWaitTimeInMs] == 0

    def test_failed_document_request_sets_throttle_headers(self):
        """A failing request also reports its throttle retry statistics on the client."""
        client = _mock_client({})

        with pytest.raises(exceptions.CosmosHttpResponseError):
            _retry_utility.Execute(client, _mock_global_endpoint_manager(), _fail, _request(ResourceType.Document))

        assert client.last_response_headers[HttpHeaders.ThrottleRetryCount] == 0
        assert client.last_response_headers[HttpHeaders.ThrottleRetryWaitTimeInMs] == 0
