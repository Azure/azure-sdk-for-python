# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.provider.aio import load_provider
from azure.appconfiguration.provider import SettingSelector
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from azure.appconfiguration import AzureAppConfigurationClient
from async_preparers import app_config_decorator_async

class TestAppConfigurationProvider(AzureRecordedTestCase):

    async def build_provider(self, connection_string, trimmed_key_prefixes=[], selects={SettingSelector("*", "\0")}):
        return await load_provider(connection_string=connection_string, trimmed_key_prefixes=trimmed_key_prefixes, selects=selects)

    # method: provider_creation
    @recorded_by_proxy_async
    @app_config_decorator_async
    def test_provider_creation(self, appconfiguration_connection_string):
        client = self.build_provider(appconfiguration_connection_string)
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"

    # method: provider_trimmed_key_prefixes
    @recorded_by_proxy_async
    @app_config_decorator_async
    def test_provider_trimmed_key_prefixes(self, appconfiguration_connection_string):
        trimmed = {"test."}
        client = self.build_provider(appconfiguration_connection_string, trimmed_key_prefixes=trimmed)
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"
        assert client["trimmed"] == "key"
        assert "test.trimmed" not in client

    # method: provider_selectors
    @recorded_by_proxy_async
    @app_config_decorator_async
    def test_provider_selectors(self, appconfiguration_connection_string):
        selects = {SettingSelector("message*", "dev")}
        client = self.build_provider(appconfiguration_connection_string, selects=selects)
        assert client["message"] == "test"
        assert "test.trimmed" not in client
