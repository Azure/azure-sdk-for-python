# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_metric_namespaces.py
DESCRIPTION:
    This sample demonstrates listing all the metric namespaces of a resource.
USAGE:
    python sample_metric_namespaces.py
    Set the environment variables with your own values before running the sample:
    1) METRICS_RESOURCE_ID - The resource ID/URI of the resource for which the metrics are being queried.

    This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
    For more information on DefaultAzureCredential, see https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""
# [START send_metric_namespaces_query]
import os

from azure.identity import DefaultAzureCredential
from azure.monitor.query import MetricsQueryClient


credential = DefaultAzureCredential()
client = MetricsQueryClient(credential)

resource_id = os.environ["METRICS_RESOURCE_ID"]
response = client.list_metric_namespaces(resource_id)

for item in response:
    print(item.fully_qualified_namespace)
    print(item.type)

# [END send_metric_namespaces_query]
