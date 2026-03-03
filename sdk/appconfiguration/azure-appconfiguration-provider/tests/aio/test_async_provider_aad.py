# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import has_feature_flag
from asynctestcase import AppConfigTestCase
from test_constants import (
    APPCONFIGURATION_ENDPOINT_STRING,
    APPCONFIGURATION_KEYVAULT_SECRET_URL,
    FEATURE_MANAGEMENT_KEY,
)
from azure.appconfiguration.provider import SettingSelector, AzureAppConfigurationKeyVaultOptions

AppConfigProviderPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    appconfiguration_endpoint_string=APPCONFIGURATION_ENDPOINT_STRING,
    appconfiguration_keyvault_secret_url=APPCONFIGURATION_KEYVAULT_SECRET_URL,
)


class TestAppConfigurationProvider(AppConfigTestCase):
    # method: provider_creation_aad
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_provider_creation_aad(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        async with await self.create_client(
            endpoint=appconfiguration_endpoint_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            feature_flag_enabled=True,
        ) as client:
            assert client.get("message") == "hi"
            assert client["my_json"]["key"] == "value"
            assert ".appconfig.featureflag/Alpha" not in client
            assert FEATURE_MANAGEMENT_KEY in client
            assert has_feature_flag(client, "Alpha")

    # method: provider_trim_prefixes
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_provider_trim_prefixes(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        trimmed = {"test."}
        async with await self.create_client(
            endpoint=appconfiguration_endpoint_string,
            trim_prefixes=trimmed,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            feature_flag_enabled=True,
        ) as client:
            assert client["message"] == "hi"
            assert client["my_json"]["key"] == "value"
            assert client["trimmed"] == "key"
            assert FEATURE_MANAGEMENT_KEY in client
            assert has_feature_flag(client, "Alpha")

    # method: provider_selectors
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_provider_selectors(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        selects = {SettingSelector(key_filter="message*", label_filter="dev")}
        async with await self.create_client(
            endpoint=appconfiguration_endpoint_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        ) as client:
            assert client["message"] == "test"
            assert "test.trimmed" not in client
            assert FEATURE_MANAGEMENT_KEY not in client

    # method: provider_selectors
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_provider_key_vault_reference(
        self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url
    ):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        async with await self.create_client(
            endpoint=appconfiguration_endpoint_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        ) as client:
            assert client["secret"] == "Very secret value"

    # method: provider_selectors
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_provider_secret_resolver(self, appconfiguration_endpoint_string):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        async with await self.create_client(
            endpoint=appconfiguration_endpoint_string, selects=selects, secret_resolver=secret_resolver
        ) as client:
            assert client["secret"] == "Resolver Value"

    # method: provider_selectors
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_provider_key_vault_reference_options(
        self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url
    ):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        key_vault_options = AzureAppConfigurationKeyVaultOptions()
        async with await self.create_client(
            endpoint=appconfiguration_endpoint_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            key_vault_options=key_vault_options,
        ) as client:
            assert client["secret"] == "Very secret value"

    # method: provider_selectors
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_provider_secret_resolver_options(self, appconfiguration_endpoint_string):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        key_vault_options = AzureAppConfigurationKeyVaultOptions(secret_resolver=secret_resolver)
        async with await self.create_client(
            endpoint=appconfiguration_endpoint_string, selects=selects, key_vault_options=key_vault_options
        ) as client:
            assert client["secret"] == "Resolver Value"

    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_provider_tag_filters(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        selects = {SettingSelector(key_filter="*", tag_filters=["a=b"])}
        async with await self.create_client(
            endpoint=appconfiguration_endpoint_string,
            selects=selects,
            feature_flag_enabled=True,
            feature_flag_selectors={SettingSelector(key_filter="*", tag_filters=["a=b"])},
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        ) as client:
            assert "tagged_config" in client
            assert FEATURE_MANAGEMENT_KEY in client
            assert has_feature_flag(client, "TaggedFeatureFlag")
            assert "message" not in client


async def secret_resolver(_):
    return "Resolver Value"
