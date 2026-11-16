# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Rust connection-string scenarios, including an intentional User-Agent contract change."""

import unittest
from unittest import mock

import pytest

from _client_transport import create_client_with_transport
from config import settings
from azure.core.pipeline.transport import RequestsTransport  # pylint: disable=no-name-in-module
import azure.cosmos
from azure.cosmos import CosmosClient, cosmos_client
from azure.cosmos.exceptions import CosmosResourceNotFoundError


@pytest.mark.cosmosEmulator
class TestsUtils(unittest.TestCase):
    def _delete_owned_database(self, client, database_id):
        try:
            client.delete_database(database_id)
        except CosmosResourceNotFoundError:
            pass

    def test_connection_string_rust(self):
        # Source: tests/test_utils.py::TestsUtils.test_connection_string
        client: CosmosClient = (azure.cosmos.CosmosClient
                                .from_connection_string(settings.TestSettings.connection_str,
                                                        consistency_level="Session", _backend="rust"))
        self.addCleanup(client.close)
        database_id = settings.unique_database_id("connection-string")
        self.addCleanup(self._delete_owned_database, client, database_id)
        db = client.create_database(database_id)
        self.assertTrue(db is not None)
        client.delete_database(db.id)


@pytest.mark.cosmosEmulator
class TestClientOptionWiring(unittest.IsolatedAsyncioTestCase):
    def test_sync_connection_string_forwards_option_rust(self):
        """The option survives the from_connection_string entry point."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_item_body_serialization.py::TestClientOptionWiring.test_sync_connection_string_forwards_option
        with mock.patch.object(cosmos_client.CosmosClient, "__init__", return_value=None) as init:
            cosmos_client.CosmosClient.from_connection_string(
                "AccountEndpoint=https://example.test;AccountKey=credential;",
                enable_compact_utf8_item_writes=True,
                _backend="rust",
            )

        self.assertTrue(init.call_args.kwargs["enable_compact_utf8_item_writes"])


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestUserAgentOverwriteRegression(unittest.TestCase):
    connection_str = settings.TestSettings.connection_str

    def test_overwrite_via_from_connection_string_rust(self):
        """accepted-vnext-change: User-Agent rejection (Gap 33, Bite 14).

        Decision: RUST_PARITY_PUSHBACKS.md#client-bite-14.
        This verifies the intentional exclusion, not legacy header parity.
        """
        # pylint: disable-next=line-too-long
        # Source: tests/test_user_agent_overwrite_regression.py::TestUserAgentOverwriteRegression.test_overwrite_via_from_connection_string
        with self.assertRaisesRegex(TypeError, "user_agent is not supported by Rust-backed APIs"):
            CosmosClient.from_connection_string(
                self.connection_str,
                user_agent="MyApp/1.0",
                user_agent_overwrite=True,
                _backend="rust",
            )
