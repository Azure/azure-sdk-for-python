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
    ):
        cred = self.get_credential(AzureAppConfigurationClient, is_async=True)
        client = AzureAppConfigurationClient(appconfiguration_endpoint_string, cred)
        await setup_configs(client)
        return await load(
            credential=cred, endpoint=appconfiguration_endpoint_string, trim_prefixes=trim_prefixes, selects=selects
        )

    async def create_client(
        self,
        appconfiguration_connection_string,
        trim_prefixes=[],
        selects={SettingSelector(key_filter="*", label_filter="\0")},
    ):
        client = AzureAppConfigurationClient.from_connection_string(appconfiguration_connection_string)
        await setup_configs(client)
        return await load(
            connection_string=appconfiguration_connection_string, trim_prefixes=trim_prefixes, selects=selects
        )


async def setup_configs(client):
    async with client:
        for config in get_configs():
            await client.set_configuration_setting(config)
