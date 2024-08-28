# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_authentication.py
DESCRIPTION:
    This sample demonstrates how to authenticate to the Azure Monitor service using both
    LogQueryClient and MetricsQueryClient.
USAGE:
    python sample_authentication.py

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""


def create_logs_query_client():
    # [START create_logs_query_client]
    from azure.identity import DefaultAzureCredential
    from azure.monitor.query import LogsQueryClient

    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential)
    # [END create_logs_query_client]


def create_logs_query_client_sovereign_cloud():
    # [START create_logs_query_client_sovereign_cloud]
    from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
    from azure.monitor.query import LogsQueryClient

    credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
    client = LogsQueryClient(credential, endpoint="https://api.loganalytics.us/v1")
    # [END create_logs_query_client_sovereign_cloud]


def create_metrics_query_client():
    # [START create_metrics_query_client]
    from azure.identity import DefaultAzureCredential
    from azure.monitor.query import MetricsQueryClient

    credential = DefaultAzureCredential()
    client = MetricsQueryClient(credential)
    # [END create_metrics_query_client]


def create_metrics_query_client_sovereign_cloud():
    # [START create_metrics_query_client_sovereign_cloud]
    from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
    from azure.monitor.query import MetricsQueryClient

    credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
    client = MetricsQueryClient(credential, endpoint="https://management.usgovcloudapi.net")
    # [END create_metrics_query_client_sovereign_cloud]


def create_metrics_client():
    # [START create_metrics_client]
    from azure.identity import DefaultAzureCredential
    from azure.monitor.query import MetricsClient

    credential = DefaultAzureCredential()
    client = MetricsClient("https://eastus.metrics.monitor.azure.com", credential)
    # [END create_metrics_client]


def create_metrics_client_sovereign_cloud():
    # [START create_metrics_client_sovereign_cloud]
    from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
    from azure.monitor.query import MetricsClient

    credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
    client = MetricsClient(
        "https://usgovvirginia.metrics.monitor.azure.us",
        credential,
        audience="https://metrics.monitor.azure.us",
    )
    # [END create_metrics_client_sovereign_cloud]


if __name__ == '__main__':
    create_logs_query_client()
    create_logs_query_client_sovereign_cloud()
    create_metrics_query_client()
    create_metrics_query_client_sovereign_cloud()
    create_metrics_client()
    create_metrics_client_sovereign_cloud()
