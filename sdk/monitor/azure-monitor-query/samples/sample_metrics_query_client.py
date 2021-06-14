# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from datetime import datetime
import urllib3
from azure.monitor.query import MetricsQueryClient
from azure.identity import ClientSecretCredential

urllib3.disable_warnings()

# [START metrics_client_auth_with_token_cred]
credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = MetricsQueryClient(credential)
# [END metrics_client_auth_with_token_cred]

# [START send_metrics_query]
metrics_uri = os.environ['METRICS_RESOURCE_URI']
response = client.query(
    metrics_uri,
    metric_names=["PublishSuccessCount"],
    start_time=datetime(2021, 5, 25),
    duration='P1D'
    )

for metric in response.metrics:
    print(metric.name)
    for time_series_element in metric.timeseries:
        for metric_value in time_series_element.data:
            print(metric_value.time_stamp)
# [END send_metrics_query]
