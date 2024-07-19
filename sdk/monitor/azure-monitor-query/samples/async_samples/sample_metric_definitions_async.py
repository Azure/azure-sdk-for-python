# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_metric_definitions_async.py
DESCRIPTION:
    This sample demonstrates listing all the metric definitions of a resource.
USAGE:
    python sample_metric_definitions_async.py
    Set the environment variables with your own values before running the sample:
    1) METRICS_RESOURCE_URI - The resource URI of the resource for which the metrics are being queried.

    This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
    For more information on DefaultAzureCredential, see https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.

    In this example, an Event Grid account resource URI is taken.
"""
import asyncio

# [START send_metric_definitions_query_async]
import os

from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.query.aio import MetricsQueryClient


async def list_definitions():
    credential = DefaultAzureCredential()
    client = MetricsQueryClient(credential)

    metrics_uri = os.environ["METRICS_RESOURCE_URI"]
    async with client:
        try:
            response = client.list_metric_definitions(metrics_uri)
            async for item in response:
                print(item.name)
                if item.metric_availabilities:
                    for availability in item.metric_availabilities:
                        print(availability.granularity)
        except HttpResponseError as err:
            print("something fatal happened")
            print(err)
    await credential.close()

# [END send_metric_definitions_query_async]

if __name__ == "__main__":
    asyncio.run(list_definitions())
