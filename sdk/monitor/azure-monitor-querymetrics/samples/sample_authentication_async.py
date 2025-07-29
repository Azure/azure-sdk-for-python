# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_authentication_async.py
DESCRIPTION:
    This sample demonstrates how to authenticate to the Azure Monitor service using MetricsClient.
USAGE:
    python sample_authentication_async.py

This example uses DefaultAzureCredential, which requests a token from Microsoft Entra ID.
For more information on DefaultAzureCredential, see https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""
import asyncio


async def create_metrics_client_async():
    # [START create_metrics_client_async]
    from azure.identity.aio import DefaultAzureCredential
    from azure.monitor.querymetrics.aio import MetricsClient

    credential = DefaultAzureCredential()
    client = MetricsClient("https://eastus.metrics.monitor.azure.com", credential)
    # [END create_metrics_client_async]


async def create_metrics_client_sovereign_cloud_async():
    # [START create_metrics_client_sovereign_cloud_async]
    from azure.identity import AzureAuthorityHosts
    from azure.identity.aio import DefaultAzureCredential
    from azure.monitor.querymetrics.aio import MetricsClient

    credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
    client = MetricsClient(
        "https://usgovvirginia.metrics.monitor.azure.us",
        credential,
        audience="https://metrics.monitor.azure.us",
    )
    # [END create_metrics_client_sovereign_cloud_async]


async def main():
    await create_metrics_client_async()
    await create_metrics_client_sovereign_cloud_async()


if __name__ == "__main__":
    asyncio.run(main())
