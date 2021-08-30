# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from datetime import datetime, timedelta
import urllib3
from azure.monitor.query import MetricsQueryClient, MetricAggregationType
from azure.identity import DefaultAzureCredential

# urllib3.disable_warnings()

# [START metrics_client_auth_with_token_cred]
credential  = DefaultAzureCredential()

client = MetricsQueryClient(credential)
# [END metrics_client_auth_with_token_cred]

# [START send_metrics_query]
metrics_uri = os.environ['METRICS_RESOURCE_URI']
response = client.query(
    metrics_uri,
    metric_names=["Ingress"],
    timespan=timedelta(hours=2),
    granularity=timedelta(minutes=5),
    aggregations=[MetricAggregationType.AVERAGE],
    )

for metric in response.metrics:
    print(metric.name + ' -- ' + metric.display_description)
    for time_series_element in metric.timeseries:
        for metric_value in time_series_element.data:
            print('The ingress at {} is {}'.format(
                metric_value.timestamp,
                metric_value.average
            ))
# [END send_metrics_query]
