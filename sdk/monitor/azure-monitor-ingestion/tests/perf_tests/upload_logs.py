#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
from datetime import datetime

from azure_devtools.perfstress_tests import PerfStressTest
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.monitor.ingestion.aio import LogsIngestionClient as AsyncLogsIngestionClient


class UploadLogsTest(PerfStressTest):

    def __init__(self, arguments):
        super().__init__(arguments)

        self.data_collection_rule_id = self.get_from_env("AZURE_MONITOR_DCR_ID")
        self.data_collection_endpoint = self.get_from_env("AZURE_MONITOR_DCE")
        self.stream_name = self.get_from_env("AZURE_MONITOR_STREAM_NAME")
        self.credential = DefaultAzureCredential()
        self.async_credential = AsyncDefaultAzureCredential()

        # Create clients
        self.client = LogsIngestionClient(
            endpoint=self.data_collection_endpoint,
            credential=self.credential
        )
        self.async_client = AsyncLogsIngestionClient(
            endpoint=self.data_collection_endpoint,
            credential=self.async_credential
        )

    async def close(self):
        self.client.close()
        self.credential.close()
        await self.async_client.close()
        await self.async_credential.close()
        await super().close()

    async def setup(self):
        await super().setup()
        # Create log entries to upload
        # TODO: Parameterize the size of each log entry
        self.logs = []
        for i in range(self.args.num_logs):
            self.logs.append({
                "Time": datetime.now().isoformat(),
                "Computer": f"Computer {i}",
                "AdditionalContext": "some additional context"
            })

    @staticmethod
    def add_arguments(parser):
        super(UploadLogsTest, UploadLogsTest).add_arguments(parser)
        parser.add_argument("-n", "--num-logs", nargs="?", type=int, help="Number of logs to be uploaded. Defaults to 100", default=100)

    def run_sync(self):
        self.client.upload(
            rule_id=self.data_collection_rule_id,
            stream_name=self.stream_name,
            logs=self.logs
        )

    async def run_async(self):
        await self.async_client.upload(
            rule_id=self.data_collection_rule_id,
            stream_name=self.stream_name,
            logs=self.logs
        )
