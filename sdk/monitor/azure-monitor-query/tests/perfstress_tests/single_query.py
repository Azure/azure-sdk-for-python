#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
from datetime import date, datetime, timezone
from azure_devtools.perfstress_tests import PerfStressTest

from azure.monitor.query import LogsQueryClient as SyncLogsQueryClient
from azure.monitor.query.aio import LogsQueryClient as AsyncLogsQueryClient

from azure.identity import DefaultAzureCredential as SyncDefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

class LogsPerfTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # auth configuration
        self.workspace_id = self.get_from_env('LOG_WORKSPACE_ID')

        self.query = "AppRequests | summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"

        # Create clients
        self.logs_client = SyncLogsQueryClient(
            credential=SyncDefaultAzureCredential()
        )
        self.async_logs_client = AsyncLogsQueryClient(
            credential=AsyncDefaultAzureCredential()
        )

    async def close(self):
        """This is run after cleanup.
        
        Use this to close any open handles or clients.
        """
        await self.async_logs_client.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test.
        
        Try to keep this minimal and focused. Using only a single client API.
        Avoid putting any ancillary logic (e.g. generating UUIDs), and put this in the setup/init instead
        so that we're only measuring the client API call.
        """
        start_time=datetime(2021, 7, 25, 0, 0, 0, tzinfo=timezone.utc)
        end_time=datetime(2021, 7, 26, 0, 0, 0, tzinfo=timezone.utc)
        self.logs_client.query_workspace(
            self.workspace_id,
            self.query,
            timespan=(start_time, end_time)
            )

    async def run_async(self):
        """The asynchronous perf test.
        
        Try to keep this minimal and focused. Using only a single client API.
        Avoid putting any ancillary logic (e.g. generating UUIDs), and put this in the setup/init instead
        so that we're only measuring the client API call.
        """
        start_time=datetime(2021, 7, 25, 0, 0, 0, tzinfo=timezone.utc)
        end_time=datetime(2021, 7, 26, 0, 0, 0, tzinfo=timezone.utc)
        await self.async_logs_client.query_workspace(
            self.workspace_id,
            self.query,
            timespan=(start_time, end_time)
            )
