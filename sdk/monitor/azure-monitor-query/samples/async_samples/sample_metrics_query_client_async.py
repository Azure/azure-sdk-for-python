# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import asyncio
from datetime import datetime, timedelta
from azure.monitor.query.aio import MetricsQueryClient
from azure.monitor.query import MetricAggregationType
from azure.identity.aio import DefaultAzureCredential

async def query_metrics():
    credential  = DefaultAzureCredential(

        )

    client = MetricsQueryClient(credential)

    metrics_uri = os.environ['METRICS_RESOURCE_URI']
    async with client:
        response = await client.query(
            metrics_uri,
            metric_names=["Ingress"],
            timespan=timedelta(hours=2),
            granularity=timedelta(minutes=15),
            aggregations=[MetricAggregationType.AVERAGE],
            )

    for metric in response.metrics:
        print(metric.name)
        for time_series_element in metric.timeseries:
            for metric_value in time_series_element.data:
                print(metric_value.timestamp)
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(query_metrics())
