# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List
from testcase import AppConfigTestCase
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.core.async_paging import AsyncItemPaged


# pylint: disable=invalid-overridden-method
class AsyncAppConfigTestCase(AppConfigTestCase):
    def create_client(self, appconfiguration_endpoint_string, audience=None):
        cred = self.get_credential(AzureAppConfigurationClient, is_async=True)
        return AzureAppConfigurationClient(appconfiguration_endpoint_string, cred, audience=audience)

    async def convert_to_list(self, items: AsyncItemPaged) -> List:
        list = []
        async for item in items:
            list.append(item)
        return list

    async def set_up(self, appconfiguration_string):
        self.client = self.create_client(appconfiguration_string)
        await self.client.set_configuration_setting(self.create_config_setting())
        await self.client.set_configuration_setting(self.create_config_setting_no_label())

    async def tear_down(self):
        if self.client is not None:
            # Archive all ready snapshots
            snapshots = self.client.list_snapshots(status=["ready"])
            async for snapshot in snapshots:
                try:
                    await self.client.archive_snapshot(name=snapshot.name)
                except Exception:  # pylint:disable=broad-except
                    pass

            # Delete all configuration settings
            config_settings = self.client.list_configuration_settings()
            async for config_setting in config_settings:
                await self.client.delete_configuration_setting(key=config_setting.key, label=config_setting.label)
            await self.client.close()
        else:
            raise ValueError("Client is None!")
