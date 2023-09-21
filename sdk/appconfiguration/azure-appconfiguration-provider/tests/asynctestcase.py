# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
from devtools_testutils import AzureRecordedTestCase
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.appconfiguration import ConfigurationSetting, FeatureFlagConfigurationSetting
from testcase import get_configs
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import SettingSelector


class AppConfigTestCase(AzureRecordedTestCase):
    import asyncio

    async def create_aad_client(
        self,
        appconfiguration_endpoint_string,
        trim_prefixes=[],
        selects={SettingSelector(key_filter="*", label_filter="\0")},
        keyvault_secret_url=None,
        refresh_on=None,
        refresh_interval=30,
        secret_resolver=None,
    ):
        cred = self.get_credential(AzureAppConfigurationClient, is_async=True)
        keyvault_cred = cred if keyvault_secret_url else None

        client = AzureAppConfigurationClient(appconfiguration_endpoint_string, cred)
        await setup_configs(client, keyvault_secret_url)
        return await load(
            credential=cred,
            endpoint=appconfiguration_endpoint_string,
            trim_prefixes=trim_prefixes,
            selects=selects,
            refresh_on=refresh_on,
            refresh_interval=refresh_interval,
            user_agent="SDK/Integration",
            key_vault_credentials=keyvault_cred,
            secret_resolver=secret_resolver,
        )

    async def create_client(
        self,
        appconfiguration_connection_string,
        trim_prefixes=[],
        selects={SettingSelector(key_filter="*", label_filter="\0")},
        keyvault_secret_url=None,
        refresh_on=None,
        refresh_interval=30,
        secret_resolver=None,
    ):
        client = AzureAppConfigurationClient.from_connection_string(appconfiguration_connection_string)
        await setup_configs(client, keyvault_secret_url)

        keyvault_cred = self.get_credential(AzureAppConfigurationClient, is_async=True) if keyvault_secret_url else None

        return await load(
            connection_string=appconfiguration_connection_string,
            trim_prefixes=trim_prefixes,
            selects=selects,
            refresh_on=refresh_on,
            refresh_interval=refresh_interval,
            user_agent="SDK/Integration",
            key_vault_credentials=keyvault_cred,
            secret_resolver=secret_resolver,
        )


async def setup_configs(client, keyvault_secret_url):
    async with client:
        for config in get_configs(keyvault_secret_url):
            await client.set_configuration_setting(config)
