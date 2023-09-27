# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import unittest
from azure.appconfiguration.provider import SettingSelector, SentinelKey
from azure.appconfiguration.provider.aio import load
from devtools_testutils.aio import recorded_by_proxy_async
from azure.appconfiguration.aio import AzureAppConfigurationClient
from async_preparers import app_config_decorator_async
from asynctestcase import AppConfigTestCase


class TestAppConfigurationProvider(AppConfigTestCase, unittest.TestCase):
    # method: refresh
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        async with await self.create_aad_client(
            appconfiguration_endpoint_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            refresh_on=[SentinelKey("refresh_message")],
            refresh_interval=1,
        ) as client:
            assert client["refresh_message"] == "original value"
            assert client["my_json"]["key"] == "value"
            assert "FeatureManagementFeatureFlags" in client
            assert "Alpha" in client["FeatureManagementFeatureFlags"]
            setting = await client._client.get_configuration_setting(key="refresh_message")
            setting.value = "updated value"
            await client._client.set_configuration_setting(setting)

            # Waiting for the refresh interval to pass
            time.sleep(2)

            await client.refresh()
            assert client["refresh_message"] == "updated value"

            setting.value = "original value"
            await client._client.set_configuration_setting(setting)

            # Waiting for the refresh interval to pass
            time.sleep(2)

            await client.refresh()
            assert client["refresh_message"] == "original value"

            setting.value = "updated value 2"
            await client._client.set_configuration_setting(setting)

            # Not waiting for the refresh interval to pass
            await client.refresh()
            assert client["refresh_message"] == "original value"

            setting.value = "original value"
            await client._client.set_configuration_setting(setting)

            await client.refresh()
            assert client["refresh_message"] == "original value"

    # method: refresh
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_empty_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        async with await self.create_aad_client(
            appconfiguration_endpoint_string, keyvault_secret_url=appconfiguration_keyvault_secret_url
        ) as client:
            assert client["refresh_message"] == "original value"
            assert client["non_refreshed_message"] == "Static"
            assert client["my_json"]["key"] == "value"
            assert "FeatureManagementFeatureFlags" in client
            assert "Alpha" in client["FeatureManagementFeatureFlags"]
            setting = await client._client.get_configuration_setting(key="refresh_message")
            setting.value = "updated value"
            await client._client.set_configuration_setting(setting)
            static_setting = await client._client.get_configuration_setting(key="non_refreshed_message")
            static_setting.value = "updated static"
            await client._client.set_configuration_setting(static_setting)

            # Waiting for the refresh interval to pass
            time.sleep(2)

            await client.refresh()
            assert client["refresh_message"] == "original value"
            assert client["non_refreshed_message"] == "Static"

            setting.value = "original value"
            await client._client.set_configuration_setting(setting)
            static_setting.value = "Static"
            await client._client.set_configuration_setting(static_setting)

    def my_callback(self):
        assert True

    def my_callback_on_fail(self):
        assert False
