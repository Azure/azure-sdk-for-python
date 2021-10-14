# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_metric_definitions_async.py
DESCRIPTION:
    This sample demonstrates listing all the metric definitions of a resource.
USAGE:
    python sample_metric_definitions_async.py
    Set the environment variables with your own values before running the sample:
    1) METRICS_RESOURCE_URI - The resource uri of the resource for which the metrics are being queried.
    In this example, an eventgrid account resource URI is taken.

    In order to use the DefaultAzureCredential, the following environment variables must be set:
    1) AZURE_CLIENT_ID - The client ID of a user-assigned managed identity.
    2) AZURE_TENANT_ID - Tenant ID to use when authenticating a user.
    3) AZURE_CLIENT_ID - The client secret to be used for authentication.
"""
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
                print(item.name)
                for availability in item.metric_availabilities:
                    print(availability.granularity)

async def main():
    sample = ListDefinitions()
    await sample.list_definitions()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
