# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import unittest
from unittest.mock import patch
from azure.appconfiguration.provider.aio._async_client_manager import AsyncConfigurationClientManager


class MockClient:

    def __init__(self, endpoint, connection_string, credential, retry_total, retry_backoff):
        self.endpoint = endpoint
        self.connection_string = connection_string
        self.credential = credential
        self.retry_total = retry_total
        self.retry_backoff = retry_backoff


@pytest.mark.usefixtures("caplog")
class TestConfigurationAsyncClientManagerLoadBalance:

    @pytest.mark.asyncio
    @patch("azure.appconfiguration.provider.aio._async_client_manager.find_auto_failover_endpoints")
    @patch(
        "azure.appconfiguration.provider.aio._async_client_manager.AzureAppConfigurationClient.from_connection_string"
    )
    async def test_find_active_clients(self, mock_client, mock_find_auto_failover_endpoints):
        # Single endpoint test no load balancing
        endpoint = "https://fake.endpoint"
        connection_string = "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret"

        mock_find_auto_failover_endpoints.return_value = []

        manager = AsyncConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, False)
        assert manager.get_next_active_client() is None

        manager.find_active_clients()
        assert len(manager._active_clients) == 1

        # Multiple endpoint test no load balancing
        failover_endpoints = ["https://fake.endpoint2", "https://fake.endpoint3"]
        mock_find_auto_failover_endpoints.return_value = failover_endpoints

        manager = AsyncConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, False)
        await manager.refresh_clients()

        manager.find_active_clients()

        assert len(manager._active_clients) == 3
        assert manager._active_clients[0].endpoint in failover_endpoints + [endpoint]
        assert manager._active_clients[1].endpoint in failover_endpoints + [endpoint]
        assert manager._active_clients[2].endpoint in failover_endpoints + [endpoint]

        # Single endpoint test load balancing
        mock_find_auto_failover_endpoints.return_value = []

        manager = AsyncConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, True)
        await manager.refresh_clients()

        manager.find_active_clients()
        assert len(manager._active_clients) == 1

        # Multiple endpoint test load balancing
        mock_find_auto_failover_endpoints.return_value = ["https://fake.endpoint2", "https://fake.endpoint3"]

        manager = AsyncConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, True)
        await manager.refresh_clients()

        manager.find_active_clients()
        assert len(manager._active_clients) == 3
        endpoint_list = [client.endpoint for client in manager._active_clients]
        next_client = manager.get_next_active_client()
        assert next_client is not None
        assert next_client.endpoint == endpoint_list[0]
        manager.find_active_clients()
        assert manager._active_clients[0].endpoint == endpoint_list[1]
        assert manager._active_clients[1].endpoint == endpoint_list[2]
        assert manager._active_clients[2].endpoint == endpoint_list[0]
        next_client = manager.get_next_active_client()
        assert next_client is not None
        assert next_client.endpoint == endpoint_list[1]
        manager.find_active_clients()
        manager.get_next_active_client()
        manager.find_active_clients()
        assert manager._active_clients[0].endpoint == endpoint_list[0]
        assert manager._active_clients[1].endpoint == endpoint_list[1]
        assert manager._active_clients[2].endpoint == endpoint_list[2]
        next_client = manager.get_next_active_client()
        assert next_client is not None
        assert next_client.endpoint == endpoint_list[0]

    @pytest.mark.asyncio
    @patch("azure.appconfiguration.provider.aio._async_client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider.aio._async_client_manager.AzureAppConfigurationClient")
    async def test_find_active_clients_entra_id(self, mock_client, mock_find_auto_failover_endpoints):
        # Single endpoint test no load balancing
        endpoint = "https://fake.endpoint"

        mock_find_auto_failover_endpoints.return_value = []

        manager = AsyncConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, False)
        assert manager.get_next_active_client() is None

        manager.find_active_clients()
        assert len(manager._active_clients) == 1

        # Multiple endpoint test no load balancing
        failover_endpoints = ["https://fake.endpoint2", "https://fake.endpoint3"]
        mock_find_auto_failover_endpoints.return_value = failover_endpoints

        manager = AsyncConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, True)
        await manager.refresh_clients()

        manager.find_active_clients()

        assert len(manager._active_clients) == 3
        assert manager._active_clients[0].endpoint in failover_endpoints + [endpoint]
        assert manager._active_clients[1].endpoint in failover_endpoints + [endpoint]
        assert manager._active_clients[2].endpoint in failover_endpoints + [endpoint]

        # Single endpoint test load balancing
        mock_find_auto_failover_endpoints.return_value = []

        manager = AsyncConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, True)
        await manager.refresh_clients()

        manager.find_active_clients()
        assert len(manager._active_clients) == 1

        # Multiple endpoint test load balancing
        mock_find_auto_failover_endpoints.return_value = ["https://fake.endpoint2", "https://fake.endpoint3"]

        manager = AsyncConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, True)
        await manager.refresh_clients()

        manager.find_active_clients()
        assert len(manager._active_clients) == 3
        endpoint_list = [client.endpoint for client in manager._active_clients]
        next_client = manager.get_next_active_client()
        assert next_client is not None
        assert next_client.endpoint == endpoint_list[0]
        manager.find_active_clients()
        assert manager._active_clients[0].endpoint == endpoint_list[1]
        assert manager._active_clients[1].endpoint == endpoint_list[2]
        assert manager._active_clients[2].endpoint == endpoint_list[0]
        next_client = manager.get_next_active_client()
        assert next_client is not None
        assert next_client.endpoint == endpoint_list[1]
        manager.find_active_clients()
        manager.get_next_active_client()
        manager.find_active_clients()
        assert manager._active_clients[0].endpoint == endpoint_list[0]
        assert manager._active_clients[1].endpoint == endpoint_list[1]
        assert manager._active_clients[2].endpoint == endpoint_list[2]
        next_client = manager.get_next_active_client()
        assert next_client is not None
        assert next_client.endpoint == endpoint_list[0]
