# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Code snippets demonstrating how to create various clients."""


def create_logs_query_client():
    # [START create_logs_query_client]
    from azure.identity import DefaultAzureCredential
    from azure.monitor.query import LogsQueryClient

    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential)
    # [END create_logs_query_client]


def create_logs_query_client_async():
    # [START create_logs_query_client_async]
    from azure.identity.aio import DefaultAzureCredential
    from azure.monitor.query.aio import LogsQueryClient

    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential)
    # [END create_logs_query_client_async]


def create_metrics_query_client():
    # [START create_metrics_query_client]
    from azure.identity import DefaultAzureCredential
    from azure.monitor.query import MetricsQueryClient

    credential = DefaultAzureCredential()
    client = MetricsQueryClient(credential)
    # [END create_metrics_query_client]


def create_metrics_query_client_async():
    # [START create_metrics_query_client_async]
    from azure.identity.aio import DefaultAzureCredential
    from azure.monitor.query.aio import MetricsQueryClient

    credential = DefaultAzureCredential()
    client = MetricsQueryClient(credential)
    # [END create_metrics_query_client_async]
