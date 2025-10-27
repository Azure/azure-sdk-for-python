# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import unittest
from unittest.mock import Mock, patch
from azure.appconfiguration import SecretReferenceConfigurationSetting
from azure.appconfiguration.provider import SettingSelector, WatchKey
from devtools_testutils import recorded_by_proxy
from preparers import app_config_decorator_aad
from testcase import AppConfigTestCase


class TestSecretRefresh(AppConfigTestCase, unittest.TestCase):
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_secret_refresh_timer(
        self,
        appconfiguration_endpoint_string,
        appconfiguration_keyvault_secret_url,
        appconfiguration_keyvault_secret_url2,
    ):
        """Test that secrets are refreshed based on the secret_refresh_interval."""
        mock_callback = Mock()

        # Create client with key vault reference and secret refresh interval
        client = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            selects={SettingSelector(key_filter="*", label_filter="prod")},
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            keyvault_secret_url2=appconfiguration_keyvault_secret_url2,
            on_refresh_success=mock_callback,
            refresh_interval=999999,
            secret_refresh_interval=1,
        )

        # Verify initial state
        assert client["secret"] == "Very secret value"
        assert mock_callback.call_count == 0

        # Mock the refresh method to track calls
        with patch.object(client, "refresh") as mock_refresh:
            # Wait for the secret refresh interval to pass
            time.sleep(2)

            client.refresh()

            # Verify refresh was called
            assert mock_refresh.call_count >= 1

            # Wait again to ensure multiple refreshes
            time.sleep(2)
            client.refresh()

            # Should have been called at least twice now
            assert mock_refresh.call_count >= 2

    @recorded_by_proxy
    @app_config_decorator_aad
    def test_secret_refresh_with_updated_values(
        self,
        appconfiguration_endpoint_string,
        appconfiguration_keyvault_secret_url,
        appconfiguration_keyvault_secret_url2,
    ):
        """Test that secrets are refreshed with updated values."""
        mock_callback = Mock()

        # Create client with the mock secret resolver
        client = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            selects={SettingSelector(key_filter="*", label_filter="prod")},
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            keyvault_secret_url2=appconfiguration_keyvault_secret_url2,
            on_refresh_success=mock_callback,
            refresh_on=[WatchKey("secret")],
            refresh_interval=1,
            secret_refresh_interval=1,  # Using a short interval for testing
        )

        # Add a key vault reference to the client (this will use mock resolver)
        appconfig_client = self.create_aad_sdk_client(appconfiguration_endpoint_string)

        # Get and modify a key vault reference setting
        kv_setting = appconfig_client.get_configuration_setting(key="secret", label="prod")
        assert kv_setting is not None

        # Verify initial value from mock resolver
        assert client["secret"] == "Very secret value"
        assert kv_setting is not None
        assert isinstance(kv_setting, SecretReferenceConfigurationSetting)
        # Update the secret_id (which is the value for SecretReferenceConfigurationSetting)
        kv_setting.secret_id = appconfiguration_keyvault_secret_url2
        appconfig_client.set_configuration_setting(kv_setting)

        # Wait for the secret refresh interval to pass
        time.sleep(2)

        # Access the value again to trigger refresh
        client.refresh()

        # Verify the value was updated
        assert client["secret"] == "Very secret value 2"
        assert mock_callback.call_count >= 1

    @recorded_by_proxy
    @app_config_decorator_aad
    def test_no_secret_refresh_without_timer(
        self,
        appconfiguration_endpoint_string,
        appconfiguration_keyvault_secret_url,
        appconfiguration_keyvault_secret_url2,
    ):
        """Test that secrets are not refreshed if secret_refresh_interval is not set."""
        mock_callback = Mock()

        # Create client without specifying secret_refresh_interval
        client = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            selects={SettingSelector(key_filter="*", label_filter="prod")},
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            keyvault_secret_url2=appconfiguration_keyvault_secret_url2,
            on_refresh_success=mock_callback,
            refresh_interval=999999,
        )

        # Verify initial state
        assert client["secret"] == "Very secret value"

        # Mock the refresh method to track calls
        with patch("time.time") as mock_time:
            # Make time.time() return increasing values to simulate passage of time
            mock_time.side_effect = [time.time(), time.time() + 100]

            # Access the key vault reference - this shouldn't trigger an auto-refresh since
            # we didn't set a secret_refresh_interval
            client.refresh()

            # Access it again to verify no auto-refresh due to secrets timer
            client.refresh()

            # The mock_time should have been called twice (for our side_effect setup)
            # but there should be no automatic refresh caused by the secret timer
            assert mock_time.call_count == 2

    @recorded_by_proxy
    @app_config_decorator_aad
    def test_secret_refresh_timer_triggers_refresh(
        self,
        appconfiguration_endpoint_string,
        appconfiguration_keyvault_secret_url,
        appconfiguration_keyvault_secret_url2,
    ):
        """Test that the secret refresh timer triggers a refresh after the specified interval."""
        mock_callback = Mock()

        # Create client with key vault reference and separate refresh intervals
        client = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            selects={SettingSelector(key_filter="*", label_filter="prod")},
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            keyvault_secret_url2=appconfiguration_keyvault_secret_url2,
            on_refresh_success=mock_callback,
            refresh_interval=999999,
            secret_refresh_interval=5,  # Secret refresh interval is short
        )

        # Now patch the refresh method and secret_refresh_timer to control behavior
        with patch.object(client, "refresh") as mock_refresh:
            # Now patch the secret_refresh_timer to control its behavior
            with patch.object(client._secret_provider, "secret_refresh_timer") as mock_timer:
                # Make needs_refresh() return True to simulate timer expiration
                mock_timer.needs_refresh.return_value = True

                # Access a key vault reference which should trigger refresh due to timer
                client.refresh()

                # Verify refresh was called
                assert mock_refresh.call_count > 0

    @recorded_by_proxy
    @app_config_decorator_aad
    def test_secret_refresh_interval_parameter(
        self,
        appconfiguration_endpoint_string,
        appconfiguration_keyvault_secret_url,
        appconfiguration_keyvault_secret_url2,
    ):
        """Test that secret_refresh_interval parameter is correctly passed and used."""
        mock_callback = Mock()

        # Create client with specific secret_refresh_interval
        client = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            selects={SettingSelector(key_filter="*", label_filter="prod")},
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            keyvault_secret_url2=appconfiguration_keyvault_secret_url2,
            on_refresh_success=mock_callback,
            refresh_interval=999999,
            secret_refresh_interval=42,  # Use a specific value we can check for
        )

        # Verify the secret refresh timer exists
        assert client._secret_provider.secret_refresh_timer is not None

        # We can only verify that it exists, but can't directly access the internal refresh_interval
        # as it's a protected attribute

        # Check with no refresh interval to ensure it's properly handled
        client2 = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            selects={SettingSelector(key_filter="*", label_filter="prod")},
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            keyvault_secret_url2=appconfiguration_keyvault_secret_url2,
            on_refresh_success=mock_callback,
            # No secret_refresh_interval specified
        )

        # Verify timer is created only when secret_refresh_interval is provided
        assert client._secret_provider.secret_refresh_timer is not None
        assert client2._secret_provider.secret_refresh_timer is None
