# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.provider.aio import load_provider
from azure.appconfiguration.provider import SettingSelector
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from async_preparers import app_config_decorator_async

class TestAppConfigurationProvider(AzureRecordedTestCase):

    async def build_provider(self, connection_string, trim_prefixes=[], selects={SettingSelector(key_filter="*", label_filter="\0")}):
        return await load_provider(connection_string=connection_string, trim_prefixes=trim_prefixes, selects=selects)

    # method: provider_creation
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_creation(self, appconfiguration_connection_string):
        async with await self.build_provider(appconfiguration_connection_string) as client:
            assert client["message"] == "hi"
            assert client["my_json"]["key"] == "value"
            assert client["FeatureManagementFeatureFlags"]["Alpha"] == '{\"enabled\": false, \"conditions\": {\"client_filters\": []}}'

    # method: provider_trim_prefixes
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_trim_prefixes(self, appconfiguration_connection_string):
        trimmed = {"test."}
        async with await self.build_provider(appconfiguration_connection_string, trim_prefixes=trimmed) as client:
            assert client["message"] == "hi"
            assert client["my_json"]["key"] == "value"
            assert client["trimmed"] == "key"
            assert "test.trimmed" not in client
            assert client["FeatureManagementFeatureFlags"]["Alpha"] == '{\"enabled\": false, \"conditions\": {\"client_filters\": []}}'

    # method: provider_selectors
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_selectors(self, appconfiguration_connection_string):
        selects = {SettingSelector(key_filter="message*",label_filter="dev")}
        async with await self.build_provider(appconfiguration_connection_string, selects=selects) as client:
            assert client["message"] == "test"
            assert "test.trimmed" not in client
            assert "FeatureManagementFeatureFlags" not in client
