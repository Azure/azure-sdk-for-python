# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import time
import unittest
from unittest.mock import Mock
from devtools_testutils import EnvironmentVariableLoader, recorded_by_proxy
from testcase import AppConfigTestCase, has_feature_flag
from test_constants import (
    APPCONFIGURATION_ENDPOINT_STRING,
    APPCONFIGURATION_KEYVAULT_SECRET_URL,
    FEATURE_MANAGEMENT_KEY,
)

AppConfigProviderPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    appconfiguration_endpoint_string=APPCONFIGURATION_ENDPOINT_STRING,
    appconfiguration_keyvault_secret_url=APPCONFIGURATION_KEYVAULT_SECRET_URL,
)


class TestAppConfigurationProviderWatchAll(AppConfigTestCase, unittest.TestCase):
    # method: refresh (watch all - no refresh_on keys, refresh_enabled=True)
    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_watch_all(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        mock_callback = Mock()
        client = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            refresh_interval=1,
            on_refresh_success=mock_callback,
            feature_flag_enabled=True,
        )
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"
        assert client["my_json"]["key"] == "value"
        assert FEATURE_MANAGEMENT_KEY in client
        assert has_feature_flag(client, "Alpha")

        appconfig_client = self.create_aad_sdk_client(appconfiguration_endpoint_string)

        setting = appconfig_client.get_configuration_setting(key="refresh_message")
        setting.value = "updated value"
        appconfig_client.set_configuration_setting(setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        # Watch all should detect the change and refresh all settings
        assert client["refresh_message"] == "updated value"
        assert mock_callback.call_count == 1

        setting.value = "original value"
        appconfig_client.set_configuration_setting(setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "original value"
        assert mock_callback.call_count == 2

    # method: refresh (watch all - no changes should not trigger refresh)
    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_watch_all_no_change(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        mock_callback = Mock()
        client = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            refresh_interval=1,
            on_refresh_success=mock_callback,
            feature_flag_enabled=True,
        )
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"

        # Waiting for the refresh interval to pass
        time.sleep(2)

        # No settings changed, refresh should be a no-op
        client.refresh()
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"
        assert mock_callback.call_count == 0

    # method: refresh (watch all - should not trigger before refresh interval)
    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_watch_all_before_interval(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        mock_callback = Mock()
        client = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            refresh_interval=10,
            on_refresh_success=mock_callback,
            feature_flag_enabled=True,
        )
        assert client["refresh_message"] == "original value"

        appconfig_client = self.create_aad_sdk_client(appconfiguration_endpoint_string)

        setting = appconfig_client.get_configuration_setting(key="refresh_message")
        setting.value = "updated value"
        appconfig_client.set_configuration_setting(setting)

        # Not waiting for the refresh interval to pass
        client.refresh()
        # Should not refresh because the interval hasn't passed
        assert client["refresh_message"] == "original value"
        assert mock_callback.call_count == 0

        setting.value = "original value"
        appconfig_client.set_configuration_setting(setting)

    # method: refresh (watch all disabled via refresh_enabled=False)
    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_watch_all_disabled(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        mock_callback = Mock()
        client = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            refresh_interval=1,
            on_refresh_success=mock_callback,
            feature_flag_enabled=True,
            refresh_enabled=False,
        )
        assert client["refresh_message"] == "original value"

        appconfig_client = self.create_aad_sdk_client(appconfiguration_endpoint_string)

        setting = appconfig_client.get_configuration_setting(key="refresh_message")
        setting.value = "updated value"
        appconfig_client.set_configuration_setting(setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        # Refresh is disabled, watch all should not activate
        assert client["refresh_message"] == "original value"
        assert mock_callback.call_count == 0

        setting.value = "original value"
        appconfig_client.set_configuration_setting(setting)

    # method: refresh (watch all refreshes all settings including non-watched ones)
    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_watch_all_refreshes_all_settings(
        self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url
    ):
        mock_callback = Mock()
        client = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            refresh_interval=1,
            on_refresh_success=mock_callback,
            feature_flag_enabled=True,
        )
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"

        appconfig_client = self.create_aad_sdk_client(appconfiguration_endpoint_string)

        # Change multiple settings at once
        setting = appconfig_client.get_configuration_setting(key="refresh_message")
        setting.value = "updated value"
        appconfig_client.set_configuration_setting(setting)

        static_setting = appconfig_client.get_configuration_setting(key="non_refreshed_message")
        static_setting.value = "updated static"
        appconfig_client.set_configuration_setting(static_setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        # Watch all should detect changes and refresh everything
        assert client["refresh_message"] == "updated value"
        assert client["non_refreshed_message"] == "updated static"
        assert mock_callback.call_count == 1

        # Restore original values
        setting.value = "original value"
        appconfig_client.set_configuration_setting(setting)
        static_setting.value = "Static"
        appconfig_client.set_configuration_setting(static_setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"
        assert mock_callback.call_count == 2

    # method: refresh (empty refresh - no refresh_on and no refresh_interval should not trigger)
    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_empty_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        mock_callback = Mock()
        client = self.create_client(
            endpoint=appconfiguration_endpoint_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            on_refresh_success=mock_callback,
            feature_flag_enabled=True,
        )
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"
        assert client["my_json"]["key"] == "value"
        assert FEATURE_MANAGEMENT_KEY in client
        assert has_feature_flag(client, "Alpha")

        appconfig_client = self.create_aad_sdk_client(appconfiguration_endpoint_string)

        setting = appconfig_client.get_configuration_setting(key="refresh_message")
        setting.value = "updated value"
        appconfig_client.set_configuration_setting(setting)
        static_setting = appconfig_client.get_configuration_setting(key="non_refreshed_message")
        static_setting.value = "updated static"
        appconfig_client.set_configuration_setting(static_setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"
        assert mock_callback.call_count == 0

        setting.value = "original value"
        appconfig_client.set_configuration_setting(setting)
        static_setting.value = "Static"
        appconfig_client.set_configuration_setting(static_setting)
