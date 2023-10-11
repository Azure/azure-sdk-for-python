# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import unittest
from azure.appconfiguration.provider import load, SettingSelector, SentinelKey
from devtools_testutils import recorded_by_proxy
from azure.appconfiguration import AzureAppConfigurationClient
from preparers import app_config_decorator_aad
from testcase import AppConfigTestCase


class TestAppConfigurationProvider(AppConfigTestCase, unittest.TestCase):
    # method: refresh
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        client = self.create_aad_client(
            appconfiguration_endpoint_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            refresh_on=[SentinelKey("refresh_message")],
            refresh_interval=1,
        )
        assert client["refresh_message"] == "original value"
        assert client["my_json"]["key"] == "value"
        assert "FeatureManagementFeatureFlags" in client
        assert "Alpha" in client["FeatureManagementFeatureFlags"]

        setting = client._client.get_configuration_setting(key="refresh_message")
        setting.value = "updated value"
        client._client.set_configuration_setting(setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "updated value"

        setting.value = "original value"
        client._client.set_configuration_setting(setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "original value"

        setting.value = "updated value 2"
        client._client.set_configuration_setting(setting)

        # Not waiting for the refresh interval to pass
        client.refresh()
        assert client["refresh_message"] == "original value"

        setting.value = "original value"
        client._client.set_configuration_setting(setting)

        client.refresh()
        assert client["refresh_message"] == "original value"

    # method: refresh
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_empty_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        client = self.create_aad_client(
            appconfiguration_endpoint_string, keyvault_secret_url=appconfiguration_keyvault_secret_url
        )
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"
        assert client["my_json"]["key"] == "value"
        assert "FeatureManagementFeatureFlags" in client
        assert "Alpha" in client["FeatureManagementFeatureFlags"]

        setting = client._client.get_configuration_setting(key="refresh_message")
        setting.value = "updated value"
        client._client.set_configuration_setting(setting)
        static_setting = client._client.get_configuration_setting(key="non_refreshed_message")
        static_setting.value = "updated static"
        client._client.set_configuration_setting(static_setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"

        setting.value = "original value"
        client._client.set_configuration_setting(setting)
        static_setting.value = "Static"
        client._client.set_configuration_setting(static_setting)

    def my_callback(self):
        assert True

    def my_callback_on_fail(self):
        assert False
