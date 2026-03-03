# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import has_feature_flag
from asynctestcase import AppConfigTestCase, setup_configs
from test_constants import APPCONFIGURATION_CONNECTION_STRING, FEATURE_MANAGEMENT_KEY
from azure.appconfiguration.provider import SettingSelector
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.aio import AzureAppConfigurationClient

AppConfigProviderPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    appconfiguration_connection_string=APPCONFIGURATION_CONNECTION_STRING,
)


class TestAppConfigurationProviderFeatureManagement(AppConfigTestCase):
    # method: load
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_load_only_feature_flags(self, appconfiguration_connection_string):
        async with await self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=[],
            feature_flag_enabled=True,
        ) as client:
            assert len(client.keys()) == 1
            assert FEATURE_MANAGEMENT_KEY in client
            assert has_feature_flag(client, "Alpha")

    # method: load
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_select_feature_flags(self, appconfiguration_connection_string):
        client = AzureAppConfigurationClient.from_connection_string(appconfiguration_connection_string)
        await setup_configs(client, None, None)

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
