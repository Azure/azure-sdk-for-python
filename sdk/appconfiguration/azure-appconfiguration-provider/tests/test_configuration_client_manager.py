# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import unittest
from unittest.mock import patch, call
from azure.appconfiguration.provider._client_manager import ConfigurationClientManager


class MockClient:

    def __init__(self, endpoint, connection_string, credential, retry_total, retry_backoff):
        self.endpoint = endpoint
        self.connection_string = connection_string
        self.credential = credential
        self.retry_total = retry_total
        self.retry_backoff = retry_backoff


@pytest.mark.usefixtures("caplog")
class TestConfigurationClientManager(unittest.TestCase):

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider._client_manager._ConfigurationClientWrapper.from_connection_string")
    def test_create_client_manager_connection_string(self, mock_client, mock_update_failover_endpoints):
        endpoint = "https://fake.endpoint"

        # No connection string or credential was provided
        with self.assertRaises(ValueError) as ex:
            ConfigurationClientManager(None, endpoint, None, "", 0, 0, True, 0, 0, False)
            assert (
                str(ex.exception) == "Please pass either endpoint and credential, or a connection string with a value."
            )
        mock_update_failover_endpoints.assert_not_called()
        mock_client.assert_not_called()

        connection_string = "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret"

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No auto failover endpoints found
        mock_update_failover_endpoints.return_value = []
        manager = ConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, False)
        manager.refresh_clients()
        assert len(manager._replica_clients) == 1
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        mock_client.assert_called_once_with(endpoint, connection_string, "", 0, 0)

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A single auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        manager = ConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, False)
        manager.refresh_clients()
        assert len(manager._replica_clients) == 2
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        connection_string2 = "Endpoint=https://fake.endpoint2/;Id=fake_id;Secret=fake_secret"
        mock_client.assert_has_calls(
            [
                call(endpoint, connection_string, "", 0, 0),
                call().endpoint.__eq__("https://fake.endpoint2"),
                call("https://fake.endpoint2", connection_string2, "", 0, 0),
            ]
        )

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider._client_manager._ConfigurationClientWrapper.from_credential")
    def test_create_client_manager_endpoint(self, mock_client, mock_update_failover_endpoints):
        endpoint = "https://fake.endpoint"

        # No connection string or credential was provided
        with self.assertRaises(ValueError) as ex:
            ConfigurationClientManager(None, endpoint, None, "", 0, 0, True, 0, 0, False)
            assert (
                str(ex.exception) == "Please pass either endpoint and credential, or a connection string with a value."
            )
        mock_update_failover_endpoints.assert_not_called()
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No auto failover endpoints found
        mock_update_failover_endpoints.return_value = []
        manager = ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, False)
        manager.refresh_clients()
        assert len(manager._replica_clients) == 1
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        mock_client.assert_called_once_with(endpoint, "fake-credential", "", 0, 0)

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A single auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        manager = ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, False)
        manager.refresh_clients()
        assert len(manager._replica_clients) == 2
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        mock_client.assert_has_calls(
            [
                call(endpoint, "fake-credential", "", 0, 0),
                call().endpoint.__eq__("https://fake.endpoint2"),
                call("https://fake.endpoint2", "fake-credential", "", 0, 0),
            ]
        )

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider._client_manager._ConfigurationClientWrapper.from_credential")
    def test_refresh_clients_credential(self, mock_client, mock_update_failover_endpoints):
        endpoint = "https://fake.endpoint"

        mock_client.return_value = MockClient("https://fake.endpoint", "", "fake-credential", 0, 0)
        mock_update_failover_endpoints.return_value = []
        manager = ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, False)
        manager_disabled_refresh = ConfigurationClientManager(
            None, endpoint, "fake-credential", "", 0, 0, False, 0, 0, False
        )

        # Reset the mocks as they are called during initialization
        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # Refresh period reached but disabled
        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        manager_disabled_refresh.refresh_clients()
        mock_update_failover_endpoints.assert_not_called()
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No auto failover endpoints found
        mock_update_failover_endpoints.return_value = []
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A single auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        mock_client.return_value = MockClient("https://fake.endpoint2", "", "fake-credential", 0, 0)
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_called_once_with("https://fake.endpoint2", "fake-credential", "", 0, 0)

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No new auto failover endpoints found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # An additional auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2", "https://fake.endpoint3"]
        mock_client.return_value = MockClient("https://fake.endpoint3", "", "fake-credential", 0, 0)
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 3
        mock_client.assert_called_once_with("https://fake.endpoint3", "fake-credential", "", 0, 0)

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A replica no longer exists
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint3"]
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_not_called()

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider._client_manager._ConfigurationClientWrapper.from_connection_string")
    def test_refresh_clients_connection_string(self, mock_client, mock_update_failover_endpoints):
        endpoint = "https://fake.endpoint"

        mock_client.return_value = MockClient(
            "https://fake.endpoint", "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret", None, 0, 0
        )
        mock_update_failover_endpoints.return_value = []
        manager = ConfigurationClientManager(
            "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret", endpoint, None, "", 0, 0, True, 0, 0, False
        )
        manager_disabled_refresh = ConfigurationClientManager(
            "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret",
            endpoint,
            None,
            "",
            0,
            0,
            False,
            0,
            0,
            False,
        )

        # Reset the mocks as they are called during initialization
        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # Refresh period reached but disabled
        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        manager_disabled_refresh.refresh_clients()
        mock_update_failover_endpoints.assert_not_called()
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No auto failover endpoints found
        mock_update_failover_endpoints.return_value = []
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A single auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        mock_client.return_value = MockClient(
            "https://fake.endpoint2", "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret", None, 0, 0
        )
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_called_once_with(
            "https://fake.endpoint2", "Endpoint=https://fake.endpoint2/;Id=fake_id;Secret=fake_secret", "", 0, 0
        )

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No new auto failover endpoints found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # An additional auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2", "https://fake.endpoint3"]
        mock_client.return_value = MockClient(
            "https://fake.endpoint3", "Endpoint=https://fake.endpoint3/;Id=fake_id;Secret=fake_secret", None, 0, 0
        )
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 3
        mock_client.assert_called_once_with(
            "https://fake.endpoint3", "Endpoint=https://fake.endpoint3/;Id=fake_id;Secret=fake_secret", "", 0, 0
        )

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A replica no longer exists
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint3"]
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_not_called()

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider._client_manager._ConfigurationClientWrapper.from_credential")
    def test_calculate_backoff(self, mock_client, mock_update_failover_endpoints):
        endpoint = "https://fake.endpoint"
        mock_update_failover_endpoints.return_value = []
        manager = ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 30, 600, False)
        manager_invalid = ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 600, 30, False)

        assert manager._calculate_backoff(0) == 30000.0
        assert 30000.0 <= manager._calculate_backoff(1) <= 60000.0
        assert 30000.0 <= manager._calculate_backoff(2) <= 120000.0
        assert 30000.0 <= manager._calculate_backoff(3) <= 240000.0
        assert 30000.0 <= manager._calculate_backoff(4) <= 480000.0
        assert 30000.0 <= manager._calculate_backoff(5) <= 600000.0
        assert 30000.0 <= manager._calculate_backoff(6) <= 600000.0
        assert 30000.0 <= manager._calculate_backoff(7) <= 600000.0
        assert 30000.0 <= manager._calculate_backoff(8) <= 600000.0
        assert 30000.0 <= manager._calculate_backoff(9) <= 600000.0
        assert 30000.0 <= manager._calculate_backoff(10) <= 600000.0

        assert manager_invalid._calculate_backoff(0) == 600000
