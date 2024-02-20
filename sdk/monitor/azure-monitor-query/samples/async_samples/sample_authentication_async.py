# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_authentication_async.py
DESCRIPTION:
    This sample demonstrates how to authenticate to the Azure Monitor service using both
    LogQueryClient and MetricsQueryClient.
USAGE:
    python sample_authentication_async.py

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""
import asyncio


async def create_logs_query_client_async():
    # [START create_logs_query_client_async]
    from azure.identity.aio import DefaultAzureCredential
    from azure.monitor.query.aio import LogsQueryClient

    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential)
    # [END create_logs_query_client_async]


async def create_metrics_query_client_async():
    # [START create_metrics_query_client_async]
    from azure.identity.aio import DefaultAzureCredential
    from azure.monitor.query.aio import MetricsQueryClient

    credential = DefaultAzureCredential()
    client = MetricsQueryClient(credential)
    # [END create_metrics_query_client_async]


async def main():
    await create_logs_query_client_async()
    await create_metrics_query_client_async()


if __name__ == '__main__':
    asyncio.run(main())
