# pylint: disable=line-too-long,useless-suppression
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_authentication.py
DESCRIPTION:
    This sample demonstrates how to authenticate to the Azure Monitor service using LogsQueryClient.
USAGE:
    python sample_authentication.py

This example uses DefaultAzureCredential, which requests a token from Microsoft Entra ID.
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


if __name__ == "__main__":
    create_logs_query_client()
    create_logs_query_client_sovereign_cloud()
