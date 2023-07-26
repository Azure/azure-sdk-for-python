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
from testcase import create_config_setting
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
        await client.set_configuration_setting(create_config_setting("message", "\0", "hi"))
        await client.set_configuration_setting(create_config_setting("message", "dev", "test"))
        await client.set_configuration_setting(
            create_config_setting("my_json", "\0", '{"key": "value"}', "application/json")
        )
        await client.set_configuration_setting(create_config_setting("test.trimmed", "\0", "key"))
        await client.set_configuration_setting(
            create_config_setting(
                ".appconfig.featureflag/Alpha",
                "\0",
                '{	"id": "Alpha", "description": "", "enabled": false, "conditions": {	"client_filters": []	}}',
                "application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
            )
        )
