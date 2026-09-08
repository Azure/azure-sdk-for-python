# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import unittest
from unittest.mock import Mock
from devtools_testutils import EnvironmentVariableLoader, recorded_by_proxy
from testcase import AppConfigTestCase, ConfigurationSetting, has_feature_flag
from test_constants import (
    APPCONFIGURATION_ENDPOINT_STRING,
    APPCONFIGURATION_KEYVAULT_SECRET_URL,
    FEATURE_MANAGEMENT_KEY,
)
from azure.appconfiguration import FeatureFlagConfigurationSetting
from azure.appconfiguration.provider import SettingSelector, WatchKey

AppConfigProviderPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    appconfiguration_endpoint_string=APPCONFIGURATION_ENDPOINT_STRING,
    appconfiguration_keyvault_secret_url=APPCONFIGURATION_KEYVAULT_SECRET_URL,
)


class TestAppConfigurationProvider(AppConfigTestCase, unittest.TestCase):
    # method: refresh
    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        mock_callback = Mock()
        appconfig_client = self.create_appconfig_client(appconfiguration_endpoint_string)
        test_prefix = self.get_resource_name("test")
        refresh_key = f"{test_prefix}-refresh-message"
        feature_id = f"{test_prefix}-alpha"
        setting = ConfigurationSetting(key=refresh_key, value="original value")
        feature_flag = FeatureFlagConfigurationSetting(feature_id=feature_id, enabled=False)
        appconfig_client.set_configuration_setting(setting)
        appconfig_client.set_configuration_setting(feature_flag)

        try:
            client = self.create_client(
                endpoint=appconfiguration_endpoint_string,
                keyvault_secret_url=appconfiguration_keyvault_secret_url,
                selects=[SettingSelector(key_filter=refresh_key)],
                refresh_on=[WatchKey(refresh_key)],
                refresh_interval=1,
                on_refresh_success=mock_callback,
                feature_flag_enabled=True,
                feature_flag_refresh_enabled=True,
                feature_flag_selectors=[SettingSelector(key_filter=feature_id)],
            )
            assert client[refresh_key] == "original value"
            assert FEATURE_MANAGEMENT_KEY in client
            assert has_feature_flag(client, feature_id)

            setting.value = "updated value"
            feature_flag.enabled = True
            appconfig_client.set_configuration_setting(setting)
            appconfig_client.set_configuration_setting(feature_flag)

            client._refresh_timer._next_refresh_time = 0
            client._feature_flag_refresh_timer._next_refresh_time = 0
            client.refresh()
            assert client[refresh_key] == "updated value"
            assert has_feature_flag(client, feature_id, True)
            assert mock_callback.call_count == 1

            setting.value = "original value"
            feature_flag.enabled = False
            appconfig_client.set_configuration_setting(setting)
            appconfig_client.set_configuration_setting(feature_flag)

            client._refresh_timer._next_refresh_time = 0
            client._feature_flag_refresh_timer._next_refresh_time = 0
            client.refresh()
            assert client[refresh_key] == "original value"
            assert has_feature_flag(client, feature_id, False)
            assert mock_callback.call_count == 2

            setting.value = "updated value 2"
            feature_flag.enabled = True
            appconfig_client.set_configuration_setting(setting)
            appconfig_client.set_configuration_setting(feature_flag)

            client.refresh()
            assert client[refresh_key] == "original value"
            assert has_feature_flag(client, feature_id, False)
            assert mock_callback.call_count == 2
        finally:
            appconfig_client.delete_configuration_setting(key=refresh_key)
            appconfig_client.delete_configuration_setting(key=feature_flag.key)

    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_no_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        appconfig_client = self.create_appconfig_client(appconfiguration_endpoint_string)
        test_prefix = self.get_resource_name("test")
        refresh_key = f"{test_prefix}-refresh-message"
        watch_key_name = f"{test_prefix}-watch-key"
        setting = ConfigurationSetting(key=refresh_key, value="original value")
        watch_key = ConfigurationSetting(key=watch_key_name, value="0")
        appconfig_client.set_configuration_setting(setting)
        appconfig_client.set_configuration_setting(watch_key)

        mock_callback = Mock()
        try:
            client = self.create_client(
                endpoint=appconfiguration_endpoint_string,
                keyvault_secret_url=appconfiguration_keyvault_secret_url,
                selects=[SettingSelector(key_filter=refresh_key)],
                refresh_on=[WatchKey(watch_key_name)],
                refresh_interval=1,
                on_refresh_success=mock_callback,
            )
            assert client[refresh_key] == "original value"

            setting.value = "updated value"
            appconfig_client.set_configuration_setting(setting)
            client._refresh_timer._next_refresh_time = 0
            client.refresh()
            assert client[refresh_key] == "original value"
            assert mock_callback.call_count == 0

            watch_key.value = "1"
            appconfig_client.set_configuration_setting(watch_key)
            client._refresh_timer._next_refresh_time = 0
            client.refresh()
            assert client[refresh_key] == "updated value"
            assert mock_callback.call_count == 1
        finally:
            appconfig_client.delete_configuration_setting(key=refresh_key)
            appconfig_client.delete_configuration_setting(key=watch_key_name)

    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_empty_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        mock_callback = Mock()
        appconfig_client = self.create_appconfig_client(appconfiguration_endpoint_string)
        refresh_key = f"{self.get_resource_name('test')}-refresh-message"
        setting = ConfigurationSetting(key=refresh_key, value="original value")
        appconfig_client.set_configuration_setting(setting)

        try:
            client = self.create_client(
                endpoint=appconfiguration_endpoint_string,
                keyvault_secret_url=appconfiguration_keyvault_secret_url,
                selects=[SettingSelector(key_filter=refresh_key)],
                refresh_on=[WatchKey(refresh_key)],
                refresh_interval=1,
                on_refresh_success=mock_callback,
                refresh_enabled=False,
            )
            assert client[refresh_key] == "original value"

            setting.value = "updated value"
            appconfig_client.set_configuration_setting(setting)
            client._refresh_timer._next_refresh_time = 0
            client.refresh()
            assert client[refresh_key] == "original value"
            assert mock_callback.call_count == 0
        finally:
            appconfig_client.delete_configuration_setting(key=refresh_key)
