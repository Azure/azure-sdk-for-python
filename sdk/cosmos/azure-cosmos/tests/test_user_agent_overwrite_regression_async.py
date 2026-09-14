# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests that constructing an async client with ``user_agent_overwrite`` does not crash.

Covers combinations of the flag with other construction-time options
(connection policy, consistency level, timeouts, logger, connection string,
AAD credential) and checks that the user-supplied user-agent prefix shows up
on outbound requests.
"""

import unittest

import pytest
from azure.core.pipeline.transport import AioHttpTransport

import test_config
from azure.cosmos import documents
from azure.cosmos.aio import CosmosClient
from test_aad_async import CosmosEmulatorCredential
from test_cosmos_http_logging_policy import create_logger


class _AsyncUserAgentCaptureTransport(AioHttpTransport):
    """Forwards every request and records the outbound User-Agent header."""

    def __init__(self):
        super().__init__()
        self.user_agents: list[str] = []

    async def send(self, request, **kwargs):
        ua = request.headers.get("User-Agent")
        if ua is not None:
            self.user_agents.append(ua)
        return await super().send(request, **kwargs)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestUserAgentOverwriteRegressionAsync(unittest.IsolatedAsyncioTestCase):
    """User-agent overwrite construction tests for the async client."""

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connection_str = configs.connection_str
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_SINGLE_PARTITION_CONTAINER_ID = configs.TEST_SINGLE_PARTITION_CONTAINER_ID

    _skip_on_non_emulator = pytest.mark.skipif(
        not configs.is_emulator,
        reason="Uses the emulator credential; only valid against the local emulator.",
    )

    @classmethod
    def setUpClass(cls):
        if cls.masterKey == "[YOUR_KEY_HERE]" or cls.host == "[YOUR_ENDPOINT_HERE]":
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' to run the tests.")

    async def _smoke_data_plane_call(self, client: CosmosClient) -> None:
        """Reads a container so the test fails if the client cannot actually be used."""
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_SINGLE_PARTITION_CONTAINER_ID)
        result = await container.read()
        assert result["id"] == container.id

    def _assert_user_agent_headers(self, capture: _AsyncUserAgentCaptureTransport, scenario: str) -> None:
        assert capture.user_agents, f"no outbound requests captured for {scenario}"
        assert all(ua.startswith("MyApp/1.0") for ua in capture.user_agents), (
            "user-agent prefix dropped for {}. captured={}".format(scenario, capture.user_agents)
        )
        assert all("azsdk-python-cosmos-async/" in ua for ua in capture.user_agents), (
            "async SDK user-agent missing for {}. captured={}".format(scenario, capture.user_agents)
        )

    async def test_overwrite_with_connection_policy_async(self):
        """Builds a client with a custom connection policy and the overwrite flag."""
        cp = documents.ConnectionPolicy()
        cp.DisableSSLVerification = self.configs.is_emulator
        capture = _AsyncUserAgentCaptureTransport()
        client = CosmosClient(
            self.host,
            self.masterKey,
            user_agent="MyApp/1.0",
            user_agent_overwrite=True,
            connection_policy=cp,
            transport=capture,
        )
        try:
            await self._smoke_data_plane_call(client)
        finally:
            await client.close()
        self._assert_user_agent_headers(capture, "connection_policy_async")

    async def test_overwrite_with_consistency_and_timeouts_async(self):
        """Builds a client combining the overwrite flag with consistency and timeout options."""
        capture = _AsyncUserAgentCaptureTransport()
        client = CosmosClient(
            self.host,
            self.masterKey,
            user_agent="MyApp/1.0",
            user_agent_overwrite=True,
            consistency_level="Session",
            connection_timeout=10,
            read_timeout=10,
            transport=capture,
        )
        try:
            await self._smoke_data_plane_call(client)
        finally:
            await client.close()
        self._assert_user_agent_headers(capture, "consistency_and_timeouts_async")

    async def test_overwrite_with_logger_and_diagnostics_async(self):
        """Builds a client combining the overwrite flag with a user-provided logger."""
        mock_handler = test_config.MockHandler()
        logger = create_logger("test_ua_overwrite_diag_async", mock_handler)
        capture = _AsyncUserAgentCaptureTransport()
        client = CosmosClient(
            self.host,
            self.masterKey,
            user_agent="MyApp/1.0",
            user_agent_overwrite=True,
            logger=logger,
            enable_diagnostics_logging=True,
            transport=capture,
        )
        try:
            await self._smoke_data_plane_call(client)
        finally:
            await client.close()
        self._assert_user_agent_headers(capture, "logger_and_diagnostics_async")

    async def test_overwrite_header_contains_user_prefix_under_both_flag_values_async(self):
        """User-supplied user-agent prefix appears on the wire with the flag on or off.

        The Cosmos SDK always keeps its base user-agent in the header, so the
        overwrite flag does not actually replace it. This pins down that
        observable behavior and confirms neither flag value crashes the client.
        """
        for overwrite_value in (True, False):
            capture = _AsyncUserAgentCaptureTransport()
            client = CosmosClient(
                self.host,
                self.masterKey,
                user_agent="MyApp/1.0",
                user_agent_overwrite=overwrite_value,
                transport=capture,
            )
            try:
                await self._smoke_data_plane_call(client)
            finally:
                await client.close()
            self._assert_user_agent_headers(capture, f"overwrite={overwrite_value}")

    async def test_overwrite_via_from_connection_string_async(self):
        """Builds a client from a connection string while also passing the overwrite flag."""
        capture = _AsyncUserAgentCaptureTransport()
        client = CosmosClient.from_connection_string(
            self.connection_str,
            user_agent="MyApp/1.0",
            user_agent_overwrite=True,
            transport=capture,
        )
        try:
            await self._smoke_data_plane_call(client)
        finally:
            await client.close()
        self._assert_user_agent_headers(capture, "from_connection_string_async")

    @_skip_on_non_emulator
    async def test_overwrite_with_aad_emulator_credential_async(self):
        """Builds a client with an AAD credential while also passing the overwrite flag."""
        credential = CosmosEmulatorCredential()
        capture = _AsyncUserAgentCaptureTransport()
        client = CosmosClient(
            self.host,
            credential,
            user_agent="MyApp/1.0",
            user_agent_overwrite=True,
            transport=capture,
        )
        try:
            await self._smoke_data_plane_call(client)
        finally:
            await client.close()
        self._assert_user_agent_headers(capture, "aad_emulator_credential_async")


if __name__ == "__main__":
    unittest.main()


