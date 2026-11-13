# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async Rust connection-string scenarios, including an intentional User-Agent contract change."""

import unittest
from unittest import mock

import pytest

from _client_transport import create_client_with_transport
from config import settings
from azure.core.pipeline.transport import AioHttpTransport  # pylint: disable=no-name-in-module
from azure.cosmos.aio import CosmosClient, _cosmos_client


@pytest.mark.cosmosEmulator
class TestClientOptionWiring(unittest.IsolatedAsyncioTestCase):
    def test_async_connection_string_forwards_option_rust(self):
        """Async twin of the from_connection_string check."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_item_body_serialization.py::TestClientOptionWiring.test_async_connection_string_forwards_option
        with mock.patch.object(_cosmos_client.CosmosClient, "__init__", return_value=None) as init:
            _cosmos_client.CosmosClient.from_connection_string(
                "AccountEndpoint=https://example.test;AccountKey=credential;",
                enable_compact_utf8_item_writes=True,
                _backend="rust",
            )

        self.assertTrue(init.call_args.kwargs["enable_compact_utf8_item_writes"])


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestUserAgentOverwriteRegressionAsync(unittest.IsolatedAsyncioTestCase):
    connection_str = settings.TestSettings.connection_str

    async def test_overwrite_via_from_connection_string_async_rust(self):
        """accepted-vnext-change: User-Agent rejection (Gap 33, Bite 14).

        Decision: RUST_PARITY_PUSHBACKS.md#client-bite-14.
        This verifies the intentional exclusion, not legacy header parity.
        """
        # pylint: disable-next=line-too-long
        # Source: tests/test_user_agent_overwrite_regression_async.py::TestUserAgentOverwriteRegressionAsync.test_overwrite_via_from_connection_string_async
        with self.assertRaisesRegex(TypeError, "user_agent is not supported by Rust-backed APIs"):
            CosmosClient.from_connection_string(
                self.connection_str,
                user_agent="MyApp/1.0",
                user_agent_overwrite=True,
                _backend="rust",
            )
