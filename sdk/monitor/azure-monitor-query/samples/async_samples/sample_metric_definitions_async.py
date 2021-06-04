# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import asyncio
from azure.monitor.query.aio import MetricsQueryClient
from azure.identity.aio import ClientSecretCredential

async def list_namespaces():
    credential  = ClientSecretCredential(
            client_id = os.environ['AZURE_CLIENT_ID'],
            client_secret = os.environ['AZURE_CLIENT_SECRET'],
            tenant_id = os.environ['AZURE_TENANT_ID']
        )

    client = MetricsQueryClient(credential)

    metrics_uri = "/subscriptions/faa080af-c1d8-40ad-9cce-e1a450ca5b57/resourceGroups/sabhyrav-resourcegroup/providers/Microsoft.EventGrid/topics/rakshith-cloud"
    response = client.list_metric_definitions(metrics_uri)

    async for item in response:
        print(item)
        for availability in item.metric_availabilities:
            print(availability.time_grain)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(list_namespaces())
