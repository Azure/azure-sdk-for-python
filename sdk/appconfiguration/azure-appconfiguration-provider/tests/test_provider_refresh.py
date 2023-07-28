# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import unittest
from azure.appconfiguration.provider import load, SettingSelector, SentinelKey
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.appconfiguration import AzureAppConfigurationClient
from preparers import app_config_decorator_aad


class TestAppConfigurationProvider(AzureRecordedTestCase, unittest.TestCase):
    def build_provider_aad(
        self, endpoint, trim_prefixes=[], selects={SettingSelector(key_filter="*", label_filter="\0")}, refresh_on=None
    ):
        cred = self.get_credential(AzureAppConfigurationClient)
        return load(
            credential=cred,
            endpoint=endpoint,
            trim_prefixes=trim_prefixes,
            selects=selects,
            refresh_on=refresh_on,
            refresh_interval=1,
        )

    def build_provider_aad_empty_refresh(
        self, endpoint, trim_prefixes=[], selects={SettingSelector(key_filter="*", label_filter="\0")}
    ):
        cred = self.get_credential(AzureAppConfigurationClient)
        return load(credential=cred, endpoint=endpoint, trim_prefixes=trim_prefixes, selects=selects)

    # method: refresh
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_refresh(self, appconfiguration_endpoint_string):
        client = self.build_provider_aad(appconfiguration_endpoint_string, refresh_on=[SentinelKey("refresh_message")])
        assert client["refresh_message"] == "original value"
        assert client["my_json"]["key"] == "value"
        assert (
            client["FeatureManagementFeatureFlags"]["Alpha"]
            == '{"enabled": false, "conditions": {"client_filters": []}}'
        )
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
    def test_empty_refresh(self, appconfiguration_endpoint_string):
        client = self.build_provider_aad_empty_refresh(appconfiguration_endpoint_string)
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"
        assert client["my_json"]["key"] == "value"
        assert (
            client["FeatureManagementFeatureFlags"]["Alpha"]
            == '{"enabled": false, "conditions": {"client_filters": []}}'
        )
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
