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


def create_metrics_query_client():
    # [START create_metrics_query_client]
    from azure.identity import DefaultAzureCredential
    from azure.monitor.query import MetricsQueryClient

    credential = DefaultAzureCredential()
    client = MetricsQueryClient(credential)
    # [END create_metrics_query_client]


if __name__ == '__main__':
    create_logs_query_client()
    create_metrics_query_client()
