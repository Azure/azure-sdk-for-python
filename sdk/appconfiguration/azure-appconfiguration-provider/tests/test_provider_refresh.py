# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
from azure.appconfiguration.provider import load, SettingSelector, AzureAppConfigurationRefreshOptions
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.appconfiguration import AzureAppConfigurationClient
from preparers import app_config_decorator_aad


class TestAppConfigurationProvider(AzureRecordedTestCase):
    def build_provider_aad(
        self,
        endpoint,
        trim_prefixes=[],
        selects={SettingSelector(key_filter="*", label_filter="\0")},
        refresh_key="message",
        refresh_all=True,
    ):
        refresh_options = AzureAppConfigurationRefreshOptions()
        refresh_options.refresh_interval = 1
        refresh_options.register(key_filter=refresh_key, refresh_all=refresh_all)
        refresh_options.callback = self.my_callback
        refresh_options.callback_on_fail = self.my_callback_on_fail
        cred = self.get_credential(AzureAppConfigurationClient)
        return load(
            credential=cred,
            endpoint=endpoint,
            trim_prefixes=trim_prefixes,
            selects=selects,
            refresh_options=refresh_options,
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
        client = self.build_provider_aad(
            appconfiguration_endpoint_string, refresh_key="refresh_message", refresh_all=False
        )
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
        assert client["refresh_message"] == "updated value"
        assert client["non_refreshed_message"] == "Static"

        setting.value = "original value"
        client._client.set_configuration_setting(setting)
        static_setting.value = "Static"
        client._client.set_configuration_setting(static_setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"

    # method: refresh
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_refresh_all(self, appconfiguration_endpoint_string):
        client = self.build_provider_aad(appconfiguration_endpoint_string, refresh_key="refresh_all_message")
        assert client["refresh_all_message"] == "original value"
        assert client["my_json"]["key"] == "value"
        assert (
            client["FeatureManagementFeatureFlags"]["Alpha"]
            == '{"enabled": false, "conditions": {"client_filters": []}}'
        )
        setting = client._client.get_configuration_setting(key="refresh_all_message")
        setting.value = "updated value"
        client._client.set_configuration_setting(setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_all_message"] == "updated value"

        setting.value = "original value"
        client._client.set_configuration_setting(setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_all_message"] == "original value"

        setting.value = "updated value 2"
        client._client.set_configuration_setting(setting)

        # Not waiting for the refresh interval to pass
        client.refresh()
        assert client["refresh_all_message"] == "original value"

        setting.value = "original value"
        client._client.set_configuration_setting(setting)

        client.refresh()
        assert client["refresh_all_message"] == "original value"

    def my_callback(self):
        assert True

    def my_callback_on_fail(self):
        assert False

    # method: refresh decorator
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_refresh_decorator(self, appconfiguration_endpoint_string):
        client = self.build_provider_aad(
            appconfiguration_endpoint_string, refresh_key="refresh_message", refresh_all=False
        )

        @client.refresh_configuration_settings
        def refresh_test_method(refresh_message):
            assert client["refresh_message"] == refresh_message
            assert client["non_refreshed_message"] == "Static"

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
        refresh_test_method("updated value")

        setting.value = "original value"
        client._client.set_configuration_setting(setting)
        static_setting.value = "Static"
        client._client.set_configuration_setting(static_setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)
        refresh_test_method("original value")

    # method: refresh decorator
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_refresh_alldecorator(self, appconfiguration_endpoint_string):
        client = self.build_provider_aad(appconfiguration_endpoint_string, refresh_key="refresh_all_message")

        @client.refresh_configuration_settings
        def refresh_test_method(refresh_message):
            assert client["refresh_all_message"] == refresh_message

        refresh_test_method("original value")
        assert client["my_json"]["key"] == "value"
        assert (
            client["FeatureManagementFeatureFlags"]["Alpha"]
            == '{"enabled": false, "conditions": {"client_filters": []}}'
        )
        setting = client._client.get_configuration_setting(key="refresh_all_message")
        setting.value = "updated value"
        client._client.set_configuration_setting(setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)
        refresh_test_method("updated value")

        setting.value = "original value"
        client._client.set_configuration_setting(setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)
        refresh_test_method("original value")

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
