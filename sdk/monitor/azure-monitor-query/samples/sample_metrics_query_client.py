# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import urllib3
from azure.monitor.query import MetricsClient
from azure.identity import ClientSecretCredential

urllib3.disable_warnings()

credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = MetricsClient(credential)

# metrics_uri = os.environ['METRICS_RESOURCE_URI']
metrics_uri = "/subscriptions/faa080af-c1d8-40ad-9cce-e1a450ca5b57/resourceGroups/sabhyrav-resourcegroup/providers/Microsoft.EventGrid/topics/rakshith-cloud"
response = client.query(
    metrics_uri,
    metricnames=["PublishSuccessCount"],
    timespan='P2D'
    )

for metric in response.metrics:
    print(metric.name)
    for time_series_element in metric.timeseries:
        for metric_value in time_series_element.data:
            print(metric_value.time_stamp)
    
