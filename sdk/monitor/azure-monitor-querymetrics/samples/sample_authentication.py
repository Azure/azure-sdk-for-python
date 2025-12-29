# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_authentication.py
DESCRIPTION:
    This sample demonstrates how to authenticate to the Azure Monitor service using MetricsClient.
USAGE:
    python sample_authentication.py

This example uses DefaultAzureCredential, which requests a token from Microsoft Entra ID.
For more information on DefaultAzureCredential, see https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""


def create_metrics_client():
    # [START create_metrics_client]
    from azure.identity import DefaultAzureCredential
    from azure.monitor.querymetrics import MetricsClient

    credential = DefaultAzureCredential()
    client = MetricsClient("https://eastus.metrics.monitor.azure.com", credential)
    # [END create_metrics_client]


def create_metrics_client_sovereign_cloud():
    # [START create_metrics_client_sovereign_cloud]
    from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
    from azure.monitor.querymetrics import MetricsClient

    credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
    client = MetricsClient(
        "https://usgovvirginia.metrics.monitor.azure.us",
        credential,
        audience="https://metrics.monitor.azure.us",
    )
    # [END create_metrics_client_sovereign_cloud]


if __name__ == "__main__":
    create_metrics_client()
    create_metrics_client_sovereign_cloud()
