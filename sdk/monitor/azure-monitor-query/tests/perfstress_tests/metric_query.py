#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
from datetime import datetime, timezone
from azure_devtools.perfstress_tests import PerfStressTest

from azure.monitor.query import MetricsQueryClient as SyncMetricsQueryClient, MetricAggregationType
from azure.monitor.query.aio import MetricsQueryClient as AsyncMetricsQueryClient

from azure.identity import DefaultAzureCredential as SyncDefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

class MetricsPerfTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # auth configuration
        self.metrics_uri = self.get_from_env('METRICS_RESOURCE_URI')
        self.names =  ["MatchedEventCount"]
        self.aggregations = [MetricAggregationType.COUNT]

        # Create clients
        self.metrics_client = SyncMetricsQueryClient(
            credential=SyncDefaultAzureCredential()
        )
        self.async_metrics_client = AsyncMetricsQueryClient(
            credential=AsyncDefaultAzureCredential()
        )

    async def close(self):
        """This is run after cleanup.
        
        Use this to close any open handles or clients.
        """
        await self.async_metrics_client.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test.
        
        Try to keep this minimal and focused. Using only a single client API.
        Avoid putting any ancillary logic (e.g. generating UUIDs), and put this in the setup/init instead
        so that we're only measuring the client API call.
        """
        self.metrics_client.query_resource(
            self.metrics_uri,
            self.names,
            aggregations=self.aggregations
            )

    async def run_async(self):
        """The asynchronous perf test.
        
        Try to keep this minimal and focused. Using only a single client API.
        Avoid putting any ancillary logic (e.g. generating UUIDs), and put this in the setup/init instead
        so that we're only measuring the client API call.
        """
        await self.async_metrics_client.query_resource(
            self.metrics_uri,
            self.names,
            aggregations=self.aggregations
            )
