# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import SettingSelector
from devtools_testutils.aio import recorded_by_proxy_async
from azure.appconfiguration.aio import AzureAppConfigurationClient
from async_preparers import app_config_decorator_async
from asynctestcase import AppConfigTestCase


class TestAppConfigurationProvider(AppConfigTestCase):
    # method: provider_creation_aad
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_creation_aad(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        async with await self.create_aad_client(
            appconfiguration_endpoint_string, keyvault_secret_url=appconfiguration_keyvault_secret_url
        ) as client:
            assert client.get("message") == "hi"
            assert client["my_json"]["key"] == "value"
            assert "FeatureManagementFeatureFlags" in client
            assert "Alpha" in client["FeatureManagementFeatureFlags"]

    # method: provider_trim_prefixes
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_trim_prefixes(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        trimmed = {"test."}
        async with await self.create_aad_client(
            appconfiguration_endpoint_string,
            trim_prefixes=trimmed,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        ) as client:
            assert client["message"] == "hi"
            assert client["my_json"]["key"] == "value"
            assert client["trimmed"] == "key"
            assert "FeatureManagementFeatureFlags" in client
            assert "Alpha" in client["FeatureManagementFeatureFlags"]

    # method: provider_selectors
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_selectors(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        selects = {SettingSelector(key_filter="message*", label_filter="dev")}
        async with await self.create_aad_client(
            appconfiguration_endpoint_string, selects=selects, keyvault_secret_url=appconfiguration_keyvault_secret_url
        ) as client:
            assert client["message"] == "test"
            assert "test.trimmed" not in client
            assert "FeatureManagementFeatureFlags" not in client
