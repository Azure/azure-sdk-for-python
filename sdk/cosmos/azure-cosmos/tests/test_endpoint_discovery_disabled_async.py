# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async unit tests for the ``enable_endpoint_discovery=False`` contract.

Guards the async portion of the fix for
https://github.com/Azure/azure-sdk-for-python/issues/46219.
"""

import unittest
import unittest.mock

import pytest

from azure.cosmos import documents, exceptions
from azure.cosmos.aio._global_endpoint_manager_async import _GlobalEndpointManager
from azure.cosmos.http_constants import StatusCodes


_DEFAULT_ENDPOINT = "https://contoso.documents.azure.com:443/"


class _FakeAsyncClient:
    def __init__(self, connection_policy: documents.ConnectionPolicy):
        self.connection_policy = connection_policy
        self.url_connection = _DEFAULT_ENDPOINT


def _make_manager(*, enable_endpoint_discovery: bool, preferred_locations):
    policy = documents.ConnectionPolicy()
    policy.EnableEndpointDiscovery = enable_endpoint_discovery
    policy.PreferredLocations = list(preferred_locations)
    return _GlobalEndpointManager(_FakeAsyncClient(policy))


async def _raise_503(_endpoint, **_kwargs):
    raise exceptions.CosmosHttpResponseError(
        status_code=StatusCodes.SERVICE_UNAVAILABLE,
        message="Service Unavailable",
    )


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
class TestEndpointDiscoveryDisabledAsync:

    async def test_disabled_does_not_try_locational_endpoints(self):
        mgr = _make_manager(
            enable_endpoint_discovery=False,
            preferred_locations=["North Europe", "West US"],
        )

        stub = unittest.mock.AsyncMock(side_effect=_raise_503)
        with unittest.mock.patch.object(mgr, "_GetDatabaseAccountStub", stub):
            with pytest.raises(exceptions.CosmosHttpResponseError):
                await mgr._GetDatabaseAccount()

        assert stub.call_count == 1
        assert stub.call_args.args[0] == _DEFAULT_ENDPOINT

    async def test_disabled_does_not_synthesize_when_no_preferred_locations(self):
        mgr = _make_manager(
            enable_endpoint_discovery=False,
            preferred_locations=[],
        )

        stub = unittest.mock.AsyncMock(side_effect=_raise_503)
        with unittest.mock.patch.object(mgr, "_GetDatabaseAccountStub", stub):
            with pytest.raises(exceptions.CosmosHttpResponseError):
                await mgr._GetDatabaseAccount()

        assert stub.call_count == 1

    async def test_enabled_still_falls_back_to_preferred_locations(self):
        """Regression check -- behavior with discovery on must be unchanged."""
        mgr = _make_manager(
            enable_endpoint_discovery=True,
            preferred_locations=["North Europe", "West US"],
        )

        stub = unittest.mock.AsyncMock(side_effect=_raise_503)
        with unittest.mock.patch.object(mgr, "_GetDatabaseAccountStub", stub):
            with pytest.raises(exceptions.CosmosHttpResponseError):
                await mgr._GetDatabaseAccount()

        assert stub.call_count == 1 + 2
        called_endpoints = [c.args[0] for c in stub.call_args_list]
        assert called_endpoints[0] == _DEFAULT_ENDPOINT
        assert "contoso-northeurope" in called_endpoints[1]
        assert "contoso-westus" in called_endpoints[2]
