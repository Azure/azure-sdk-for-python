# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.provider import SettingSelector
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.aio import AzureAppConfigurationClient
from devtools_testutils.aio import recorded_by_proxy_async
from async_preparers import app_config_decorator_async
from asynctestcase import AppConfigTestCase, setup_configs, has_feature_flag
from test_constants import FEATURE_MANAGEMENT_KEY


class TestAppConfigurationProviderFeatureManagement(AppConfigTestCase):
    # method: load
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_load_only_feature_flags(self, appconfiguration_connection_string):
        async with await self.create_client(
            appconfiguration_connection_string,
            selects=[],
            feature_flag_enabled=True,
        ) as client:
            assert len(client.keys()) == 1
            assert FEATURE_MANAGEMENT_KEY in client
            assert has_feature_flag(client, "Alpha")

    # method: load
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_select_feature_flags(self, appconfiguration_connection_string):
        client = AzureAppConfigurationClient.from_connection_string(appconfiguration_connection_string)
        await setup_configs(client, None)

        async with await load(
            connection_string=appconfiguration_connection_string,
            selects=[],
            feature_flag_enabled=True,
            feature_flag_selectors=[SettingSelector(key_filter="B*")],
            user_agent="SDK/Integration",
        ) as client:
            assert len(client.keys()) == 1
            assert FEATURE_MANAGEMENT_KEY in client
            assert not has_feature_flag(client, "Alpha")
