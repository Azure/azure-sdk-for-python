# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import ResourceExistsError
from testcase import AppConfigTestCase
from typing import List


class AsyncAppConfigTestCase(AppConfigTestCase):
    def create_aad_client(self, appconfiguration_endpoint_string):
        cred = self.get_credential(AzureAppConfigurationClient, is_async=True)
        return AzureAppConfigurationClient(appconfiguration_endpoint_string, cred)

    def create_client(self, appconfiguration_connection_string):
        return AzureAppConfigurationClient.from_connection_string(appconfiguration_connection_string)

    async def add_for_test(self, client, config_setting):
        try:
            await client.add_configuration_setting(config_setting)
        except ResourceExistsError:
            pass

    async def convert_to_list(self, config_settings: AsyncItemPaged) -> List:
        list = []
        async for item in config_settings:
            list.append(item)
        return list

    async def set_up(self, appconfiguration_string, is_aad=False):
        if is_aad:
            self.client = self.create_aad_client(appconfiguration_string)
        else:
            self.client = self.create_client(appconfiguration_string)
        await self.add_for_test(self.client, self.create_config_setting())
        await self.add_for_test(self.client, self.create_config_setting_no_label())

    async def tear_down(self):
        if self.client is not None:
            config_settings = self.client.list_configuration_settings()
            async for config_setting in config_settings:
                await self.client.delete_configuration_setting(key=config_setting.key, label=config_setting.label)
            await self.client.close()
        else:
            raise ValueError("Client is None!")
