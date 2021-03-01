# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import uuid

from azure_devtools.perfstress_tests import PerfStressTest

from azure.appconfiguration import ConfigurationSetting, AzureAppConfigurationClient as SyncAppConfigClient
from azure.appconfiguration.aio import AzureAppConfigurationClient as AsyncAppConfigClient


class SetTest(PerfStressTest):
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_APP_CONFIG_CONNECTION_STRING")
        self.key = "KEY"
        self.value = str(uuid.uuid4())
        self.service_client = SyncAppConfigClient.from_connection_string(connection_string=connection_string)
        self.async_service_client = AsyncAppConfigClient.from_connection_string(connection_string=connection_string)

    async def close(self):
        # await self.async_service_client.close()
        await super().close()

    def run_sync(self):
        kv = ConfigurationSetting(
            key=self.key,
            value="VALUE" + self.value,
        )
        self.service_client.set_configuration_setting(kv)

    async def run_async(self):
        kv = ConfigurationSetting(
            key=self.key,
            value="VALUE" + self.value,
        )
        await self.async_service_client.set_configuration_setting(kv)
