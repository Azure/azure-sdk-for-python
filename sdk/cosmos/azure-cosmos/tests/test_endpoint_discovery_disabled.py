# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for the ``enable_endpoint_discovery=False`` contract on the
global endpoint manager.

These tests guard the fix for
https://github.com/Azure/azure-sdk-for-python/issues/46219 where the
synchronous and asynchronous ``_GlobalEndpointManager._GetDatabaseAccount``
methods would fall back to synthesized public regional endpoints
(``https://<account>-<region>.documents.azure.com``) even when the caller
explicitly disabled endpoint discovery -- causing intermittent
``403 Forbidden`` errors against private-endpoint-only accounts whose
private DNS zone did not include the regional FQDN.
"""

import unittest
import unittest.mock

import pytest

from azure.cosmos import documents, exceptions
from azure.cosmos._global_endpoint_manager import _GlobalEndpointManager
from azure.cosmos.http_constants import StatusCodes


_DEFAULT_ENDPOINT = "https://contoso.documents.azure.com:443/"


class _FakeClient:
    """Minimal client surface used by ``_GlobalEndpointManager``."""

    def __init__(self, connection_policy: documents.ConnectionPolicy):
        self.connection_policy = connection_policy
        self.url_connection = _DEFAULT_ENDPOINT


def _make_manager(*, enable_endpoint_discovery: bool, preferred_locations):
    policy = documents.ConnectionPolicy()
    policy.EnableEndpointDiscovery = enable_endpoint_discovery
    policy.PreferredLocations = list(preferred_locations)
    return _GlobalEndpointManager(_FakeClient(policy))


def _raise_503(_endpoint, **_kwargs):
    raise exceptions.CosmosHttpResponseError(
        status_code=StatusCodes.SERVICE_UNAVAILABLE,
        message="Service Unavailable",
    )


@pytest.mark.cosmosEmulator
class TestEndpointDiscoveryDisabled(unittest.TestCase):
    """Synchronous ``_GlobalEndpointManager._GetDatabaseAccount`` contract."""

    def test_disabled_does_not_try_locational_endpoints(self):
        mgr = _make_manager(
            enable_endpoint_discovery=False,
            preferred_locations=["North Europe", "West US"],
        )

        stub = unittest.mock.Mock(side_effect=_raise_503)
        with unittest.mock.patch.object(mgr, "_GetDatabaseAccountStub", stub):
            with self.assertRaises(exceptions.CosmosHttpResponseError):
                mgr._GetDatabaseAccount()

        # The stub must have been called exactly once -- against the user's URL.
        self.assertEqual(stub.call_count, 1)
        called_endpoint = stub.call_args.args[0]
        self.assertEqual(called_endpoint, _DEFAULT_ENDPOINT)

    def test_disabled_does_not_synthesize_when_no_preferred_locations(self):
        mgr = _make_manager(
            enable_endpoint_discovery=False,
            preferred_locations=[],
        )

        stub = unittest.mock.Mock(side_effect=_raise_503)
        with unittest.mock.patch.object(mgr, "_GetDatabaseAccountStub", stub):
            with self.assertRaises(exceptions.CosmosHttpResponseError):
                mgr._GetDatabaseAccount()

        self.assertEqual(stub.call_count, 1)

    def test_enabled_still_falls_back_to_preferred_locations(self):
        """Regression check -- behavior with discovery on must be unchanged."""
        mgr = _make_manager(
            enable_endpoint_discovery=True,
            preferred_locations=["North Europe", "West US"],
        )

        stub = unittest.mock.Mock(side_effect=_raise_503)
        with unittest.mock.patch.object(mgr, "_GetDatabaseAccountStub", stub):
            with self.assertRaises(exceptions.CosmosHttpResponseError):
                mgr._GetDatabaseAccount()

        # 1 attempt on the default endpoint plus one per preferred location.
        self.assertEqual(stub.call_count, 1 + 2)
        called_endpoints = [c.args[0] for c in stub.call_args_list]
        self.assertEqual(called_endpoints[0], _DEFAULT_ENDPOINT)
        self.assertIn("contoso-northeurope", called_endpoints[1])
        self.assertIn("contoso-westus", called_endpoints[2])


if __name__ == "__main__":
    unittest.main()
