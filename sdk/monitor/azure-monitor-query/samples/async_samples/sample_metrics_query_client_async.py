# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import asyncio
from datetime import datetime, timedelta
import urllib3
from azure.monitor.query.aio import MetricsQueryClient
from azure.identity.aio import DefaultAzureCredential

urllib3.disable_warnings()

async def query_metrics():
    credential  = DefaultAzureCredential(
            client_id = os.environ['AZURE_CLIENT_ID'],
            client_secret = os.environ['AZURE_CLIENT_SECRET'],
            tenant_id = os.environ['AZURE_TENANT_ID']
        )

    client = MetricsQueryClient(credential)

    metrics_uri = os.environ['METRICS_RESOURCE_URI']
    async with client:
        response = await client.query(
            metrics_uri,
            metric_names=["PublishSuccessCount"],
            start_time=datetime(2021, 5, 25),
            duration=timedelta(days=1)
            )

    for metric in response.metrics:
        print(metric.name)
        for time_series_element in metric.timeseries:
            for metric_value in time_series_element.data:
                print(metric_value.time_stamp)
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(query_metrics())
