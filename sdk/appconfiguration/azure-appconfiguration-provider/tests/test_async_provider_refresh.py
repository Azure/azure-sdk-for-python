# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import unittest
import pytest
import sys

from azure.appconfiguration.provider import WatchKey
from devtools_testutils.aio import recorded_by_proxy_async
from async_preparers import app_config_decorator_async
from asynctestcase import AppConfigTestCase, has_feature_flag
from test_constants import FEATURE_MANAGEMENT_KEY

try:
    # Python 3.7 does not support AsyncMock
    from unittest.mock import AsyncMock

    class TestAppConfigurationProvider(AppConfigTestCase, unittest.TestCase):
        # method: refresh
        @app_config_decorator_async
        @recorded_by_proxy_async
        @pytest.mark.skipif(sys.version_info < (3, 8), reason="Python 3.7 does not support AsyncMock")
        @pytest.mark.asyncio
        async def test_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
            mock_callback = AsyncMock()
            async with await self.create_aad_client(
                appconfiguration_endpoint_string,
                keyvault_secret_url=appconfiguration_keyvault_secret_url,
                refresh_on=[WatchKey("refresh_message")],
                refresh_interval=1,
                on_refresh_success=mock_callback,
                feature_flag_enabled=True,
                feature_flag_refresh_enabled=True,
            ) as client:
                assert client["refresh_message"] == "original value"
                assert client["my_json"]["key"] == "value"
                assert FEATURE_MANAGEMENT_KEY in client
                assert has_feature_flag(client, "Alpha")
                setting = await client._client.get_configuration_setting(key="refresh_message")
                setting.value = "updated value"
                feature_flag = await client._client.get_configuration_setting(key=".appconfig.featureflag/Alpha")
                feature_flag.enabled = True
                await client._client.set_configuration_setting(setting)
                await client._client.set_configuration_setting(feature_flag)

                # Waiting for the refresh interval to pass
                time.sleep(2)

                await client.refresh()
                assert client["refresh_message"] == "updated value"
                assert has_feature_flag(client, "Alpha", True)
                assert mock_callback.call_count == 1

                setting.value = "original value"
                feature_flag.enabled = False
                await client._client.set_configuration_setting(setting)
                await client._client.set_configuration_setting(feature_flag)

                # Waiting for the refresh interval to pass
                time.sleep(2)

                await client.refresh()
                assert client["refresh_message"] == "original value"
                assert has_feature_flag(client, "Alpha", False)
                assert mock_callback.call_count == 2

                setting.value = "updated value 2"
                feature_flag.enabled = True
                await client._client.set_configuration_setting(setting)
                await client._client.set_configuration_setting(feature_flag)

                # Not waiting for the refresh interval to pass
                await client.refresh()
                assert client["refresh_message"] == "original value"
                assert has_feature_flag(client, "Alpha", False)
                assert mock_callback.call_count == 2

                setting.value = "original value"
                await client._client.set_configuration_setting(setting)

                await client.refresh()
                assert client["refresh_message"] == "original value"
                assert mock_callback.call_count == 2

        # method: refresh
        @app_config_decorator_async
        @recorded_by_proxy_async
        @pytest.mark.skipif(sys.version_info < (3, 8), reason="Python 3.7 does not support AsyncMock")
        @pytest.mark.asyncio
        async def test_empty_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
            mock_callback = AsyncMock()
            async with await self.create_aad_client(
                appconfiguration_endpoint_string,
                keyvault_secret_url=appconfiguration_keyvault_secret_url,
                on_refresh_success=mock_callback,
                feature_flag_enabled=True,
            ) as client:
                assert client["refresh_message"] == "original value"
                assert client["non_refreshed_message"] == "Static"
                assert client["my_json"]["key"] == "value"
                assert FEATURE_MANAGEMENT_KEY in client
                assert has_feature_flag(client, "Alpha")
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
                assert mock_callback.call_count == 0

                setting.value = "original value"
                await client._client.set_configuration_setting(setting)
                static_setting.value = "Static"
                await client._client.set_configuration_setting(static_setting)

except ImportError:
    pass
