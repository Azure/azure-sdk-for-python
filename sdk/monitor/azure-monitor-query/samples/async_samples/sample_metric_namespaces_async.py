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

    metrics_uri = os.environ['METRICS_RESOURCE_URI']
    response = client.list_metric_namespaces(metrics_uri)

    async for item in response:
        print(item.metric_namespace_name)
        print(item.type)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(list_namespaces())
