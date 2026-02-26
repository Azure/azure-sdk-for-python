# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import unittest
import sys
from unittest.mock import Mock
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from async_preparers import app_config_decorator_async
from testcase import has_feature_flag
from asynctestcase import AppConfigTestCase
from test_constants import FEATURE_MANAGEMENT_KEY

try:
    from unittest.mock import AsyncMock

    class TestAppConfigurationProviderWatchAll(AppConfigTestCase, unittest.TestCase):
        # method: refresh (watch all - no refresh_on keys, refresh_enabled=True)
        @app_config_decorator_async
        @recorded_by_proxy_async
        @pytest.mark.skipif(sys.version_info < (3, 8), reason="Python 3.7 does not support AsyncMock")
        @pytest.mark.asyncio
        async def test_watch_all(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
            mock_callback = Mock()
            async with await self.create_client(
                endpoint=appconfiguration_endpoint_string,
                keyvault_secret_url=appconfiguration_keyvault_secret_url,
                refresh_interval=1,
                on_refresh_success=mock_callback,
                feature_flag_enabled=True,
            ) as client:
                assert client["refresh_message"] == "original value"
                assert client["non_refreshed_message"] == "Static"
                assert client["my_json"]["key"] == "value"
                assert FEATURE_MANAGEMENT_KEY in client
                assert has_feature_flag(client, "Alpha")

                appconfig_client = self.create_aad_sdk_client(appconfiguration_endpoint_string)

                setting = await appconfig_client.get_configuration_setting(key="refresh_message")
                setting.value = "updated value"
                await appconfig_client.set_configuration_setting(setting)

                # Waiting for the refresh interval to pass
                time.sleep(2)

                await client.refresh()
                # Watch all should detect the change and refresh all settings
                assert client["refresh_message"] == "updated value"
                assert mock_callback.call_count == 1

                setting.value = "original value"
                await appconfig_client.set_configuration_setting(setting)

                # Waiting for the refresh interval to pass
                time.sleep(2)

                await client.refresh()
                assert client["refresh_message"] == "original value"
                assert mock_callback.call_count == 2

        # method: refresh (watch all - no changes should not trigger refresh)
        @app_config_decorator_async
        @recorded_by_proxy_async
        @pytest.mark.skipif(sys.version_info < (3, 8), reason="Python 3.7 does not support AsyncMock")
        @pytest.mark.asyncio
        async def test_watch_all_no_change(
            self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url
        ):
            mock_callback = Mock()
            async with await self.create_client(
                endpoint=appconfiguration_endpoint_string,
                keyvault_secret_url=appconfiguration_keyvault_secret_url,
                refresh_interval=1,
                on_refresh_success=mock_callback,
                feature_flag_enabled=True,
            ) as client:
                assert client["refresh_message"] == "original value"
                assert client["non_refreshed_message"] == "Static"

                # Waiting for the refresh interval to pass
                time.sleep(2)

                # No settings changed, refresh should be a no-op
                await client.refresh()
                assert client["refresh_message"] == "original value"
                assert client["non_refreshed_message"] == "Static"
                assert mock_callback.call_count == 0

        # method: refresh (watch all - should not trigger before refresh interval)
        @app_config_decorator_async
        @recorded_by_proxy_async
        @pytest.mark.skipif(sys.version_info < (3, 8), reason="Python 3.7 does not support AsyncMock")
        @pytest.mark.asyncio
        async def test_watch_all_before_interval(
            self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url
        ):
            mock_callback = Mock()
            async with await self.create_client(
                endpoint=appconfiguration_endpoint_string,
                keyvault_secret_url=appconfiguration_keyvault_secret_url,
                refresh_interval=10,
                on_refresh_success=mock_callback,
                feature_flag_enabled=True,
            ) as client:
                assert client["refresh_message"] == "original value"

                appconfig_client = self.create_aad_sdk_client(appconfiguration_endpoint_string)

                setting = await appconfig_client.get_configuration_setting(key="refresh_message")
                setting.value = "updated value"
                await appconfig_client.set_configuration_setting(setting)

                # Not waiting for the refresh interval to pass
                await client.refresh()
                # Should not refresh because the interval hasn't passed
                assert client["refresh_message"] == "original value"
                assert mock_callback.call_count == 0

                setting.value = "original value"
                await appconfig_client.set_configuration_setting(setting)

        # method: refresh (watch all disabled via refresh_enabled=False)
        @app_config_decorator_async
        @recorded_by_proxy_async
        @pytest.mark.skipif(sys.version_info < (3, 8), reason="Python 3.7 does not support AsyncMock")
        @pytest.mark.asyncio
        async def test_watch_all_disabled(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
            mock_callback = Mock()
            async with await self.create_client(
                endpoint=appconfiguration_endpoint_string,
                keyvault_secret_url=appconfiguration_keyvault_secret_url,
                refresh_interval=1,
                on_refresh_success=mock_callback,
                feature_flag_enabled=True,
                refresh_enabled=False,
            ) as client:
                assert client["refresh_message"] == "original value"

                appconfig_client = self.create_aad_sdk_client(appconfiguration_endpoint_string)

                setting = await appconfig_client.get_configuration_setting(key="refresh_message")
                setting.value = "updated value"
                await appconfig_client.set_configuration_setting(setting)

                # Waiting for the refresh interval to pass
                time.sleep(2)

                await client.refresh()
                # Refresh is disabled, watch all should not activate
                assert client["refresh_message"] == "original value"
                assert mock_callback.call_count == 0

                setting.value = "original value"
                await appconfig_client.set_configuration_setting(setting)

        # method: refresh (watch all refreshes all settings including non-watched ones)
        @app_config_decorator_async
        @recorded_by_proxy_async
        @pytest.mark.skipif(sys.version_info < (3, 8), reason="Python 3.7 does not support AsyncMock")
        @pytest.mark.asyncio
        async def test_watch_all_refreshes_all_settings(
            self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url
        ):
            mock_callback = Mock()
            async with await self.create_client(
                endpoint=appconfiguration_endpoint_string,
                keyvault_secret_url=appconfiguration_keyvault_secret_url,
                refresh_interval=1,
                on_refresh_success=mock_callback,
                feature_flag_enabled=True,
            ) as client:
                assert client["refresh_message"] == "original value"
                assert client["non_refreshed_message"] == "Static"

                appconfig_client = self.create_aad_sdk_client(appconfiguration_endpoint_string)

                # Change multiple settings at once
                setting = await appconfig_client.get_configuration_setting(key="refresh_message")
                setting.value = "updated value"
                await appconfig_client.set_configuration_setting(setting)

                static_setting = await appconfig_client.get_configuration_setting(key="non_refreshed_message")
                static_setting.value = "updated static"
                await appconfig_client.set_configuration_setting(static_setting)

                # Waiting for the refresh interval to pass
                time.sleep(2)

                await client.refresh()
                # Watch all should detect changes and refresh everything
                assert client["refresh_message"] == "updated value"
                assert client["non_refreshed_message"] == "updated static"
                assert mock_callback.call_count == 1

                # Restore original values
                setting.value = "original value"
                await appconfig_client.set_configuration_setting(setting)
                static_setting.value = "Static"
                await appconfig_client.set_configuration_setting(static_setting)

                # Waiting for the refresh interval to pass
                time.sleep(2)

                await client.refresh()
                assert client["refresh_message"] == "original value"
                assert client["non_refreshed_message"] == "Static"
                assert mock_callback.call_count == 2

        # method: refresh (empty refresh - no refresh_on and no refresh_interval should not trigger)
        @app_config_decorator_async
        @recorded_by_proxy_async
        @pytest.mark.skipif(sys.version_info < (3, 8), reason="Python 3.7 does not support AsyncMock")
        @pytest.mark.asyncio
        async def test_empty_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
            mock_callback = AsyncMock()
            async with await self.create_client(
                endpoint=appconfiguration_endpoint_string,
                keyvault_secret_url=appconfiguration_keyvault_secret_url,
                on_refresh_success=mock_callback,
                feature_flag_enabled=True,
            ) as client:
                assert client["refresh_message"] == "original value"
                assert client["non_refreshed_message"] == "Static"
                assert client["my_json"]["key"] == "value"
                assert FEATURE_MANAGEMENT_KEY in client
                assert has_feature_flag(client, "Alpha")

                appconfig_client = self.create_aad_sdk_client(appconfiguration_endpoint_string)

                setting = await appconfig_client.get_configuration_setting(key="refresh_message")
                setting.value = "updated value"
                await appconfig_client.set_configuration_setting(setting)
                static_setting = await appconfig_client.get_configuration_setting(key="non_refreshed_message")
                static_setting.value = "updated static"
                await appconfig_client.set_configuration_setting(static_setting)

                # Waiting for the refresh interval to pass
                time.sleep(2)

                await client.refresh()
                assert client["refresh_message"] == "original value"
                assert client["non_refreshed_message"] == "Static"
                assert mock_callback.call_count == 0

                setting.value = "original value"
                await appconfig_client.set_configuration_setting(setting)
                static_setting.value = "Static"
                await appconfig_client.set_configuration_setting(static_setting)

except ImportError:
    pass
