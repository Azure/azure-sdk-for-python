# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import unittest
from unittest.mock import patch
from azure.appconfiguration.provider._client_manager import ConfigurationClientManager


class MockClient:

    def __init__(self, endpoint, connection_string, credential, retry_total, retry_backoff):
        self.endpoint = endpoint
        self.connection_string = connection_string
        self.credential = credential
        self.retry_total = retry_total
        self.retry_backoff = retry_backoff


@pytest.mark.usefixtures("caplog")
class TestConfigurationClientManagerLoadBalance(unittest.TestCase):

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider._client_manager.AzureAppConfigurationClient.from_connection_string")
    def test_find_active_clients(self, mock_client, mock_find_auto_failover_endpoints):
        # Single endpoint test no load balancing
        endpoint = "https://fake.endpoint"
        connection_string = "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret"

        mock_find_auto_failover_endpoints.return_value = []

        with ConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, False) as manager:
            assert manager.get_next_active_client() is None

            manager.find_active_clients()
            assert len(manager._active_clients) == 1

        # Multiple endpoint test no load balancing
        failover_endpoints = ["https://fake.endpoint2", "https://fake.endpoint3"]
        mock_find_auto_failover_endpoints.return_value = failover_endpoints

        manager = ConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, False)
        manager.refresh_clients()

        manager.find_active_clients()

        assert len(manager._active_clients) == 3
        assert manager._active_clients[0].endpoint in failover_endpoints + [endpoint]
        assert manager._active_clients[1].endpoint in failover_endpoints + [endpoint]
        assert manager._active_clients[2].endpoint in failover_endpoints + [endpoint]

        # Single endpoint test load balancing
        mock_find_auto_failover_endpoints.return_value = []

        manager = ConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, True)
        manager.refresh_clients()

        manager.find_active_clients()
        assert len(manager._active_clients) == 1

        # Multiple endpoint test load balancing
        mock_find_auto_failover_endpoints.return_value = ["https://fake.endpoint2", "https://fake.endpoint3"]

        manager = ConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, True)
        manager.refresh_clients()

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

        manager.close()

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider._client_manager.AzureAppConfigurationClient")
    def test_find_active_clients_entra_id(self, mock_client, mock_find_auto_failover_endpoints):
        # Single endpoint test no load balancing
        endpoint = "https://fake.endpoint"

        mock_find_auto_failover_endpoints.return_value = []

        with ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, False) as manager:
            assert manager.get_next_active_client() is None

            manager.find_active_clients()
            assert len(manager._active_clients) == 1

        # Multiple endpoint test no load balancing
        failover_endpoints = ["https://fake.endpoint2", "https://fake.endpoint3"]
        mock_find_auto_failover_endpoints.return_value = failover_endpoints

        manager = ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, True)
        manager.refresh_clients()

        manager.find_active_clients()

        assert len(manager._active_clients) == 3
        assert manager._active_clients[0].endpoint in failover_endpoints + [endpoint]
        assert manager._active_clients[1].endpoint in failover_endpoints + [endpoint]
        assert manager._active_clients[2].endpoint in failover_endpoints + [endpoint]

        # Single endpoint test load balancing
        mock_find_auto_failover_endpoints.return_value = []

        manager = ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, True)
        manager.refresh_clients()

        manager.find_active_clients()
        assert len(manager._active_clients) == 1

        # Multiple endpoint test load balancing
        mock_find_auto_failover_endpoints.return_value = ["https://fake.endpoint2", "https://fake.endpoint3"]

        manager = ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, True)
        manager.refresh_clients()

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

        manager.close()
