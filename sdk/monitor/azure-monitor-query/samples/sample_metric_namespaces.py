# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from azure.monitor.query import MetricsQueryClient
from azure.identity import DefaultAzureCredential

credential  = DefaultAzureCredential()

client = MetricsQueryClient(credential)

metrics_uri = '/subscriptions/faa080af-c1d8-40ad-9cce-e1a450ca5b57/resourceGroups/sabhyrav-resourcegroup/providers/Microsoft.EventGrid/topics/rakshith-cloud'
response = client.list_metric_namespaces(metrics_uri)

for item in response:
    print(item.fully_qualified_namespace)
    print(item.type)
