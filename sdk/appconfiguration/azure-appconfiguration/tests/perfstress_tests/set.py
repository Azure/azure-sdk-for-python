# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from devtools_testutils.perfstress_tests import PerfStressTest

from azure.appconfiguration import ConfigurationSetting, AzureAppConfigurationClient as SyncAppConfigClient
from azure.appconfiguration.aio import AzureAppConfigurationClient as AsyncAppConfigClient
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential


class SetTest(PerfStressTest):
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)
        endpoint = self.get_from_env("AZURE_APP_CONFIG_ENDPOINT")
        self.key = "KEY"
        self.value = str(uuid.uuid4())
        self.service_client = SyncAppConfigClient(endpoint, DefaultAzureCredential())
        self.async_service_client = AsyncAppConfigClient(endpoint, AsyncDefaultAzureCredential())

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
