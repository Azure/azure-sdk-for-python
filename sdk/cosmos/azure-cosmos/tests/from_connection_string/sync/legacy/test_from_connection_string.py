# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original connection-string assertions with explicit Rust selection."""

import unittest
from unittest import mock

import pytest

from _client_transport import create_client_with_transport
import test_config
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
                                .from_connection_string(test_config.TestConfig.connection_str,
                                                        consistency_level="Session", _backend="rust"))
        self.addCleanup(client.close)
        database_id = test_config.unique_database_id("connection-string")
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


class _UserAgentCaptureTransport(RequestsTransport):
    """Forwards every request and records the outbound User-Agent header."""

    def __init__(self):
        super().__init__()
        self.user_agents: list[str] = []

    def send(self, request, **kwargs):
        ua = request.headers.get("User-Agent")
        if ua is not None:
            self.user_agents.append(ua)
        return super().send(request, **kwargs)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestUserAgentOverwriteRegression(unittest.TestCase):
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connection_str = configs.connection_str
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_SINGLE_PARTITION_CONTAINER_ID = configs.TEST_SINGLE_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        if cls.masterKey == "[YOUR_KEY_HERE]" or cls.host == "[YOUR_ENDPOINT_HERE]":
            raise Exception(  # pylint: disable=broad-exception-raised
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' to run the tests.")

    def _smoke_data_plane_call(self, client: CosmosClient) -> None:
        """Reads a container so the test fails if the client cannot actually be used."""
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_SINGLE_PARTITION_CONTAINER_ID)
        assert container.read()["id"] == container.id

    def _assert_user_agent_headers(self, capture: _UserAgentCaptureTransport, scenario: str) -> None:
        assert capture.user_agents, f"no outbound requests captured for {scenario}"
        assert all(ua.startswith("MyApp/1.0") for ua in capture.user_agents), (
            "user-agent prefix dropped for {}. captured={}".format(scenario, capture.user_agents)
        )
        assert all("azsdk-python-cosmos/" in ua for ua in capture.user_agents), (
            "sync SDK user-agent missing for {}. captured={}".format(scenario, capture.user_agents)
        )

    def test_overwrite_via_from_connection_string_rust(self):
        """Builds a client from a connection string while also passing the overwrite flag."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_user_agent_overwrite_regression.py::TestUserAgentOverwriteRegression.test_overwrite_via_from_connection_string
        capture = _UserAgentCaptureTransport()
        client = create_client_with_transport(CosmosClient.from_connection_string,
            self.connection_str,
            user_agent="MyApp/1.0",
            user_agent_overwrite=True,
            transport=capture,
            _backend="rust",
        )
        try:
            self._smoke_data_plane_call(client)
        finally:
            client.close()
        self._assert_user_agent_headers(capture, "from_connection_string")
