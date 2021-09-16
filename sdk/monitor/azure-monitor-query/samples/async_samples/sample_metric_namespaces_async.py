# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import asyncio
from azure.monitor.query.aio import MetricsQueryClient
from azure.identity.aio import DefaultAzureCredential

class ListNameSpaces():
    async def list_namespaces(self):
        credential  = DefaultAzureCredential()

        client = MetricsQueryClient(credential)

        metrics_uri = os.environ['METRICS_RESOURCE_URI']
        async with client:
            response = client.list_metric_namespaces(metrics_uri)
            async for item in response:
                print(item.fully_qualified_namespace)
                print(item.type)

async def main():
    sample = ListNameSpaces()
    await sample.list_namespaces()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
