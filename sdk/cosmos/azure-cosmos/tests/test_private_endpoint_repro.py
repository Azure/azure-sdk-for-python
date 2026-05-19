# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Higher-fidelity repro for the private-endpoint 403 scenario from
https://github.com/Azure/azure-sdk-for-python/issues/46219.

Unlike ``test_endpoint_discovery_disabled.py``, this test constructs a real
``CosmosClient`` end-to-end. It hooks ``CosmosClientConnection.GetDatabaseAccount``
to record every URL the SDK actually attempts to call and to simulate the
private-endpoint scenario where the default endpoint succeeds the first time
(client construction succeeds) but the *next* database-account read fails --
mirroring a transient network blip after which the SDK previously fell back
to synthesized public regional FQDNs.

The test asserts on the URLs the SDK touches -- not on network results -- so
it runs without any Azure dependency.
"""

import unittest
import unittest.mock

import pytest

from azure.cosmos import documents, exceptions
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.documents import DatabaseAccount
from azure.cosmos.http_constants import StatusCodes


_PRIVATE_ENDPOINT = "https://contoso.documents.azure.com:443/"
_MASTER_KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="  # public emulator key


def _make_db_account():
    """Healthy DatabaseAccount with two regions -- matches the customer setup."""
    db = DatabaseAccount()
    db._WritableLocations = [
        {"name": "North Europe",
         "databaseAccountEndpoint": "https://contoso-northeurope.documents.azure.com:443/"},
    ]
    db._ReadableLocations = [
        {"name": "North Europe",
         "databaseAccountEndpoint": "https://contoso-northeurope.documents.azure.com:443/"},
        {"name": "West US",
         "databaseAccountEndpoint": "https://contoso-westus.documents.azure.com:443/"},
    ]
    db._EnableMultipleWritableLocations = False
    db.ConsistencyPolicy = {"defaultConsistencyLevel": "Session"}
    return db


def _build_get_database_account_mock():
    """Returns (mock, calls_list).

    The mock returns a healthy DatabaseAccount on the *first* call (so the
    CosmosClient ctor succeeds) and raises ServiceUnavailable on every
    subsequent call. ``calls`` records the URL passed to each invocation,
    letting the test inspect exactly which endpoints the SDK attempted.
    """
    calls: list[str] = []

    def side_effect(self, url_connection=None, **kwargs):  # noqa: ARG001
        url = url_connection if url_connection is not None else self.url_connection
        calls.append(url)
        if len(calls) == 1:
            return _make_db_account()
        raise exceptions.CosmosHttpResponseError(
            status_code=StatusCodes.SERVICE_UNAVAILABLE,
            message="Service Unavailable (simulated transient blip)",
        )

    return side_effect, calls


@pytest.mark.cosmosEmulator
class TestPrivateEndpointRepro(unittest.TestCase):
    """Repro of issue #46219 against a real CosmosClient."""

    def _construct_client(self, *, enable_endpoint_discovery: bool):
        return CosmosClient(
            _PRIVATE_ENDPOINT,
            credential=_MASTER_KEY,
            consistency_level="Session",
            enable_endpoint_discovery=enable_endpoint_discovery,
            preferred_locations=["North Europe", "West US"],
        )

    def test_disabled_never_contacts_synthesized_regional_endpoints(self):
        """With discovery off, only the user-supplied URL is ever touched.

        Before the fix, when a post-startup database-account refresh failed
        against the private endpoint the SDK would call
        ``https://contoso-northeurope.documents.azure.com`` and
        ``https://contoso-westus.documents.azure.com``. On a customer's
        private-endpoint-only account those FQDNs resolve via *public* DNS
        and the request gets a 403 from the Cosmos firewall.

        After the fix, the SDK re-raises the original error and never
        constructs a regional URL.
        """
        side_effect, calls = _build_get_database_account_mock()

        with unittest.mock.patch(
            "azure.cosmos._cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount",
            side_effect,
        ):
            client = self._construct_client(enable_endpoint_discovery=False)
            # Calls so far: 1 (the startup database-account read).
            # Simulate the periodic 5-minute refresh path directly. In real
            # life this runs on a daemon thread; calling it inline lets the
            # test observe which URLs the SDK attempts.
            mgr = client.client_connection._global_endpoint_manager
            with self.assertRaises(exceptions.CosmosHttpResponseError):
                mgr._GetDatabaseAccount()

        urls_touched = sorted(set(calls))
        print("\n[discovery=False] URLs the SDK contacted:")
        for u in urls_touched:
            print(f"  - {u}")

        # The default endpoint is the only host the SDK touched.
        for url in calls:
            self.assertIn("contoso.documents.azure.com", url)
            self.assertNotIn("contoso-northeurope", url)
            self.assertNotIn("contoso-westus", url)

    def test_enabled_does_fall_back_to_regional_endpoints(self):
        """Regression check: discovery-on behavior is unchanged."""
        side_effect, calls = _build_get_database_account_mock()

        with unittest.mock.patch(
            "azure.cosmos._cosmos_client_connection.CosmosClientConnection.GetDatabaseAccount",
            side_effect,
        ):
            client = self._construct_client(enable_endpoint_discovery=True)
            mgr = client.client_connection._global_endpoint_manager
            with self.assertRaises(exceptions.CosmosHttpResponseError):
                mgr._GetDatabaseAccount()

        urls_touched = sorted(set(calls))
        print("\n[discovery=True]  URLs the SDK contacted:")
        for u in urls_touched:
            print(f"  - {u}")

        joined = " ".join(calls)
        self.assertIn("contoso-northeurope", joined)
        self.assertIn("contoso-westus", joined)


if __name__ == "__main__":
    unittest.main()
