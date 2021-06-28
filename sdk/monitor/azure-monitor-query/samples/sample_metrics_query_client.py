# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from datetime import datetime, timedelta
import urllib3
from azure.monitor.query import MetricsQueryClient
from azure.identity import DefaultAzureCredential

urllib3.disable_warnings()

# [START metrics_client_auth_with_token_cred]
credential  = DefaultAzureCredential()

client = MetricsQueryClient(credential)
# [END metrics_client_auth_with_token_cred]

# [START send_metrics_query]
metrics_uri = os.environ['METRICS_RESOURCE_URI']
response = client.query(
    metrics_uri,
    metric_names=["MatchedEventCount"],
    start_time=datetime(2021, 6, 21),
    duration=timedelta(days=1),
    aggregation=['Count']
    )

for metric in response.metrics:
    print(metric.name)
    for time_series_element in metric.timeseries:
        for metric_value in time_series_element.data:
            if metric_value.count != 0:
                print(
                    "There are {} matched events at {}".format(
                        metric_value.count,
                        metric_value.time_stamp
                    )
                )
# [END send_metrics_query]
