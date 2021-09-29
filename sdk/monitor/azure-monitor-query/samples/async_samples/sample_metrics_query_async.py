# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_metrics_query_async.py
DESCRIPTION:
    This sample demonstrates authenticating the LogsQueryClient and querying a single query
    on multiple workspaces using the additional_workspaces param.
USAGE:
    python sample_metrics_query_async.py
    Set the environment variables with your own values before running the sample:
    1) METRICS_RESOURCE_URI - The resource uri of the resource for which the metrics are being queried.
    In this example, a storage account resource URI is taken.

    In order to use the DefaultAzureCredential, the following environment variables must be set:
    1) AZURE_CLIENT_ID - The client ID of a user-assigned managed identity.
    2) AZURE_TENANT_ID - Tenant ID to use when authenticating a user.
    3) AZURE_CLIENT_ID - The client secret to be used for authentication.
"""
import os
import asyncio
from datetime import timedelta
from azure.monitor.query.aio import MetricsQueryClient
from azure.monitor.query import MetricAggregationType
from azure.identity.aio import DefaultAzureCredential

async def query_metrics():
    credential  = DefaultAzureCredential()

    client = MetricsQueryClient(credential)

    metrics_uri = os.environ['METRICS_RESOURCE_URI']
    async with client:
        response = await client.query_resource(
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
