# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import asyncio
from azure.monitor.query.aio import MetricsQueryClient
from azure.identity.aio import DefaultAzureCredential

class ListDefinitions():
    async def list_definitions(self):
        credential  = DefaultAzureCredential()

        client = MetricsQueryClient(credential)

        metrics_uri = os.environ['METRICS_RESOURCE_URI']
        async with client:
            response = client.list_metric_definitions(metrics_uri)

            async for item in response:
                print(item.namespace)
                for availability in item.metric_availabilities:
                    print(availability.granularity)

async def main():
    sample = ListDefinitions()
    await sample.list_definitions()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
