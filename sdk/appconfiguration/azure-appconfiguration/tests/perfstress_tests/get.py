# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure_devtools.perfstress_tests import PerfStressTest

from azure.appconfiguration import ConfigurationSetting, AzureAppConfigurationClient as SyncAppConfigClient
from azure.appconfiguration.aio import AzureAppConfigurationClient as AsyncAppConfigClient


class GetTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_APP_CONFIG_CONNECTION_STRING")
        self.key = "KEY"
        self.service_client = SyncAppConfigClient.from_connection_string(connection_string=connection_string)
        self.async_service_client = AsyncAppConfigClient.from_connection_string(connection_string=connection_string)

    async def global_setup(self):
        await super().global_setup()
        kv = ConfigurationSetting(
            key=self.key,
            value="VALUE",
        )
        await self.async_service_client.set_configuration_setting(kv)

    async def close(self):
        # await self.async_service_client.close()
        await super().close()

    def run_sync(self):
        self.service_client.get_configuration_setting(key=self.key)

    async def run_async(self):
        await self.async_service_client.get_configuration_setting(key=self.key)
